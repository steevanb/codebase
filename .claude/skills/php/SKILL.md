---
name: php
description: Knowledge about PHP packages for codebase.watch - package names, where dependencies are declared, how deprecations look, how to write and color PHP code in the pages. Load it before working on a page of the php language, e.g. from /app:release:update or /app:site:update.
---

# PHP

What `/app:release:update` and `/app:site:update` need to know about the packages of the `php` language, whatever their project.
What is specific to a project (Symfony, Doctrine...) is in the skill of its vendor.

## Packages

- A package is named `<vendor>/<package>` on Packagist (https://packagist.org/packages/<vendor>/<package>),
  usually the same name as its GitHub repository.
- Its `composer.json` gives its name (`name`), its directory in a monorepo, and its dependencies.

## Dependencies

The `dependencies` section of a release page is about the changes of `composer.json`:

- `require.php`: the minimum PHP version (e.g. `>=8.4`).
- `require.ext-*`: the PHP extensions.
- `require.*`, `conflict.*`: the other packages and their versions.

A commit only touching `require-dev` is not a dependency change for the users: it goes in `other`.

## Deprecations and BC breaks

- A deprecation is usually triggered with `trigger_error(..., E_USER_DEPRECATED)` (or a helper of the project) and
  documented with a `@deprecated` PHPDoc tag. It is never a BC break: it goes in `other`.
- BC breaks are removed classes, methods or arguments, changed signatures (types, order of the arguments), changed
  behaviors. A raised minimum PHP version goes in `dependencies`, not in `bc-breaks`.

## Code in the pages

- Write PHP code as `<pre class="code"><code class="language-php">`, without the `<?php` tag:
  `bin/dev/highlight.py` colors it with the Pygments PHP lexer.
- Show the PHP names that changed with `data-removed` and `data-added`, e.g. `data-removed="setDefault"`.
- In the texts, a method is written `<code>setOptions()</code>`, a class `<code>OptionsResolver</code>`.
- The Pygments PHP lexer does not color the classes used as types (`OptionsResolver $resolver`) nor `void`:
  this is expected.
