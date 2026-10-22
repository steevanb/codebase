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
So is a constant (null, true, false) or a number, as a whole word: // ['key' => null]
The title of an example (<h3> followed by its block) gets the class example-exception when its code throws an
exception (a comment starting with its class: // InvalidOptionsException: ...), example-ok otherwise, unless it is
example-warning, written by hand for a surprising behavior: the CSS shows "OK", "Exception" or "Warning" before it.
The examples of a section are sorted: OK, then warnings, then exceptions.
When a marked name is the type of a parameter of a function or a method, its parameter is marked with it, in the
same <mark>, and its uses in the body of the function are marked too:
function (Options $options) { return $options['a']; } marks "Options $options" and "$options".

The use statements at the start of a block, with the empty line following them, are wrapped in
<span class="code-uses">, which /assets/js/main.js shows or hides.

A PHP block is written with the syntax of the newest PHP version offered (see below), typed as much as this version
allows. The code-meta gives the minimum PHP version of the package (<span>PHP 5.3</span>): the offered versions are this
one and the last minor version of each newer major version of PHP allowed by the package (5.6, 7.4, 8.4, up to the
php.max of its settings file). The code of the older versions is derived from the newest one, removing what they do
not support: new without parentheses (8.4), mixed and union types (8.0), arrow functions (7.4), void, nullable and
iterable types (7.1), scalar and return types (7.0), [] arrays and calls on new (5.4). The messages shown in the
comments are the ones of each version: the warning of an undefined array key is a notice before PHP 8.0, an Error is
a fatal error before PHP 7.0, a TypeError a catchable fatal error (the message of a TypeError for an argument of
the wrong class is worded differently before PHP 8.0, the TypeError of an illegal offset in isset() is a warning
before PHP 8.0, isset() then giving false).
One <pre class="code" data-php="<versions>"> per different code, from the oldest version to the newest one, the
last one being the source of the others (the same <pre> for every version when the code does not change).
The versions are listed on the code-block (data-php-versions), /assets/js/main.js shows the chosen one.

Runs inside the docker/python image, which provides Pygments: run bin/dev/start.py first to build it.

Usage: bin/dev/highlight.py [file.html ...]   (default: every page in docs/)
"""

import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / 'docs'
IMAGE = 'codebase-python'

BLOCK = re.compile(r'(<pre class="code"[^>]*><code class="language-(?!text")([\w+-]+)"[^>]*>)(.*?)(</code></pre>)', re.DOTALL)
# A block of PHP code, with the PHP version of its code-meta and its <pre>, the first one being the source
PHP_BLOCK = re.compile(
    r'(<div class="code-block")[^>]*(>\s*<div class="code-meta">[^\n]*<span>PHP (\d+\.\d+)</span></div>(\s*))'
    r'((?:<pre class="code"[^>]*><code class="language-php"[^>]*>.*?</code></pre>\s*)+)(</div>)',
    re.DOTALL,
)
PHP_PRE = re.compile(r'<pre class="code"[^>]*>(<code class="language-php"[^>]*>)(.*?)</code></pre>', re.DOTALL)
# The last minor version of each major version of PHP, offered besides the minimum version of the package
PHP_VERSIONS = ['5.6', '7.4', '8.4']
SCALAR_TYPES = 'string|int|float|bool'
# PHP 8.4: a call on new without parentheses around it, on the same line or chained on the next ones
NEW_WITHOUT_PARENTHESES = re.compile(r'^(\$\w+ = )new (\w+\([^()\n]*\))(?=->|\n(?: *//[^\n]*\n)* +->)', re.MULTILINE)
# PHP 8.0: mixed type and union types, of a parameter or returned
MIXED_PARAMETER = re.compile(r'(\(|, )mixed (\$\w+)')
UNION_PARAMETER = re.compile(r'(\(|, )\??[\w\\]+(?:\|[\w\\]+)+ (\$\w+)')
MIXED_OR_UNION_RETURN = re.compile(r'\): (?:mixed|static|[\w\\?]+(?:\|[\w\\]+)+)(?= \{| =>)')
# PHP 8.0: the warning of an undefined key of an array, a notice before
UNDEFINED_KEY = re.compile(r'// Warning: Undefined array key "([^"]*)"')
# PHP 8.0: the message of a TypeError for an argument of the wrong class, worded differently before
TYPE_ERROR_ARGUMENT = re.compile(r'(// TypeError: )([\w\\]+::\w+\(\)): Argument #(\d+) \(\$\w+\) must be of type ([\w\\]+), (\w+) given')
# PHP 8.0: the TypeError of an illegal offset in isset(), a warning before, isset() then giving false
ILLEGAL_OFFSET_ISSET = re.compile(r'// TypeError: Cannot access offset of type \w+ in isset or empty')
# PHP 7.0: an Error thrown (e.g. instanceof on null), a fatal error before; a TypeError, a catchable fatal error
UNCAUGHT_ERROR = re.compile(r'// Error: ')
UNCAUGHT_TYPE_ERROR = re.compile(r'// TypeError: ')
# PHP 7.4: an arrow function, its parameters and its return type
ARROW_FUNCTION = re.compile(r'\bfn (\([^()]*\)(?:: \??[\w\\]+)?) => ')
# PHP 7.1: void, iterable and nullable types
VOID_RETURN = re.compile(r'\): void(?= \{)')
NULLABLE_PARAMETER = re.compile(rf'(\(|, )\?(?:(?:{SCALAR_TYPES}|iterable) (\$\w+)|([\w\\]+) (\$\w+))')
ITERABLE_TYPE = re.compile(r'(\(|, )iterable (\$\w+)|\): \??iterable(?= \{)')
# PHP 7.0: scalar types of the parameters, return types
SCALAR_PARAMETER = re.compile(rf'(\(|, )(?:{SCALAR_TYPES}) (\$\w+)')
RETURN_TYPE = re.compile(r'\): \??[\w\\]+(?= \{)')
# PHP 5.4: a call on new, the object being created in its own statement before
CALL_ON_NEW = re.compile(r'^(\$\w+) = \(new (\w+\([^()\n]*\))\)\n(?=(?: *//[^\n]*\n)* +->)', re.MULTILINE)
# PHP 5.4: a single call on new, on the same line, with the comments above it
SINGLE_CALL_ON_NEW = re.compile(r'^((?://[^\n]*\n)*)(\$\w+) = \(new (\w+\([^()\n]*\))\)->', re.MULTILINE)
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
# The title of an example (<h3>), followed by its paragraphs and its block of code
EXAMPLE_TITLE = re.compile(
    r'<h3(?: class="([^"]*)")?>(.*?</h3>(?:\s*<p>.*?</p>)*\s*<div class="code-block".*?</pre>\s*</div>)',
    re.DOTALL,
)
# The examples of a section, after its title and its paragraphs, and an example in it
SECTION_EXAMPLES = re.compile(
    r'(<section[^>]*>\s*<h2>[^\n]*</h2>(?:\s*<p>.*?</p>|\s*<ul[^>]*>.*?</ul>)*)((?:\s*<h3 class="example-[\w-]+">.*?</pre>\s*</div>)+)(\s*</section>)',
    re.DOTALL,
)
EXAMPLE = re.compile(
    r'\s*<h3 class="example-[\w-]+">.*?</h3>(?:\s*<p>.*?</p>|\s*<div class="callout[^"]*">.*?</div>)*'
    r'\s*<div class="code-block".*?</pre>\s*</div>',
    re.DOTALL,
)
EXAMPLE_ORDER = ['example-ok', 'example-warning', 'example-exception']
# The short name of the class of an exception thrown by the next line, at the start of a comment
EXCEPTION = re.compile(r'<span class="tok-c1">// \w+(?:Exception|Error):')
# The use statements at the start of a block, and the empty lines following them
USES = re.compile(r'(?:use [^\n]+;\n)+\n*')

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
            # A constant (null, true, false) or a number is also marked in the comments, as a whole word
            elif re.fullmatch(r'null|true|false|\d+(?:\.\d+)?', name):
                colored = COMMENT.sub(
                    lambda comment: re.sub(
                        rf'(?<![\w.\'"]){re.escape(name)}(?![\w.\'"])',
                        lambda word: f'<mark class="{css_class}">{word.group(0)}</mark>',
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

def version(name: str) -> tuple:
    return tuple(int(number) for number in name.split('.'))

def php_max(path: Path) -> str | None:
    """php.max of the settings file of the version of a page in docs/releases/<vendor>/<repository>/<version>/."""
    parts = path.resolve().relative_to(DOCS_DIR).parts
    if len(parts) < 5 or parts[0] != 'releases':
        return None
    settings = ROOT_DIR / 'config' / 'releases' / parts[1] / parts[2] / f'{parts[3]}.json'
    if not settings.exists():
        return None

    return json.loads(settings.read_text()).get('php', {}).get('max')

def expression_end(code: str, start: int) -> int:
    """End of the expression starting at start: a ",", ";" or a closing bracket of depth 0, or the end of the line."""
    depth, quote, position = 0, None, start
    while position < len(code):
        character = code[position]
        if quote is not None:
            if character == '\\':
                position += 1
            elif character == quote:
                quote = None
        elif character in '\'"':
            quote = character
        elif character in '([{':
            depth += 1
        elif character in ')]}':
            if depth == 0:
                break
            depth -= 1
        elif character in ',;\n' and depth == 0:
            break
        position += 1

    return position

def closures(code: str) -> str:
    """fn (...) => expression becomes a closure returning the expression, on 3 lines."""
    while (arrow := ARROW_FUNCTION.search(code)) is not None:
        end = expression_end(code, arrow.end())
        indentation = re.match(r' *', code[code.rfind('\n', 0, arrow.start()) + 1:]).group(0)
        code = (
            f'{code[:arrow.start()]}function {arrow.group(1)} {{\n{indentation}    return {code[arrow.end():end]};'
            f'\n{indentation}}}{code[end:]}'
        )

    return code

def long_arrays(code: str) -> str:
    """[...] becomes array(...), in the code and in the comments, not an access to an item ($options['a'])."""
    position = 0
    while (bracket := code.find('[', position)) >= 0:
        position = bracket + 1
        if bracket > 0 and (code[bracket - 1].isalnum() or code[bracket - 1] in '_])}\'"'):
            continue
        depth, quote, end = 1, None, bracket + 1
        while depth > 0:
            if end >= len(code):
                return code
            character = code[end]
            if quote is not None:
                if character == '\\':
                    end += 1
                elif character == quote:
                    quote = None
            elif character in '\'"':
                quote = character
            elif character == '[':
                depth += 1
            elif character == ']':
                depth -= 1
            end += 1
        code = code[:bracket] + 'array(' + code[bracket + 1:end - 1] + ')' + code[end:]

    return code

def calls_on_variable(code: str) -> str:
    """(new X()) followed by calls chained on the next lines becomes a statement creating the object, then the calls
    on its variable: a single call on one line, its comments above it after an empty line, several calls chained on the
    variable."""
    while (new := CALL_ON_NEW.search(code)) is not None:
        variable, end = new.group(1), new.end()
        while end < len(code) and code[end] != ';':
            end = expression_end(code, end) if code[end] not in '\n' else end + 1
            if end < len(code) and code[end] in ',)]}':
                end += 1
        chain = code[new.end():end]
        calls = re.findall(r'^    ->', chain, re.MULTILINE)
        if len(calls) == 1:
            comments, call = re.match(r'((?: *//[^\n]*\n)*) +->(.*)', chain, re.DOTALL).groups()
            comments = re.sub(r'^ +', '', comments, flags=re.MULTILINE)
            statement = (f'\n{comments}' if comments else '') + f'{variable}->' + call.replace('\n    ', '\n')
        else:
            statement = f'{variable}\n{chain}'
        code = f'{code[:new.start()]}{variable} = new {new.group(2)};\n{statement}{code[end:]}'

    return code

def php_syntax(code: str, php: str) -> str:
    """The code written for the newest PHP version offered, written for an older one."""
    if version(php) < (8, 4):
        code = NEW_WITHOUT_PARENTHESES.sub(r'\1(new \2)', code)
    if version(php) < (8, 0):
        code = MIXED_PARAMETER.sub(r'\1\2', code)
        code = UNION_PARAMETER.sub(r'\1\2', code)
        code = MIXED_OR_UNION_RETURN.sub(')', code)
        code = UNDEFINED_KEY.sub(r'// Notice: Undefined index: \1', code)
        code = ILLEGAL_OFFSET_ISSET.sub('// Warning: Illegal offset type in isset or empty\n// false', code)
        code = TYPE_ERROR_ARGUMENT.sub(r'\1Argument \3 passed to \2 must be an instance of \4, \5 given', code)
    if version(php) < (7, 4):
        code = closures(code)
    if version(php) < (7, 1):
        code = VOID_RETURN.sub(')', code)
        code = NULLABLE_PARAMETER.sub(
            lambda match: match.group(1) + (match.group(2) or f'{match.group(3)} {match.group(4)} = null'),
            code,
        )
        code = ITERABLE_TYPE.sub(lambda match: f'{match.group(1)}{match.group(2)}' if match.group(1) else ')', code)
    if version(php) < (7, 0):
        code = SCALAR_PARAMETER.sub(r'\1\2', code)
        code = RETURN_TYPE.sub(')', code)
        code = UNCAUGHT_ERROR.sub('// Fatal error: ', code)
        code = UNCAUGHT_TYPE_ERROR.sub('// Catchable fatal error: ', code)
    if version(php) < (5, 4):
        code = SINGLE_CALL_ON_NEW.sub(
            lambda match: f'{match.group(2)} = new {match.group(3)};\n'
            + (f'\n{match.group(1)}' if match.group(1) else '') + f'{match.group(2)}->',
            code,
        )
        code = long_arrays(calls_on_variable(code))

    return code

def php_variants(match: re.Match, maximum: str | None) -> str:
    """One <pre> per different code among the PHP versions offered, rebuilt from the last one."""
    minimum, indentation = match.group(3), match.group(4)
    code_tag, code = PHP_PRE.findall(match.group(5))[-1]
    text = html.unescape(TAG.sub('', code))
    versions = [minimum] + [
        php for php in PHP_VERSIONS
        if version(php) > version(minimum) and (maximum is None or version(php) <= version(maximum))
    ]

    variants = []
    for php in versions:
        variant = php_syntax(text, php)
        if variants and variants[-1][1] == variant:
            variants[-1][0].append(php)
        else:
            variants.append(([php], variant))

    # A single version offered (e.g. the minimum version of the package is the newest one): no menu
    if len(versions) == 1:
        return f'{match.group(1)}{match.group(2)}<pre class="code">{code_tag}{html.escape(text, quote=False)}</code></pre>{indentation[:-4]}{match.group(6)}'

    pres = indentation.join(
        f'<pre class="code" data-php="{" ".join(served)}">{code_tag}{html.escape(variant, quote=False)}</code></pre>'
        for served, variant in variants
    )

    return f'{match.group(1)} data-php-versions="{" ".join(versions)}"{match.group(2)}{pres}{indentation[:-4]}{match.group(6)}'

def example_title(match: re.Match) -> str:
    """The title of an example says whether its code throws an exception, unless it is a warning (written by hand)."""
    if match.group(1) == 'example-warning':
        return match.group(0)

    return f'<h3 class="example-{"exception" if EXCEPTION.search(match.group(2)) else "ok"}">{match.group(2)}'

def sort_examples(match: re.Match) -> str:
    """The examples of a section, in this order: OK, then warnings, then exceptions, keeping their order otherwise."""
    examples = EXAMPLE.findall(match.group(2))
    if ''.join(examples) != match.group(2):
        return match.group(0)
    examples.sort(key=lambda example: EXAMPLE_ORDER.index(re.match(r'\s*<h3 class="([\w-]+)"', example).group(1)))

    return match.group(1) + ''.join(examples) + match.group(3)

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
        text = html.unescape(TAG.sub('', code))
        uses = USES.match(text)
        colored = mark(highlight(text[uses.end() if uses else 0:], lexer, formatter).rstrip('\n'), opening_tag)
        if uses:
            colored_uses = highlight(uses.group(0), lexer, formatter).rstrip('\n')
            colored = f'<span class="code-uses">{colored_uses}\n\n</span>{colored}'

        return opening_tag + colored + match.group(4)

    maximum = php_max(path)
    updated = BLOCK.sub(replace, PHP_BLOCK.sub(lambda match: php_variants(match, maximum), content))
    updated = SECTION_EXAMPLES.sub(sort_examples, EXAMPLE_TITLE.sub(example_title, updated))
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
