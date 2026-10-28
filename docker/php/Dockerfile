FROM debian:13.7-slim

# PHP 5.6, 7.4 and 8.4 from the repository of Ondřej Surý, with the extensions needed by PHPUnit
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -sSLo /usr/share/keyrings/sury-php.gpg https://packages.sury.org/php/apt.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/sury-php.gpg] https://packages.sury.org/php/ trixie main" \
        > /etc/apt/sources.list.d/sury-php.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        php5.6-cli php5.6-json php5.6-mbstring php5.6-xml \
        php7.4-cli php7.4-json php7.4-mbstring php7.4-xml \
        php8.4-cli php8.4-mbstring php8.4-xml \
    && rm -rf /var/lib/apt/lists/*

# The newest PHPUnit allowed by each PHP version, run with phpunit-php5.6, phpunit-php7.4 and phpunit-php8.4
RUN set -e; \
    for versions in 5.6:5.7.27 7.4:9.6.38 8.4:13.4.3; do \
        php="${versions%%:*}"; \
        phpunit="${versions#*:}"; \
        curl -sSLo "/usr/local/lib/phpunit-$phpunit.phar" "https://phar.phpunit.de/phpunit-$phpunit.phar"; \
        printf '#!/bin/sh\nexec php%s /usr/local/lib/phpunit-%s.phar "$@"\n' "$php" "$phpunit" \
            > "/usr/local/bin/phpunit-php$php"; \
        chmod +x "/usr/local/bin/phpunit-php$php"; \
    done

WORKDIR /app
