---
name: php
description: Knowledge about PHP packages for codebase.watch - package names, where dependencies are declared, how deprecations look, how to write and color PHP code in the pages. Load it before working on a page of the php language, e.g. from /app:release:update or /app:site:update.
---

# PHP

What `/app:release:update`, `/app:changes:review` and `/app:site:update` need to know about the packages of the `php`
language, whatever their project.
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

`require-dev` only holds the dependencies needed to develop the package: a commit only touching it goes in `other`.

## PHP versions of a version

The settings file of each version has a `php` key, after `maintenance`: the PHP versions allowed by `require.php` of
the `composer.json` of its `ref`, shown in the `At a glance.` section of the release page (`7.1 – 7.4`, or `>= 8.4`).

- `min`: the minor version of the lowest PHP version allowed (`>=8.4.1` gives `8.4`, `^5.5.9|>=7.0.8` gives `5.5`).
- `max`: the last minor version allowed, only when the constraint has an upper bound (`^7.1.3` gives `7.4`, the last
  PHP 7); omitted otherwise.

```json
"php": {
    "min": "7.1",
    "max": "7.4"
}
```

Check it each time the file is checked: the branch of a version in development can change it.

## Labels of the changes

Official case of the names (see the `changes` skill): `PHP`, `PHPDoc`, `PHPUnit`, e.g.
``Bump to PHP `>= 8.4.1` (was `>= 8.4`)``, never ``Bump to php `>= 8.4.1` ``.

## Deprecations and BC breaks

- A deprecation is usually triggered with `trigger_error(..., E_USER_DEPRECATED)` (or a helper of the project) and
  documented with a `@deprecated` PHPDoc tag.
- What is a BC break and where deprecations go: see the `changes` skill.

## Code in the pages

- Write PHP code as `<pre class="code"><code class="language-php">`, without the `<?php` tag:
  `bin/dev/highlight.py` colors it with the Pygments PHP lexer.
- Show the PHP names that changed with `data-removed` and `data-added`, e.g. `data-removed="setDefault"`.
  A marked class used as the type of a parameter of a function or a method marks its parameter too
  in the same mark (`function (Options $options)` marks `Options $options`), and its uses in the body of the
  function too, done by `bin/dev/highlight.py`.
- Comment giving the versions where a line works (only when the block compares versions, see `/app:site:update`):
  `// 4.2 – 7.4`, `// >= 8.0`.
- Never write `// ...` for the code left out: leave it out. Write an empty body as `{}`.
- An exception thrown by a line is shown like a result, in a comment just above it: the short name of its class, then
  its message copied exactly, e.g. `// MissingOptionsException: The required option "lastName" is  missing.`
- Version of the language in the `code-meta` of a block: `PHP <major>.<minor>`, the minimum PHP version required by
  the oldest version of the package shown in the block (its `php.min`), e.g. `<span>PHP 5.3</span>` for 2.1.
- Use the syntax of the minimum PHP version required by the package in the version shown (`require.php`), e.g. no
  `[]` arrays before PHP 5.4 (write `array()`), also in the comments showing a result.
- Chain as many calls as the API allows in the version shown (methods returning `$this`: check it in the code of
  the version), one chained method per line, from the creation of the object:
  - PHP >= 8.4: `new` without parentheses around it;
  - PHP 5.4 – 8.3: `(new OptionsResolver())`;
  - PHP < 5.4: no call on `new`, so create the object in its own statement, then chain on the variable.

  ```php
  // PHP >= 8.4
  $resolver = new OptionsResolver()
      ->setRequired('firstName')
      ->setDefault('age', null);
  // PHP 5.4 – 8.3
  $resolver = (new OptionsResolver())
      ->setRequired('firstName')
      ->setDefault('age', null);
  // PHP < 5.4
  $resolver = new OptionsResolver();
  $resolver
      ->setRequired(array('firstName'))
      ->setDefaults(array('age' => null));
  ```
- In the texts, a method is written `<code>setOptions()</code>`, a class `<code>OptionsResolver</code>`.
- The Pygments PHP lexer does not color the classes used as types (`OptionsResolver $resolver`) nor `void`:
  this is expected.
