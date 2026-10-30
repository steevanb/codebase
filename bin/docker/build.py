#!/usr/bin/env python3

"""Build the Docker images used by the bin/ scripts, one after the other, in the order of IMAGES.

Shows a table with one row per image, its status and its build time, with a loader while it builds.
When a build fails, its output is shown and the next images are not built.
Without the provenance attestation, which holds the build time, an image built again from the cache keeps its ID: the
images built FROM it then stay cached too.
Only uses the standard library.

Usage: bin/docker/build.py
"""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

# An image built from another one (FROM) comes after it
IMAGES = [
    ('codebase-python', 'docker/python'),
    ('codebase-php', 'docker/php'),
    ('codebase-symfony-options-resolver', 'docker/symfony/options-resolver'),
]

LOADER = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
HEADERS = ('Image', 'Status', 'Time')
STATUS_WIDTH = len('· building')
INTERACTIVE = sys.stdout.isatty()

def color(text: str, code: str) -> str:
    return f'\x1b[{code}m{text}\x1b[0m' if INTERACTIVE else text

def status_cell(status: str, frame: int) -> str:
    text = {
        'waiting': '· waiting',
        'building': f'{LOADER[frame % len(LOADER)]} building',
        'built': '✓ built',
        'failed': '✗ failed',
    }[status]
    code = {'waiting': '2', 'building': '36', 'built': '32', 'failed': '31'}[status]

    return color(text.ljust(STATUS_WIDTH), code)

def table(rows: list[dict], frame: int) -> list[str]:
    widths = [
        max(len(HEADERS[0]), *(len(row['image']) for row in rows)),
        max(len(HEADERS[1]), STATUS_WIDTH),
        max(len(HEADERS[2]), len('000.0s')),
    ]
    lines = [
        color('  '.join(header.ljust(width) for header, width in zip(HEADERS, widths)), '1'),
        '  '.join('─' * width for width in widths),
    ]
    for row in rows:
        duration = f'{row["duration"]:.1f}s' if row['duration'] is not None else ''
        lines.append('  '.join([
            row['image'].ljust(widths[0]),
            status_cell(row['status'], frame),
            duration.rjust(widths[2]),
        ]))

    return lines

class Screen:
    """Draws the table again in place, on a terminal."""

    def __init__(self):
        self.height = 0

    def draw(self, lines: list[str]):
        if self.height:
            sys.stdout.write(f'\x1b[{self.height}A')
        sys.stdout.write(''.join(f'\x1b[2K{line}\n' for line in lines))
        sys.stdout.flush()
        self.height = len(lines)

def build(row: dict, screen: Screen, rows: list[dict]) -> str:
    """Builds the image of the row, drawing the loader while it builds, and returns the output of docker build."""
    started = time.monotonic()
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            ['docker', 'build', '--quiet', '--provenance=false', '--tag', row['image'], str(ROOT_DIR / row['context'])],
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        frame = 0
        while process.poll() is None:
            row['duration'] = time.monotonic() - started
            if INTERACTIVE:
                screen.draw(table(rows, frame))
            frame += 1
            time.sleep(0.1)
        row['duration'] = time.monotonic() - started
        row['status'] = 'built' if process.returncode == 0 else 'failed'
        output.seek(0)

        return output.read().decode(errors='replace')

def main():
    rows = [{'image': image, 'context': context, 'status': 'waiting', 'duration': None} for image, context in IMAGES]
    screen = Screen()
    if INTERACTIVE:
        sys.stdout.write('\x1b[?25l')
    try:
        for row in rows:
            row['status'] = 'building'
            output = build(row, screen, rows)
            if INTERACTIVE:
                screen.draw(table(rows, 0))
            if row['status'] == 'failed':
                if not INTERACTIVE:
                    print('\n'.join(table(rows, 0)), flush=True)
                sys.exit(f'\nBuilding Docker image {row["image"]} failed:\n{output}')
        if not INTERACTIVE:
            print('\n'.join(table(rows, 0)))
    finally:
        if INTERACTIVE:
            sys.stdout.write('\x1b[?25h')
            sys.stdout.flush()

if __name__ == '__main__':
    main()
