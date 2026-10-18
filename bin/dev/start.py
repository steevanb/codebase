#!/usr/bin/env python3

"""Build the Docker images used by the other bin/dev/ scripts, then serve docs/ locally with nginx, like GitHub Pages does.

The server runs in the background, in the "codebase-server" container: stop it with bin/dev/stop.py,
read its logs with `docker logs -f codebase-server`. Running this script again restarts it.
"""

import subprocess
from pathlib import Path

PORT = 25050
PROJECT_DIR = Path(__file__).resolve().parents[2]
CONTAINER = 'codebase-server'
NGINX_IMAGE = 'nginx:1.30.6-alpine'
DOCKER_IMAGES = {
    'codebase-python': PROJECT_DIR / 'docker' / 'python',
}


def build_docker_images():
    for image, context in DOCKER_IMAGES.items():
        print(f'Building Docker image {image}', flush=True)
        subprocess.run(['docker', 'build', '--quiet', '--tag', image, str(context)], check=True,
                       stdout=subprocess.DEVNULL)


def start_server():
    subprocess.run(['docker', 'rm', '--force', CONTAINER], capture_output=True)
    subprocess.run(
        [
            'docker', 'run', '--detach',
            '--name', CONTAINER,
            '--volume', f'{PROJECT_DIR / "docs"}:/usr/share/nginx/html:ro',
            '--volume', f'{PROJECT_DIR / "docker" / "nginx" / "default.conf"}:/etc/nginx/conf.d/default.conf:ro',
            '--publish', f'{PORT}:80',
            NGINX_IMAGE,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(f'Open http://localhost:{PORT} (stop with bin/dev/stop.py)')


def main():
    build_docker_images()
    start_server()


if __name__ == '__main__':
    main()
