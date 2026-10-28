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
- Show the PHP names that changed with `data-removed` and `data-mark-1`, e.g. `data-removed="setDefault"`.
  A marked class used as the type of a parameter of a function or a method marks its parameter too
  in the same mark (`function (Options $options)` marks `Options $options`), and its uses in the body of the
  function too, done by `bin/dev/highlight.py`, but not after `new` (`new Options()` is not marked).
- Comment giving the versions where a line works (only when the block compares versions, see `/app:site:update`):
  `// 4.2 – 7.4`, `// >= 8.0`.
- A block starts with a `use` statement for each class it uses in its code (`new`, types of the parameters,
  `instanceof`, `::`...), even when it only compares versions, sorted alphabetically, one per line, followed by an
  empty line. Also for a class only named in a comment (e.g. an exception shown as a result:
  `// InvalidOptionsException: ...` needs `use Symfony\Component\OptionsResolver\Exception\InvalidOptionsException;`),
  except a class of the global namespace (e.g. `OutOfBoundsException`).

  ```php
  use Symfony\Component\OptionsResolver\Options;
  use Symfony\Component\OptionsResolver\OptionsResolver;

  $resolver = new OptionsResolver();
  ```
- Never write `// ...` for the code left out: leave it out. Write an empty body as `{}`.
- An exception thrown by a line is shown like a result, in a comment just above it: the short name of its class, then
  its message copied exactly, e.g. `// MissingOptionsException: The required option "lastName" is  missing.`
  The end of a message giving a local path (where PHP ran the code) is cut, with the comma before it, e.g.
  `, called in /package/OptionsResolver.php on line 192` or ` in /package/Options.php on line 506`: it depends on
  the machine, not on the package.
- A PHP error triggered by a line is shown the same way, the name of its constant first: `E_NOTICE`, `E_WARNING`,
  `E_DEPRECATED`, `E_ERROR` (a fatal error), `E_RECOVERABLE_ERROR` (a catchable fatal error), e.g.
  `// E_WARNING: Undefined array key "email"`, never `// Warning: ...`. Also in the texts (e.g. a callout:
  "An `E_NOTICE`, ..."). `bin/dev/highlight.py` shows the name starting such a comment like the label of the title
  of its example: amber for `E_NOTICE`, `E_WARNING` and `E_DEPRECATED`, red for an exception, an `Error`, `E_ERROR`
  and `E_RECOVERABLE_ERROR`.
- No useless variable: a call is assigned to a variable only when its result is shown (in the comment above it, or
  used by the next lines). A call throwing an exception is not assigned, e.g.
  `// OptionDefinitionException: ...` above `$options->all();`, not `$all = $options->all();`.
- When the code of a block behaves differently depending on the PHP version (e.g. an `E_WARNING`, then `false`, before
  PHP 8.0, a `TypeError` since), the label of the example (`OK`, `Warning` or `Exception`) is the one of the newest
  PHP version offered: `Exception` for the `TypeError` of PHP 8.4. A warning callout gives the behavior of each range
  of versions (see `/app:site:update`).
  A different level of PHP error is a different behavior too, even when the code goes on the same way: e.g. an
  `E_NOTICE` before PHP 8.0 and an `E_WARNING` since for an undefined array key, an `E_ERROR` before PHP 7.0 and an
  `Error` since, an `E_RECOVERABLE_ERROR` before PHP 7.0 and a `TypeError` since.
- Version of the language in the `code-meta` of a block: `PHP <major>.<minor>`, the minimum PHP version required by
  the oldest version of the package shown in the block (its `php.min`), e.g. `<span>PHP 5.3</span>` for 2.1.
- Write the code with the syntax of the newest PHP version offered: 8.4, or the `php.max` of the version shown when
  it is lower (e.g. 7.4). `bin/dev/highlight.py` derives the code of the older versions offered (the minimum PHP
  version of the package, 5.6, 7.4), chosen in a menu of the `code-meta`, removing what they do not support: `new`
  without parentheses (8.4), `mixed` and union types (8.0), arrow functions (7.4), `void`, nullable and `iterable`
  types (7.1), scalar and return types (7.0), `[]` arrays and calls on `new` (5.4), also in the comments showing a
  result. Write this code as the last `<pre>` of the block (the other ones are rebuilt from it).
  Chain from `new` every call returning `$this`. `new` is always on its own line, every call (even a single one) on
  the next lines, one per line, a comment (e.g. an exception) just above the call it is about:

  ```php
  $resolver = new OptionsResolver()
      ->setDefaults(['key' => 'foo']);
  ```

  Before PHP 5.4, a single call becomes a statement on the variable, its comment above it after an empty line
  (`$resolver->setDefaults(array('key' => 'foo'));`), several calls are chained on the variable.
- Type as much as the newest version allows: the parameters and the return type of every closure (e.g.
  `fn (Options $options, string $value): string => strtoupper($value)`), `mixed` when any value is possible.
  A closure only returning an expression is an arrow function (`fn`).
- A closure is always on its own line: given to a call with other arguments, each argument goes on its own line;
  in an array, the array has one element per line.

  ```php
  $options->set(
      'key',
      fn (Options $options): string => 'foo'
  );
  $resolver = new OptionsResolver()
      ->setDefaults([
          'key' => fn (Options $options): string => 'foo',
      ]);
  ```
- In a list of values, `null` always comes first, before the other values: `[null, 'foo']`, never `['foo', null]`.
  Also in a list of types: `'null'` first, e.g. `setAllowedTypes(['age' => ['null', 'int']])`, never
  `['int', 'null']`.
- Chain as many calls as the API allows in the version shown (methods returning `$this`: check it in the code of
  the version), from the creation of the object, one chained method per line, below `new` (see above):
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
  In a title (`h1`, `h2`, `h3`), a method is written with its full signature, as declared in the code of the version
  shown: `<code>setDefault(string $option, mixed $value): static</code>` (see `/app:site:update`).
- The Pygments PHP lexer does not color the classes used as types (`OptionsResolver $resolver`) nor `void`:
  this is expected.

## Testing the code of the pages

Run every block of a page with each PHP version it offers, after `bin/dev/highlight.py` (it writes the code of the
older versions), and compare the output with the comment of the block (result or exception).
Always test with the latest patch release of the version shown (e.g. `v2.1.13` for 2.1, never `v2.1.0`): it is the one
the users install. Find it with `git ls-remote --tags`:

```bash
git ls-remote --tags https://github.com/<vendor>/<package> 'v<version>.*' | sed 's/.*tags\///; s/\^{}//' | sort -uV | tail -1
git clone -q --depth 1 -b <latest tag> https://github.com/<vendor>/<package> <scratchpad>/<package>-<latest tag>
.claude/skills/php/run-blocks.py <page> <scratchpad>/<package>-<latest tag> <scratchpad>/blocks
```

- Each `<pre data-php="...">` runs in the official `php:<version>-cli` Docker image of each of its versions, the
  package installed with the `composer:2` image (`composer install`, its `vendor/` kept in the clone).
- It prints `$options` at the end of the block (`var_export`), or the exception thrown, and the PHP errors with the
  name of their constant (`E_WARNING: ...`), written like in the pages.
- The images of PHP 5.3, 5.4 and 5.5 can no longer be pulled (manifest v1 refused by containerd >= 2.1, or a missing
  layer): their code runs with PHP 5.6, which does not check that it only uses what these versions support (e.g.
  `[]` arrays before 5.4): check it by reading the code.
- The deprecations triggered by the package itself are left out (e.g. the return types of `ArrayAccess` with PHP 8.1+
  in an old package); an `E_DEPRECATED`, an `E_NOTICE` or an `E_WARNING` triggered by the block is kept: show it in the page when
  it is part of the example.
