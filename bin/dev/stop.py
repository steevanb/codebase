#!/usr/bin/env python3

"""Stop the local server started by bin/dev/start.py."""

import subprocess

CONTAINER = 'codebase-server'


def main():
    result = subprocess.run(['docker', 'rm', '--force', CONTAINER], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print('The server is not running')
    else:
        print('Server stopped')


if __name__ == '__main__':
    main()
