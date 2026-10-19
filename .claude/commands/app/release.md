---
description: Create or update the codebase.watch page listing what is new in a release
argument-hint: <language> <repository> <version>   (e.g. php symfony/options-resolver 8.0)
---

# Create a release page

Create (or update) the page that lists the new features and improvements of one version of one repository,
compared to the previous version.

## Parameters

Arguments given: `$ARGUMENTS`

They are, in this order:

1. **Language**: e.g. `php`
2. **Repository**: e.g. `symfony/options-resolver`, in the `<vendor>/<package>` form of GitHub
3. **Version**: e.g. `8.0`, always a minor version `X.Y`

If a parameter is missing, ask for it with the `AskUserQuestion` tool before doing anything else.
Ask for all the missing parameters in a single call.

## Project knowledge

This command is common to every language and every project. What is specific comes from two skills,
to load with the `Skill` tool before anything else:

- **The skill of the language**, named after it (e.g. `php`): package names, where the dependencies are declared,
  how deprecations and BC breaks look, how to write and color code in the pages.
- **The skill of the vendor**, named after the vendor of the repository (e.g. `symfony` for `symfony/options-resolver`):
  - which repository holds the history (e.g. a monorepo) and the directory of the package in it,
  - how versions, branches and tags work, and what the previous version of a version is,
  - where to find the changelog, the documentation and the articles (blog...) about a change,
  - how to classify the commits (commit message conventions...),
  - how to name the project and the package in the pages.

If one of them does not exist, find the answers (in the repository for a vendor: README, CONTRIBUTING, branches, tags,
changelog), ask the user what you cannot find, then create the skill in `.claude/skills/<name>/SKILL.md`
with the same sections as the `php` or `symfony` skill, so the next run does not have to look again.

## Site architecture

The site is hosted on GitHub Pages from the `docs/` directory of the `master` branch,
with the custom domain `codebase.watch`.

```
docs/
├── CNAME                   codebase.watch
├── .nojekyll               files are served as is
├── 404.html
├── index.html              home page
├── favicon.svg             icon of every page
├── assets/css/main.css     styles shared by every page
├── assets/fonts/           Poppins and JetBrains Mono, self-hosted
├── assets/favicons/        favicons of the sites we link to, named <domain>.svg (or .png)
└── releases/
    ├── index.html                              list of vendors, with their language
    └── <vendor>/
        ├── index.html                          list of packages
        └── <package>/
            ├── index.html                      list of versions, newest first
            └── <version>/index.html            the release page
```

- One URL = one directory containing an `index.html`: `https://codebase.watch/releases/<vendor>/<package>/<version>/`.
  The language is not in the URL: `<vendor>/<package>` is the repository on GitHub, unique whatever its language.
- Links are absolute from the site root (`/releases/<vendor>/`, `/assets/css/main.css`), never relative.
  The site cannot be browsed through `file://`: run `bin/dev/start.py` (http://localhost:25100, served in the
  background by the `codebase-server` container), stop it with `bin/dev/stop.py`.
- Links to another site (GitHub, documentation, blog posts...) open in a new tab: `target="_blank" rel="noopener"`.
  Links inside the site do not.
- Name what the text is about: the package when it is about the package, the project only when it is about the whole
  project, which should be rare. The vendor skill gives the names and examples.
  Quoted texts (commit messages, deprecation messages) are left as they are.
- A message read in the code (deprecation, exception, error...) is copied exactly as the code produces it:
  same words, same punctuation, on a single line if it is a single line, never wrapped nor reformatted.
  Only the placeholders are replaced by their values (e.g. `%s` by the method name), as the code does.
- Every time the name of a package is written, it links to our site: to the page of the version it talks about
  (`/releases/<vendor>/<package>/<version>/`), or to the page of the package (`/releases/<vendor>/<package>/`)
  when it talks about no version or we have no page for this version. Never link to GitHub nor to another site
  from the name of a package. Exceptions: titles (`<title>`, `h1`, `h2`, breadcrumb, `list-title`), quoted texts
  (commit and deprecation messages), and texts that are already a link (e.g. the links of `Sources`).
- Only the page of a package links its name to its repository on GitHub, in its subtitle:
  `What is new in each release of the <a href="https://github.com/<repository>" target="_blank" rel="noopener"><package></a> <component, package...>.`
  Never link a page to itself.
- Every page is written in English, and uses only `/assets/css/main.css`: no inline style, no external dependency.
  Add the classes a page needs to `main.css` instead of duplicating styles.
- The links of a `Sources` section are sorted in this order: commits (and the comparison on GitHub), pull requests,
  documentation of the project, blog of the project, then the rest (changelog, other articles...).
- Every link of a `Sources` section starts with the favicon of the site it points to, inside the link:
  `<a href="https://github.com/..." target="_blank" rel="noopener"><img class="favicon" src="/assets/favicons/github.com.svg" alt="" width="16" height="16">...</a>`.
  When `docs/assets/favicons/<domain>.svg` does not exist, download the icon declared by the home page of the site
  (`<link rel="icon">`, SVG preferred), check that it contains no script, and make it visible in dark mode
  (a `prefers-color-scheme: dark` style in the SVG) if it is dark.
- Every page links `/favicon.svg` in its `<head>`, before `main.css`.
- Every page starts with the `masthead` header (logo and navigation), copied from the reference page:
  the `Releases` link has `nav-link-active` on every page under `/releases/`.
- Every page has a breadcrumb linking each level: `codebase.watch / releases / <vendor> / <package> / <version>`.

## Reference page

Use `docs/releases/symfony/options-resolver/8.0/index.html` as the template: same structure, same classes.

Every `section` is a card, in the style of gitstatshub.com:

- Its title is `<h2><span>...</span></h2>`, with one key word in `<em>` (shown with a gradient) and a final period,
  e.g. `<h2><span>New <em>features</em> and improvements.</span></h2>`. The `<span>` is required.
  The chapter number (`I`, `II`...) is added by the CSS: never write it.
- Its background color is given by a `tone-<color>` class: `indigo`, `emerald`, `amber`, `rose`, `blue`, `orange`, `violet`, `teal`, `slate`.
  Each section of a page has its own color, except `The sources.`, always white (no class).
  Use the tones of the reference pages for the same sections.

1. Masthead header, then breadcrumb.
2. Title as given by the vendor skill (e.g. `<Project> <Package> <version>`), without badge nor subtitle.
3. Section `At a glance.` (`tone-amber`), holding the stats, each one with its label first, then its value,
   the first one being `stat-hero`: compared versions (`7.4 → 8.0`), number of new features and improvements,
   number of commits (hidden ones included), date of the first release of the version (or the current version, e.g. `8.2.0-DEV`,
   when in development). After the stats, a `section-note` telling which commits are listed:
   `Commits of <code><tag or branch></code> touching <a href="/releases/<vendor>/<package>/"><package></a> that are not in the <code><previous branch></code> branch.`
4. The changes of the commits, shown by type: one section per type, in this order. Each type is a `section` value of
   the `changes` of the settings file (see [Commit settings](#commit-settings)), used as the `id` of its section.
   A commit that does several things has several changes, so it can be shown several times, with a different label,
   in the same type or in different ones:
   - `bc-breaks`, title `BC <em>breaks</em>.`, `tone-rose`: changes that can break existing code when upgrading
     (removed features or BC layers, changed signatures or behaviors...). A dependency change is never a BC break.
   - `new-features`, title `New <em>features</em>.`, `tone-emerald`: new capabilities.
   - `improvements`, title `<em>Improvements</em>.`, `tone-indigo`: enhancements of existing features.
   - `dependencies`, title `<em>Dependencies</em>.`, `tone-violet`: changes of the required version of the language,
     of its extensions or of other packages (the language skill says where they are declared).
   - `other`, title `<em>Other</em> changes.`, `tone-slate`: everything else (bugfixes, deprecations, tests, coding standards,
     documentation, CI...). Its `section-note` is always `No impact on your code.`
   The title is followed by the number of changes shown in it: `<h2><span>BC <em>breaks</em>.</span><span class="count">2</span></h2>`,
   then a `section-note` describing the type for this version, then the `commits` list, one row per change.
   **A type without any change has no section at all.**
   If there is no commit at all, display a single section `The <em>commits</em>.` (`tone-teal`) with an `empty` block.
   Each row shows only the `message` of the change (no author, no date, no hash: the commit is reached through its icon),
   When the change has an example page, the label links to it (`<a class="commit-main">`), otherwise it is not a link
   (`<div class="commit-main">`).
   On the right of the row, `commit-links` holds one icon link (inline SVG, with `title` and `aria-label`) for, in this order:
   - each example page of the change, titled `Example`, linking to our page (same tab);
   - the commit on GitHub, titled `Commit <10 first characters of the hash>`;
   - its pull request, titled `Pull request #<number>` (if `pullRequest` is set).
   Its `links` (blog...) are not shown on the release page.
   Copy the markup and the SVG icons from the reference page.
5. Section `The sources.` (no tone): comparison on GitHub, documentation of the package, changelog of the version.
6. Footer: `Last checked on <today, YYYY-MM-DD>.`

## What counts as a new feature

Only new features and improvements of existing features: never bugfixes, deprecations, tests, coding standards or CI.
The commits are the starting point: they list every modification of the version. The changelog of the version helps
to find the features, but never replaces the commits.

The message of a commit is not enough: always read its diff (`git show <hash> -- <directory>`) to check that its
label tells everything it does. A message can be vague, or forget a part of the change (e.g. "Remove BC layer" that also
changes a signature). Write the label from what the diff does. When a commit does several things (e.g. a new option and
a deprecation), give it one change per thing, each with its own label and type: the commit is then shown once per change.

## Finding the commits

1. Find the repository that holds the history, and the directory of the package in it, from the vendor skill
   (by default: the repository itself, its root directory).
2. Clone it in the scratchpad directory, without blobs to stay fast:
   `git clone --filter=blob:none --no-checkout <url>`, then fetch the branches and tags you need.
3. Previous version: given by the vendor skill (by default the previous minor version).
4. Commits of the version, merge commits excluded, limited to the directory of the package:
   - released: `git log --no-merges <previous branch>..<tag of the first release> -- <directory>`
   - in development: `git log --no-merges <previous branch>..<version branch> -- <directory>`
5. Link the commits to the repository that holds them (`https://github.com/<owner>/<repository>/commit/<hash>`).

## Commit settings

The classification of the commits is stored in `config/releases/<vendor>/<package>/settings.json`,
the same path as the pages in `docs/`, one file per package for all its versions.
The page is built from this file: never classify a commit only in the page.

```json
{
    "commits": {
        "df4804a0650e6177d2fa85df6d97b88471173968": {
            "changes": [
                {
                    "message": "Add the `foo` option",
                    "section": "new-features",
                    "pages": [
                        {
                            "type": "example",
                            "slug": "foo-option"
                        }
                    ]
                },
                {
                    "message": "Deprecate the `bar` option, use `foo` instead",
                    "section": "other",
                    "pages": []
                }
            ],
            "hidden": false,
            "pullRequest": "https://github.com/<owner>/<repository>/pull/<number>",
            "links": []
        }
    }
}
```

- Key: the full hash of the commit.
- `changes`: what the commit does, one item per thing it does, each shown as a row of the release page
  (see [What counts as a new feature](#what-counts-as-a-new-feature)). Most commits have one change.
  Each change has a `message`, a `section` and `pages`:
- `message`: the label of the change displayed in the pages, written from the diff and the commit message.
  Remove the prefix naming the package (e.g. `[OptionsResolver]`): the page is already about it.
  It starts with a capital letter. Write code between backticks, displayed as `<code>`. It can be edited to make it clearer:
  the page shows the `message` of the settings file, never the original commit message.
  Two changes of the same commit have different labels.
  For a `dependencies` change, add the previous requirement at the end, read in the dependency file of the previous
  version (e.g. ``Bump Symfony 8 to PHP `>= 8.4` (was `>= 8.2`)``): versions are code, between backticks.
- `section`: the type of the change, `bc-breaks`, `new-features`, `improvements`, `dependencies` or `other`.
- `hidden`: `true` to leave the commit out of the pages, `false` otherwise. Hide every commit that only changes
  tests in the directory of the package (the vendor skill says where they are): list its files with
  `git show --stat --format= <hash> -- <directory>`. Such a commit has a single change in `other`.
  A hidden commit stays in the file so that it is never asked again. None of its changes is displayed nor counted in a type,
  but it is counted in the `Commits` stat, which gives the real number of commits of the version.
- `pullRequest`: full URL of the pull request that merged the commit (e.g. `https://github.com/<owner>/<repository>/pull/<number>`),
  `null` when the commit was pushed directly.
  Find it with `git rev-list --first-parent --ancestry-path <hash>..<tag or branch> | tail -1`: if the commit itself is
  on the first-parent line of the branch, it was pushed directly; otherwise this merge commit's message holds `#<number>`.
- `links`: other pages that talk about the commit or its pull request, as `{"title": "...", "url": "..."}` objects,
  `[]` if none. Always search the sources listed by the vendor skill (blog...); other articles are welcome.
  They are not shown on the release page, only in the sources of the example pages of the commit,
  with the title in the format given by the vendor skill.
- `pages`: the pages our site builds for the change, `[]` if none. Each page has a `type` and a `slug`
  (its directory, lowercase words separated by `-`). The only type for now is `example`,
  see [Example pages](#example-pages).

The version whose page displays a commit is not stored: it is the version in which `git log` finds the commit
(see [Finding the commits](#finding-the-commits)).

Before building the page:

1. If the settings file does not exist, create it with `{"commits": {}}`.
2. List the commits of the version (see [Finding the commits](#finding-the-commits)) that are not in the file yet.
3. If there are some, read the diff of each of them, write its changes (label and type of each) yourself, then ask the
   user to confirm with the `AskUserQuestion` tool, 4 changes per call: one question per change, its header being the
   short hash, the question showing the label (and saying when the commit has several changes), and the options being
   your proposed section first (marked `(Recommended)`) then the 3 next most likely sections (the user can pick the 5th
   one through "Other"). Their `pages` is `[]`.
   Commits that only change tests are not asked: write them directly as `other` and `hidden`, and list them in the summary.
4. Write the answers in the settings file, keeping the commits sorted by date, oldest first, then build the page.
5. Commits already in the file are never asked again: their settings are used as they are.

## Example pages

A change of a commit can have example pages, listed in its `pages` setting with the `example` type, and stored in
`docs/releases/<vendor>/<package>/<version>/<slug>/index.html`.
Use `docs/releases/symfony/options-resolver/8.0/nested-options/index.html` as the template:

- Breadcrumb down to the slug, title without badge.
- The section `At a glance.` starts with a stat `Type`, whose value is the type of the change
  (`BC break`, `New feature`, `Improvement`, `Dependency` or `Other`), with the tone of the section of this type
  on the release page (e.g. `<div class="stat tone-rose">` for a BC break), then the versions concerned.
  The stat of the version of the change (e.g. `Old way removed` for a BC break) has the same tone as `Type`.
  When the old way was deprecated first, a stat `Old way deprecated` (no tone, like the other versions)
  gives its version, separate from the stat of the version adding the new way (e.g. `<code>setOptions()</code> added`).
  After the stats, a `section-note` sums up the change and how to migrate (no subtitle under the title).
- Then these sections, in this order, the ranges of versions titled with the versions as inline code (no link):
  - `<h2><span><em>BC break</em></span></h2>` (for a BC break, with the tone of its type: `tone-rose`): one block of
    code per syntax (e.g. one for `setDefault()`, one for the fluent `default()`), the old line followed by the new one, each line preceded by a PHP comment giving the versions where
    it works (`// 4.2 – 7.4`, then `// >= 8.0`), the old names in `data-removed`, the new ones in `data-added`.
    The old range starts at the version that introduced it (read in the changelog of the package) and ends at the
    last version where it can be used.
    **A deprecated code can still be used**: the deprecation only warns. The old range goes up to the last
    version before the removal (here `7.4`), deprecated versions included.
    When a syntax of the old way came later (e.g. a fluent method), give its version in its comment and in a paragraph just above its block of code.
    No separate section for the new way: these blocks already show it.
  - `<h2><span><em>Deprecated</em> <code>7.3 – 7.4</code></span></h2>` (`tone-orange`, the warning color), when the old way was
    deprecated before being removed: a paragraph saying that the old code still works but triggers a deprecation,
    then the deprecation message as `language-text` code.
  - `<h2><span><em>Migration</em></span></h2>`, with the tone of the type of the change (`tone-rose` for a BC break):
    what you saw happens when the code is not migrated (error or silent change of behavior, in a `callout` block),
    the code showing it, how it fails and how to find the code to migrate (the version adding the new way is
    already in `At a glance`).
  Skip the ranges that do not apply (e.g. no `Deprecated` section for a change removed without deprecation).
  In these sections, write one sentence per paragraph (`<p>`), also inside a `callout`.
- Code: **only the code that changed**, a few lines: never a full implementation (no class, no unrelated options),
  use `// ...` for the rest, but write an empty body as `{}`, never `{ // ... }`. Old and new code side by side in the
  same block, one block per syntax (see `BC break`).
  Write code as `<pre class="code"><code class="language-<Pygments lexer>">` (the language skill gives it, e.g.
  `language-php`; other text as `language-text`), then run
  `bin/dev/highlight.py <page>`: it colors the code blocks with Pygments in the HTML itself (no JavaScript,
  no flicker on load), inside the `codebase-python` Docker image built by `bin/dev/start.py` (run it first). It rebuilds every block from its text, so it can be run again.
  Show what changed by listing the names (methods, classes, options...) on the `<code>` tag, separated by spaces:
  `data-removed="oldMethod"` (red) and `data-added="newMethod"` (green).
- Sources: documentation of the package (always with the anchor of the section when there is one), pull requests, commit,
  and every article that talks about it (search the sources listed by the vendor skill).

The release page links to an example page from the row of its change, see the sections of the commits.

## Parent pages

When the page is new, update every level above it:

- `docs/releases/<vendor>/<package>/index.html`: add the version, newest first,
  with `Released on YYYY-MM-DD, compared to X.Y` or `In development, compared to X.Y`.
- Create the missing `index.html` of the package and vendor levels, and link them from the level above
  (`docs/releases/index.html` lists the vendors, with `<Language> · <description>`).
- `docs/index.html`: add the page to `Latest releases`, and the project to `Projects` if it is new.

## Checks

1. Run `bin/dev/start.py` (it returns once the server is up, leave it running for the user) and check with `curl` that the new page and every parent page answer `200`.
2. Check with `curl -L` that the external links (comparison, commits, pull requests, changelog, articles) answer `200`.
3. Do not commit.
4. Summarize the page to the user: features found, changes by type, commits added to the settings file (and those split in several changes), choices you made.
