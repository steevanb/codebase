#!/usr/bin/env python3

"""Build the pages of docs/ from the settings files of config/releases/, written by /app:release:update.

config/releases/
├── <vendor>/vendor.json                    name, language and description of the vendor
└── <vendor>/<package>/
    ├── package.json                        name, type, repository and history (repository of the commits) of the package
    └── <version>.json                      a minor version: release, maintenance, sources and changes

Builds (and overwrites):
- docs/releases/index.html                              list of the vendors
- docs/releases/<vendor>/index.html                     list of the packages of the vendor
- docs/releases/<vendor>/<package>/index.html           versions of the package, by major version
- docs/releases/<vendor>/<package>/<version>/index.html release page of each version
- the "Latest releases" and "Projects" lists of docs/index.html

Example pages (docs/releases/<vendor>/<package>/<version>/<slug>/) are written by hand: they are never touched.
Only uses the standard library: runs without Docker.

Usage: bin/dev/site.py
"""

import html
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / 'config' / 'releases'
DOCS_DIR = ROOT_DIR / 'docs'
TODAY = date.today().isoformat()

SECTIONS = [
    ('bc-breaks', 'tone-rose', 'BC <em>breaks</em>.'),
    ('new-features', 'tone-emerald', 'New <em>features</em>.'),
    ('improvements', 'tone-indigo', '<em>Improvements</em>.'),
    ('dependencies', 'tone-violet', '<em>Dependencies</em>.'),
    ('other', 'tone-slate', '<em>Other</em> changes.'),
]

ICON_EXAMPLE = '<svg class="icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M5.5 4 1.5 8l4 4M10.5 4l4 4-4 4"/></svg>'
ICON_COMMIT = '<svg class="icon" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="2.75"/><path d="M1 8h4.25M10.75 8H15"/></svg>'
ICON_PR = '<svg class="icon" viewBox="0 0 16 16" aria-hidden="true"><circle cx="4" cy="3.5" r="1.75"/><circle cx="4" cy="12.5" r="1.75"/><circle cx="12" cy="12.5" r="1.75"/><path d="M4 5.25v5.5M12 10.75V6.5a2 2 0 0 0-2-2H7.5M9 3l-1.5 1.5L9 6"/></svg>'

def escape(text: str) -> str:
    return html.escape(text, quote=False)

def markdown(text: str) -> str:
    """Code between backticks becomes <code>, everything else is escaped."""
    parts = text.split('`')

    return ''.join(f'<code>{escape(part)}</code>' if i % 2 else escape(part) for i, part in enumerate(parts))

def version_key(version: str) -> tuple:
    return tuple(int(part) for part in version.split('.'))

def read_json(path: Path) -> dict:
    return json.loads(path.read_text())

def head(title: str, description: str, path: str) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} · codebase.watch</title>
    <meta name="description" content="{html.escape(description)}">
    <link rel="canonical" href="https://codebase.watch{path}">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="/assets/css/main.css">
</head>
<body>
    <header class="masthead">
        <div class="masthead-inner">
            <a class="brand" href="/">
                <span class="brand-glyph" aria-hidden="true">&lt;/&gt;</span>
                <span class="brand-wordmark">
                    <span class="brand-name">codebase<span>.watch</span></span>
                    <span class="brand-sub">what is new in your dependencies</span>
                </span>
            </a>
            <input class="nav-toggle" id="nav-toggle" type="checkbox" aria-label="Menu">
            <label class="nav-burger burger" for="nav-toggle" aria-hidden="true"><span></span></label>
            <nav class="nav">
                <a class="nav-link" href="/">Home</a>
                <a class="nav-link nav-link-active" href="/releases/"{' aria-current="page"' if path == '/releases/' else ''}>Releases</a>
            </nav>
        </div>
    </header>
    <div class="container">
'''

def breadcrumb(*levels: str) -> str:
    """Each level but the last one links to its page: ('releases', 'symfony', 'options-resolver')."""
    lines = ['        <nav class="breadcrumb">', '            <a href="/">codebase.watch</a> /']
    path = '/'
    for level in levels[:-1]:
        path += f'{level}/'
        lines.append(f'            <a href="{path}">{level}</a> /')
    lines.append(f'            {levels[-1]}')
    lines.append('        </nav>')

    return '\n'.join(lines) + '\n'

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text() != content:
        path.write_text(content)
        print(f'Built {path.relative_to(ROOT_DIR)}')

def badge(text: str, tone: str) -> str:
    return f'<span class="badge tone-{tone}">{text}</span>'

def released_badge(day: str) -> str:
    return badge(f'Released <time datetime="{day}">{day}</time>', 'blue')

def is_maintained(until: str) -> bool:
    return until > TODAY[:7]

class Package:
    def __init__(self, vendor: 'Vendor', directory: Path):
        self.vendor = vendor
        self.slug = directory.name
        self.settings = read_json(directory / 'package.json')
        self.name = self.settings['name']
        self.url = f'/releases/{vendor.slug}/{self.slug}/'
        self.versions = sorted(
            (Version(self, path) for path in directory.glob('*.json') if path.name != 'package.json'),
            key=lambda version: version_key(version.number),
            reverse=True,
        )

class Version:
    def __init__(self, package: Package, path: Path):
        self.package = package
        self.number = path.stem
        self.settings = read_json(path)
        self.previous = self.settings.get('previous')
        self.release = self.settings['release']
        self.released = 'date' in self.release
        self.maintenance = self.settings['maintenance']
        self.changes = self.settings['changes']
        self.url = f'{package.url}{self.number}/'

    def commits(self) -> set:
        return {commit['hash'] for change in self.changes for commit in change['commits']}

class Vendor:
    def __init__(self, directory: Path):
        self.slug = directory.name
        self.settings = read_json(directory / 'vendor.json')
        self.name = self.settings['name']
        self.url = f'/releases/{self.slug}/'
        self.packages = sorted(
            (Package(self, path) for path in directory.iterdir() if (path / 'package.json').exists()),
            key=lambda package: package.name,
        )

def commit_row(version: Version, change: dict) -> str:
    examples = [page for page in change.get('pages', []) if page['type'] == 'example']
    message = f'<span class="commit-message">{markdown(change["message"])}</span>'
    lines = ['                <li class="commit">']
    if examples:
        lines += [
            f'                    <a class="commit-main" href="{version.url}{examples[0]["slug"]}/">',
            f'                        {message}',
            '                    </a>',
        ]
    else:
        lines += ['                    <div class="commit-main">', f'                        {message}', '                    </div>']

    # Mobile menu of the links: the id is unique per row, a commit being shown once per change
    first = change['commits'][0]['hash'][:10]
    version.rows[first] = version.rows.get(first, 0) + 1
    menu = f'links-{first}-{version.rows[first]}'
    lines += [
        f'                    <input class="commit-toggle" id="{menu}" type="checkbox" aria-label="Links">',
        f'                    <label class="commit-burger burger" for="{menu}" aria-hidden="true"><span></span></label>',
        '                    <div class="commit-links">',
    ]
    for page in examples:
        lines.append(f'                        <a class="icon-link" href="{version.url}{page["slug"]}/" title="Example" aria-label="Example">{ICON_EXAMPLE}<span class="icon-link-label">Example</span></a>')
    for commit in change['commits']:
        title = f'Commit {commit["hash"][:10]}'
        lines.append(f'                        <a class="icon-link" href="{version.package.settings["history"]}/commit/{commit["hash"]}" target="_blank" rel="noopener" title="{title}" aria-label="{title}">{ICON_COMMIT}<span class="icon-link-label">{title}</span></a>')
        if commit.get('pullRequest'):
            title = f'Pull request #{commit["pullRequest"].rsplit("/", 1)[1]}'
            lines.append(f'                        <a class="icon-link" href="{commit["pullRequest"]}" target="_blank" rel="noopener" title="{title}" aria-label="{title}">{ICON_PR}<span class="icon-link-label">{title}</span></a>')
    lines += ['                    </div>', '                </li>']

    return '\n'.join(lines)

def section_note(section: str, version: Version) -> str:
    return {
        'bc-breaks': f'Changes that can break existing code when upgrading from {version.previous}.',
        'new-features': 'New capabilities added by this version.',
        'improvements': 'Enhancements of existing features.',
        'dependencies': f'Changes of the required {version.package.vendor.settings["language"]} version, extensions or packages.',
        'other': 'No impact on your code.',
    }[section]

def stat(label: str, value: str, css_class: str = 'stat') -> str:
    return f'''                <div class="{css_class}">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>'''

def maintenance_stats(version: Version) -> list:
    stats = []
    for label, key, tone in (('Bug fixes', 'bugFixesUntil', 'emerald'), ('Security fixes', 'securityFixesUntil', 'amber')):
        until = version.maintenance[key]
        if is_maintained(until):
            stats.append(stat(label, f'Until {until}', f'stat tone-{tone}'))
        else:
            stats.append(stat(label, f'Ended {until}', 'stat tone-rose'))

    return stats

def favicon(url: str) -> str:
    domain = urlparse(url).hostname
    for extension in ('svg', 'png'):
        if (DOCS_DIR / 'assets' / 'favicons' / f'{domain}.{extension}').exists():
            return f'/assets/favicons/{domain}.{extension}'

    raise SystemExit(f'No favicon for {domain}: add docs/assets/favicons/{domain}.svg (see /app:site:update).')

def release_page(version: Version) -> str:
    package = version.package
    version.rows = {}
    rows = {key: [] for key, _, _ in SECTIONS}
    for change in version.changes:
        if not change.get('hidden', False):
            rows[change['section']].append(commit_row(version, change))
    features = len(rows['new-features']) + len(rows['improvements'])
    ref = version.release['ref']
    package_link = f'<a href="{package.url}">{package.name}</a>'

    if version.previous:
        description = f'New features and improvements of the {package.name} {package.settings["type"]} in version {version.number}, compared to {version.previous}.'
        hero = stat('Compared versions', f'{version.previous} → {version.number}', 'stat stat-hero')
    else:
        description = f'First version of the {package.name} {package.settings["type"]}, created in {version.number}.'
        hero = stat('First version', version.number, 'stat stat-hero')
    if version.released:
        when = stat(f'Released ({ref})', version.release['date'])
    else:
        when = stat('Status', version.release['version'])
    stats = [hero, stat('New features', str(features)), stat('Commits', str(len(version.commits()))), when]
    stats += maintenance_stats(version)
    stats_html = '\n'.join(stats)

    sections = []
    for key, tone, title in SECTIONS:
        if rows[key]:
            sections.append(f'''        <section id="{key}" class="{tone}">
            <h2><span>{title}</span><span class="count">{len(rows[key])}</span></h2>
            <p class="section-note">{section_note(key, version)}</p>
            <ul class="commits">
{chr(10).join(rows[key])}
            </ul>
        </section>
''')
    if not version.commits():
        if version.released:
            empty = f'The <code>{ref}</code> tag contains no commit touching {package_link} that is not already in the <code>{version.previous}</code> branch.'
        else:
            empty = f'The <code>{ref}</code> branch contains no commit touching {package_link} that is not already in <code>{version.previous}</code>.'
        sections.append(f'''        <section id="commits" class="tone-teal">
            <h2><span>The <em>commits</em>.</span></h2>
            <div class="empty">
                <strong>No commit.</strong>
                {empty}
            </div>
        </section>
''')

    sources = '\n'.join(
        f'                <li><a href="{html.escape(source["url"])}" target="_blank" rel="noopener"><img class="favicon" src="{favicon(source["url"])}" alt="" width="16" height="16">{escape(source["title"])}</a></li>'
        for source in version.settings['sources']
    )

    return head(f'{package.name} {version.number}', description, version.url) + breadcrumb(
        'releases', package.vendor.slug, package.slug, version.number
    ) + f'''
        <h1>{package.name} {version.number}</h1>

        <section id="overview" class="tone-amber">
            <h2><span>At a <em>glance</em>.</span></h2>
            <div class="stats">
{stats_html}
            </div>
        </section>

{chr(10).join(sections)}
        <section id="sources">
            <h2><span>The <em>sources</em>.</span></h2>
            <ul class="sources">
{sources}
            </ul>
        </section>

        <footer>
            Last checked on {version.settings["checkedOn"]}.
        </footer>
    </div>
</body>
</html>
'''

def version_badges(version: Version) -> str:
    badges = []
    if version.released:
        bug_fixes = is_maintained(version.maintenance['bugFixesUntil'])
        security_fixes = is_maintained(version.maintenance['securityFixesUntil'])
        if bug_fixes:
            badges.append(badge('Bug fixes', 'emerald'))
        if security_fixes:
            badges.append(badge('Security fixes', 'amber'))
        if not bug_fixes and not security_fixes:
            badges.append(badge('Unmaintained', 'rose'))
    if version.maintenance.get('lts', False):
        badges.append(badge('LTS', 'indigo'))

    return ''.join(badges)

def major_badges(versions: list) -> str:
    released = [version for version in versions if version.released]
    bug_fixes = any(is_maintained(version.maintenance['bugFixesUntil']) for version in released)
    security_fixes = any(is_maintained(version.maintenance['securityFixesUntil']) for version in released)
    badges = []
    if released and not bug_fixes and not security_fixes:
        badges.append(badge('Unmaintained', 'rose'))
    if released:
        badges.append(released_badge(released[-1].release['date']))
    else:
        badges.append(badge('In development', 'violet'))
    if bug_fixes:
        badges.append(badge('Bug fixes', 'emerald'))
    if security_fixes:
        badges.append(badge('Security fixes', 'amber'))
    badges += [badge(f'LTS {version.number}', 'indigo') for version in versions if version.maintenance.get('lts', False)]

    return ''.join(badges)

def package_page(package: Package) -> str:
    majors = {}
    for version in package.versions:
        majors.setdefault(version.number.split('.')[0], []).append(version)

    sections = []
    for major, versions in majors.items():
        tiles = []
        for version in versions:
            status = released_badge(version.release['date']) if version.released else badge('In development', 'violet')
            tiles.append(f'''                <li>
                    <a class="stat stat-hero" href="{version.url}">
                        <span class="stat-label">{status}</span>
                        <span class="stat-value">{version.number}</span>
                        <span class="badges">{version_badges(version)}</span>
                    </a>
                </li>''')
        sections.append(f'''        <section id="version-{major}">
            <h2><span>Version <em>{major}.x</em></span><span class="badges">{major_badges(versions)}</span></h2>
            <ul class="stats stats-versions">
{chr(10).join(tiles)}
            </ul>
        </section>
''')

    kind = package.settings['type']
    repository = f'<a href="{package.settings["repository"]}" target="_blank" rel="noopener">{package.name}</a>'

    return head(f'{package.name} releases', f'What is new in each release of the {package.name} {kind}.', package.url) + breadcrumb(
        'releases', package.vendor.slug, package.slug
    ) + f'''
        <h1>{package.name}</h1>
        <p class="subtitle">What is new in each release of the {repository} {kind}.</p>

{chr(10).join(sections)}    </div>
</body>
</html>
'''

def list_item(url: str, title: str, description: str, indent: str = '                ') -> str:
    return f'''{indent}<li>
{indent}    <a href="{url}">
{indent}        <div class="list-title">{title}</div>
{indent}        <div class="list-description">{description}</div>
{indent}    </a>
{indent}</li>'''

def vendor_page(vendor: Vendor) -> str:
    items = '\n'.join(list_item(package.url, package.name, package.settings['type'].capitalize()) for package in vendor.packages)

    return head(f'{vendor.name} releases', vendor.settings['subtitle'], vendor.url) + breadcrumb('releases', vendor.slug) + f'''
        <h1>{vendor.name}</h1>
        <p class="subtitle">{vendor.settings["subtitle"]}</p>

        <ul class="list">
{items}
        </ul>
    </div>
</body>
</html>
'''

def vendor_item(vendor: Vendor, indent: str = '                ') -> str:
    return list_item(vendor.url, vendor.name, f'{vendor.settings["language"]} · {vendor.settings["description"]}', indent)

def releases_page(vendors: list) -> str:
    items = '\n'.join(vendor_item(vendor) for vendor in vendors)

    return head('Releases', 'What is new in each release, by project.', '/releases/') + breadcrumb('releases') + f'''
        <h1>Releases</h1>
        <p class="subtitle">What is new in each release, by project.</p>

        <ul class="list">
{items}
        </ul>
    </div>
</body>
</html>
'''

def home_page(vendors: list) -> str:
    """Only the lists of the "latest" and "projects" sections of the home page are built."""
    content = (DOCS_DIR / 'index.html').read_text()
    latest = []
    for vendor in vendors:
        for package in vendor.packages:
            version = package.versions[0]
            title = f'{package.name} {version.number}'
            if not version.released:
                title += ' <span class="badge">In development</span>'
            description = f'{vendor.settings["language"]} · Compared to {version.previous}' if version.previous else vendor.settings['language']
            latest.append(list_item(version.url, title, description))
    projects = [vendor_item(vendor) for vendor in vendors]
    for section, items in (('latest', latest), ('projects', projects)):
        content = re.sub(
            rf'(<section id="{section}".*?<ul class="list">\n).*?(\n            </ul>)',
            lambda match: match.group(1) + '\n'.join(items) + match.group(2),
            content,
            count=1,
            flags=re.DOTALL,
        )

    return content

def main():
    vendors = sorted((Vendor(path) for path in CONFIG_DIR.iterdir() if (path / 'vendor.json').exists()), key=lambda vendor: vendor.name)
    write(DOCS_DIR / 'index.html', home_page(vendors))
    write(DOCS_DIR / 'releases' / 'index.html', releases_page(vendors))
    for vendor in vendors:
        write(DOCS_DIR / 'releases' / vendor.slug / 'index.html', vendor_page(vendor))
        for package in vendor.packages:
            write(DOCS_DIR / 'releases' / vendor.slug / package.slug / 'index.html', package_page(package))
            for version in package.versions:
                write(DOCS_DIR / 'releases' / vendor.slug / package.slug / version.number / 'index.html', release_page(version))

if __name__ == '__main__':
    main()
