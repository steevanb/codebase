#!/usr/bin/env python3

"""Highlight the code blocks of the pages in docs/ with Pygments.

Every <pre class="code"><code class="language-<name>"> block is colored with <span class="tok-*"> tags,
<name> being the name of a Pygments lexer (php, javascript, python...), language-text being left as is.
The tags are written in the HTML itself: no JavaScript, no flicker when the page loads.
A block is always rebuilt from its plain text, so the script can be run again safely.

The names listed in the data-removed and data-added attributes of the <code> tag (separated by spaces) are
wrapped in <mark class="code-removed"> and <mark class="code-added">, to show what changed between two versions:
<pre class="code"><code class="language-php" data-added="setOptions">
The names listed in data-other are wrapped in <mark class="code-other"> (blue), to tell them apart from the green ones
(e.g. two options of the same example), and those listed in data-third in <mark class="code-third"> (amber), for a
third one.
A name followed by #<number> is only marked at this occurrence in the code (1 for the first), not in the comments:
data-other="$previousValue#3" marks the third $previousValue only, array_merge([])#2 the array of the second call.
A string ('firstName') is also marked in the comments, between ' or ": // The option "firstName" does not exist.
So is a constant (null, true, false) or a number, as a whole word: // ['key' => null]
A variable followed by a call ($clone->resolve) marks the variable only where this method is called on it.
A call followed by ([]) marks the brackets of the array given to this call, not what is inside: resolve([]) marks
the [ and ] of resolve(['foo']), or array( and ) before PHP 5.4, also after a name: set('roles', ['foo']).
fn([]) marks the array returned by a closure: fn (Options $options): array => ['foo'].
The title of an example (<h3> followed by its block) gets the class example-exception when its code throws an
exception (a comment starting with its class: // InvalidOptionsException: ...), example-ok otherwise, unless it is
example-warning, written by hand for a surprising behavior: the CSS shows "OK", "Exception" or "Warning" before it.
The examples of a section are sorted: OK, then warnings, then exceptions.
When a marked name is the type of a parameter of a function or a method, its parameter is marked with it, in the
same <mark>, and its uses in the body of the function are marked too:
function (Options $options) { return $options['a']; } marks "Options $options" and "$options".
A marked class is not marked after new (new Options()).

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
# PHP 8.4: a call on new without parentheses around it, chained on the next lines
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
TAG = re.compile(r'</?(?:span|mark)[^>]*>')
MARKS = {'removed': 'code-removed', 'added': 'code-added', 'other': 'code-other', 'third': 'code-third'}
# A marked type in a parameter list (after "(" or ","), followed by its parameter
TYPED_PARAMETER = re.compile(
    r'(<span class="tok-p">[^<]*[(,]</span>\s*(?:<span class="tok-o">\?</span>)?)'
    r'<mark class="([\w-]+)">(<span class="tok-\w+">[^<]+</span>)</mark>(\s+)'
    # The parameter may be marked too (data-added="mixed $options#3"): one mark for both
    r'(?:<mark class="\2">)?(<span class="tok-nv">\$\w+</span>)(?:</mark>)?'
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
        for name in (html.unescape(names.group(1)).split() if names else []):
            # name#2: only the second occurrence of the name in the code, not in the comments
            name, occurrence = re.fullmatch(r'(.+?)(?:#(\d+))?', name).groups()
            occurrence = int(occurrence) if occurrence else None
            # A class is not marked where it is created (new Options()): only where it is used
            colored = sub_occurrence(
                rf'(?<!<span class="tok-k">new</span> )<span class="tok-\w+">{re.escape(name)}</span>',
                lambda token: f'<mark class="{css_class}">{token.group(0)}</mark>',
                colored,
                occurrence,
            )
            # A string is also marked in the comments (results, exception messages), between ' or "
            string = re.fullmatch(r"'([^']+)'", name)
            if string and occurrence is None:
                colored = COMMENT.sub(
                    lambda comment: re.sub(
                        rf'([\'"]){re.escape(string.group(1))}\1',
                        lambda quoted: f'<mark class="{css_class}">{quoted.group(0)}</mark>',
                        comment.group(0),
                    ),
                    colored,
                )
            # A constant (null, true, false) or a number is also marked in the comments, as a whole word
            elif occurrence is None and re.fullmatch(r'null|true|false|\d+(?:\.\d+)?', name):
                colored = COMMENT.sub(
                    lambda comment: re.sub(
                        rf'(?<![\w.\'"]){re.escape(name)}(?![\w.\'"])',
                        lambda word: f'<mark class="{css_class}">{word.group(0)}</mark>',
                        comment.group(0),
                    ),
                    colored,
                )

            # A variable only where a method is called on it ($clone->resolve): not its other uses
            receiver = re.fullmatch(r'(\$\w+)->(\w+)', name)
            if receiver:
                colored = re.sub(
                    rf'<span class="tok-nv">{re.escape(receiver.group(1))}</span>'
                    rf'(?=<span class="tok-o">-&gt;</span>(?:<mark[^>]*>)?<span class="tok-na">{receiver.group(2)}</span>)',
                    lambda token: f'<mark class="{css_class}">{token.group(0)}</mark>',
                    colored,
                )
            # The brackets of the array given to a call (resolve([])): [ and ], or array( and ), not what is inside
            call = re.fullmatch(r'(\w+)\(\[\]\)', name)
            if call:
                ranges = array_brackets(colored, call.group(1))
                if occurrence:
                    ranges = ranges[2 * occurrence - 2:2 * occurrence]
                colored = mark_ranges(colored, ranges, css_class)

    # One mark for the type and its parameter, so that the space between them is marked too
    colored = TYPED_PARAMETER.sub(
        lambda match: f'{match.group(1)}<mark class="{match.group(2)}">{match.group(3)}{match.group(4)}{match.group(5)}</mark>',
        colored,
    )

    for parameter in TYPED_PARAMETER_MARKED.finditer(colored):
        colored = mark_in_body(colored, parameter.end(), parameter.group(2), parameter.group(1))

    return colored

def sub_occurrence(pattern: str, replacement, colored: str, occurrence: int | None) -> str:
    """re.sub, on every match, or only on the given one (1 for the first)."""
    if occurrence is None:
        return re.sub(pattern, replacement, colored)
    matches = list(re.finditer(pattern, colored))
    if len(matches) < occurrence:
        return colored
    match = matches[occurrence - 1]

    return colored[:match.start()] + replacement(match) + colored[match.end():]

def plain_text(colored: str) -> tuple[str, list[int]]:
    """The text of colored code, and the position in the colored code of each of its characters."""
    text, positions = '', []
    for character in re.finditer(r'<[^>]+>|&[#\w]+;|[^<&]', colored):
        if not character.group(0).startswith('<'):
            text += html.unescape(character.group(0))
            positions.append(character.start())

    return text, positions

def array_brackets(colored: str, function: str) -> list[tuple[int, int]]:
    """The positions in the text of the brackets of the arrays given to a function, outside the comments."""
    text, _ = plain_text(colored)
    ranges = []
    # The array is the first argument, or the second one after a name or a variable: set('roles', ['foo']);
    # fn([]) is the array returned by a closure: fn (Options $options): array => ['foo'], or return array('foo');
    pattern = (r'(?:=> |return )(\[|array\()' if function == 'fn'
               else rf'(?<![\w$]){re.escape(function)}\((?:\'[^\']*\', |\$\w+, )?(\[|array\()')
    for call in re.finditer(pattern, text):
        if '//' in text[text.rfind('\n', 0, call.start()) + 1:call.start()]:
            continue
        start = call.start(1)
        end = expression_end(text, call.end())
        ranges += [(start, call.end()), (end, end + 1)]

    return ranges

def open_token(colored: str) -> str:
    """The opening tag of the token still open at the end of colored code, or an empty string."""
    tags = []
    for tag in re.finditer(r'<span class="tok-\w+">|</span>', colored):
        if tag.group(0) == '</span>':
            tags.pop()
        else:
            tags.append(tag.group(0))

    return tags[-1] if tags else ''

def mark_ranges(colored: str, ranges: list[tuple[int, int]], css_class: str) -> str:
    """Mark ranges of the text of colored code, splitting the tokens they start or end in."""
    _, positions = plain_text(colored)
    for start, end in sorted(ranges, reverse=True):
        first = positions[start]
        last = positions[end - 1] + len(re.match(r'&[#\w]+;|.', colored[positions[end - 1]:], re.DOTALL).group(0))
        before, after = open_token(colored[:first]), open_token(colored[:last])
        colored = (
            colored[:first] + ('</span>' if before else '') + f'<mark class="{css_class}">' + before
            + colored[first:last] + ('</span>' if after else '') + '</mark>' + after + colored[last:]
        )

    return re.sub(r'<span class="tok-\w+"></span>', '', colored)

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
