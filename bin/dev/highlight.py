#!/usr/bin/env python3

"""Highlight the code blocks of the pages in docs/ with Pygments.

Every <pre class="code"><code class="language-<name>"> block is colored with <span class="tok-*"> tags,
<name> being the name of a Pygments lexer (php, javascript, python...), language-text being left as is.
The tags are written in the HTML itself: no JavaScript, no flicker when the page loads.
A block is always rebuilt from its plain text, so the script can be run again safely.

The names listed in the data-removed and data-added attributes of the <code> tag (separated by spaces) are
wrapped in <mark class="code-removed"> and <mark class="code-added">, to show what changed between two versions:
<pre class="code"><code class="language-php" data-added="setOptions">
A string ('firstName') is also marked in the comments, between ' or ": // The option "firstName" does not exist.
When a marked name is the type of a parameter of a function or a method, its parameter is marked with it, in the
same <mark>, and its uses in the body of the function are marked too:
function (Options $options) { return $options['a']; } marks "Options $options" and "$options".

Runs inside the docker/python image, which provides Pygments: run bin/dev/start.py first to build it.

Usage: bin/dev/highlight.py [file.html ...]   (default: every page in docs/)
"""

import html
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / 'docs'
IMAGE = 'codebase-python'

BLOCK = re.compile(r'(<pre class="code"><code class="language-(?!text")([\w+-]+)"[^>]*>)(.*?)(</code></pre>)', re.DOTALL)
TAG = re.compile(r'</?(?:span|mark)[^>]*>')
MARKS = {'removed': 'code-removed', 'added': 'code-added'}
# A marked type in a parameter list (after "(" or ","), followed by its parameter
TYPED_PARAMETER = re.compile(
    r'(<span class="tok-p">[^<]*[(,]</span>\s*(?:<span class="tok-o">\?</span>)?)'
    r'<mark class="([\w-]+)">(<span class="tok-\w+">[^<]+</span>)</mark>(\s+<span class="tok-nv">\$\w+</span>)'
)
# A type and its parameter once marked together, to find the parameter in the body of the function
TYPED_PARAMETER_MARKED = re.compile(
    r'<mark class="([\w-]+)"><span class="tok-\w+">[^<]+</span>\s+<span class="tok-nv">(\$\w+)</span></mark>'
)
PUNCTUATION = re.compile(r'<span class="tok-p">([^<]*)</span>')
COMMENT = re.compile(r'<span class="tok-c1">(?:[^<]|</?mark[^>]*>)*</span>')

def run_in_docker():
    image_exists = subprocess.run(['docker', 'image', 'inspect', IMAGE], capture_output=True).returncode == 0
    if not image_exists:
        sys.exit(f'Docker image "{IMAGE}" not found: run bin/dev/start.py first to build it.')

    paths = [str(Path(p).resolve().relative_to(ROOT_DIR)) for p in sys.argv[1:]]
    command = [
        'docker', 'run', '--rm',
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--volume', f'{ROOT_DIR}:/app',
        IMAGE,
        'python', 'bin/dev/highlight.py', *paths,
    ]
    sys.exit(subprocess.run(command).returncode)

def mark(colored: str, opening_tag: str) -> str:
    for attribute, css_class in MARKS.items():
        names = re.search(rf'data-{attribute}="([^"]*)"', opening_tag)
        for name in (names.group(1).split() if names else []):
            colored = re.sub(
                rf'<span class="tok-\w+">{re.escape(name)}</span>',
                lambda token: f'<mark class="{css_class}">{token.group(0)}</mark>',
                colored,
            )
            # A string is also marked in the comments (results, exception messages), between ' or "
            string = re.fullmatch(r"'([^']+)'", name)
            if string:
                colored = COMMENT.sub(
                    lambda comment: re.sub(
                        rf'([\'"]){re.escape(string.group(1))}\1',
                        lambda quoted: f'<mark class="{css_class}">{quoted.group(0)}</mark>',
                        comment.group(0),
                    ),
                    colored,
                )

    # One mark for the type and its parameter, so that the space between them is marked too
    colored = TYPED_PARAMETER.sub(
        lambda match: f'{match.group(1)}<mark class="{match.group(2)}">{match.group(3)}{match.group(4)}</mark>',
        colored,
    )

    for parameter in TYPED_PARAMETER_MARKED.finditer(colored):
        colored = mark_in_body(colored, parameter.end(), parameter.group(2), parameter.group(1))

    return colored

def mark_in_body(colored: str, start: int, variable: str, css_class: str) -> str:
    """Mark the uses of a parameter in the body of its function: from its first "{" to the matching "}"."""
    depth = 0
    for punctuation in PUNCTUATION.finditer(colored, start):
        for character in punctuation.group(1):
            if character == '{':
                depth += 1
            elif character == '}' and depth > 0:
                depth -= 1
                if depth == 0:
                    end = punctuation.start()
                    body = re.sub(
                        rf'(?<!<mark class="{css_class}">)<span class="tok-nv">{re.escape(variable)}</span>',
                        lambda token: f'<mark class="{css_class}">{token.group(0)}</mark>',
                        colored[start:end],
                    )

                    return colored[:start] + body + colored[end:]

    return colored

def process(path: Path) -> bool:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name

    formatter = HtmlFormatter(nowrap=True, classprefix='tok-')
    content = path.read_text()

    def replace(match: re.Match) -> str:
        opening_tag, language, code = match.group(1), match.group(2), match.group(3)
        # startinline: PHP code without the <?php tag
        lexer = get_lexer_by_name(language, startinline=True)
        colored = highlight(html.unescape(TAG.sub('', code)), lexer, formatter).rstrip('\n')

        return opening_tag + mark(colored, opening_tag) + match.group(4)

    updated = BLOCK.sub(replace, content)
    if updated == content:
        return False
    path.write_text(updated)

    return True

def main():
    if os.environ.get('CODEBASE_DOCKER') != '1':
        run_in_docker()

    paths = [Path(p) for p in sys.argv[1:]] or sorted(DOCS_DIR.rglob('*.html'))
    for path in paths:
        if process(path):
            print(f'Highlighted {path}')

if __name__ == '__main__':
    main()
