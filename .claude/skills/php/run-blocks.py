#!/usr/bin/env python3

"""Run the PHP blocks of a page with every PHP version they are written for.

Every <pre class="code" data-php="<versions>"> of the page (colored or not by bin/dev/highlight.py) is run once per
version of its data-php attribute, in the official php:<version>-cli Docker image, with the package installed in
<package dir> (a clone of its repository at the tag of the version shown): its dependencies are installed there
first with the composer Docker image when it has no vendor/ directory.
Each block is written to a file of <scratch dir>, run by run-block.php (next to this script): the output is the value
of the last variable set by the block (var_export, e.g. $options), or the exception (or the Error, PHP >= 7.0) it
throws, written like in the pages (short name of its class, then its message), to compare with the comment of the
block: before PHP 7.0, an Error is a fatal error, printed by PHP.
The deprecations triggered by the package itself (not by the block) are left out: an old version of a package
triggers some with a recent PHP version.

The images of PHP 5.3, 5.4 and 5.5 can no longer be pulled (manifest v1, refused by containerd >= 2.1, or a missing
layer): their code is run with PHP 5.6, which runs the same code but does not check that it only uses what these
versions support.

Usage: .claude/skills/php/run-blocks.py <page.html> <package dir> [<scratch dir>]
"""

import html
import os
import re
import subprocess
import sys
import tempfile

OLDEST_IMAGE = '5.6'
RUNNER_DIR = os.path.dirname(os.path.abspath(__file__))

def blocks(page):
    content = open(page).read()
    for match in re.finditer(r'<pre class="code" data-php="([^"]+)"><code class="language-php"[^>]*>(.*?)</code></pre>', content, re.S):
        yield match.group(1).split(), html.unescape(re.sub(r'<[^>]+>', '', match.group(2)))

def image(version):
    major, minor = (int(part) for part in version.split('.'))

    return f'php:{OLDEST_IMAGE if (major, minor) < (5, 6) else version}-cli'

def install(package):
    if not os.path.isdir(os.path.join(package, 'vendor')):
        subprocess.run(
            ['docker', 'run', '--rm', '-u', f'{os.getuid()}:{os.getgid()}', '-v', f'{package}:/app', 'composer:2',
             'install', '--no-dev', '--no-interaction', '--quiet', '--ignore-platform-reqs'],
            check=True,
        )

def run(package, scratch, name, version):
    output = subprocess.run(
        ['docker', 'run', '--rm', '-v', f'{package}:/package:ro', '-v', f'{scratch}:/blocks:ro',
         '-v', f'{RUNNER_DIR}:/runner:ro', image(version),
         'php', '-d', 'error_reporting=-1', '-d', 'display_errors=stderr', '/runner/run-block.php', f'/blocks/{name}'],
        capture_output=True, text=True,
    )
    lines = (output.stdout + output.stderr).splitlines()

    return '\n'.join(line for line in lines if line.strip() and not re.search(r'Deprecated: .* in /package/', line))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    page, package = sys.argv[1], os.path.abspath(sys.argv[2])
    scratch = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else tempfile.mkdtemp()
    install(package)
    for number, (versions, code) in enumerate(blocks(page), 1):
        name = f'block-{number}.php'
        open(os.path.join(scratch, name), 'w').write('<?php\n\n' + code + '\n')
        for version in versions:
            print(f'== block {number}, PHP {version} ({image(version)})\n{run(package, scratch, name, version)}')
