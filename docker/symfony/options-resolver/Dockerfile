FROM codebase-php

COPY --from=composer:2.10.3 /usr/bin/composer /usr/local/bin/composer

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

# Every minor version of symfony/options-resolver in /opt/symfony/options-resolver/<version>, with the dependencies
# allowed by the oldest PHP version that runs it (2.x and 3.x: PHP 5.6, 4.x and 5.x: PHP 7.4, then PHP 8.4).
# The last one is still in development: its branch is installed.
RUN set -e; \
    for versions in \
        2.1:5.6.40 2.2:5.6.40 2.3:5.6.40 2.4:5.6.40 2.5:5.6.40 2.6:5.6.40 2.7:5.6.40 2.8:5.6.40 \
        3.0:5.6.40 3.1:5.6.40 3.2:5.6.40 3.3:5.6.40 3.4:5.6.40 \
        4.0:7.4.33 4.1:7.4.33 4.2:7.4.33 4.3:7.4.33 4.4:7.4.33 \
        5.0:7.4.33 5.1:7.4.33 5.2:7.4.33 5.3:7.4.33 5.4:7.4.33 \
        6.0:8.4.27 6.1:8.4.27 6.2:8.4.27 6.3:8.4.27 6.4:8.4.27 \
        7.0:8.4.27 7.1:8.4.27 7.2:8.4.27 7.3:8.4.27 7.4:8.4.27 \
        8.0:8.4.27 8.1:8.4.27 8.2-dev:8.4.27; \
    do \
        version="${versions%%:*}"; \
        php="${versions#*:}"; \
        case "$version" in \
            *-dev) version="${version%-dev}"; constraint="$version.x-dev" ;; \
            *) constraint="~$version.0" ;; \
        esac; \
        directory="/opt/symfony/options-resolver/$version"; \
        mkdir -p "$directory"; \
        echo '{}' > "$directory/composer.json"; \
        composer --working-dir="$directory" config platform.php "$php"; \
        composer --working-dir="$directory" require --no-interaction --no-progress \
            "symfony/options-resolver:$constraint"; \
    done; \
    rm -rf /root/.composer/cache /root/.cache/composer
