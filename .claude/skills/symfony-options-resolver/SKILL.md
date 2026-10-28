---
name: symfony-options-resolver
description: Knowledge about the symfony/options-resolver package for codebase.watch - how to write its examples, where to check a validated change (issue #9). Load it before writing or reviewing an example page of symfony/options-resolver, or validating one of its changes, e.g. from /app:site:update or /app:changes:review.
---

# symfony/options-resolver

What the example pages and the validation of the changes of `symfony/options-resolver` need, in addition to the
skills `symfony` and `php`.

## Examples

- Every block of code that configures an `OptionsResolver` ends with a call to `resolve()`, its result in a comment
  just above it, written with the syntax of the block:

  ```php
  // array('key' => 'foo', 'firstName' => 'bar')
  $options = $resolver->resolve(array('firstName' => 'bar'));
  ```

  When `resolve()` throws an exception, its result is not assigned (no useless variable, see the `php` skill):

  ```php
  // MissingOptionsException: The required option "firstName" is  missing.
  $resolver->resolve();
  ```

- Mark with `data-mark-1` what the example shows, the key of the option or its value, depending on what the example
  is about (e.g. the value for an allowed value, the key for a missing option).
  To show that an option exists and keeps its value, mark its key with `data-mark-1` and its value with `data-mark-2`,
  e.g. `data-mark-1="get 'key'" data-mark-2="'foo'"` for `set('key', 'foo')` read as `'foo'`.
  When the value changes (normalized, computed by a lazy option...), mark the new value with `data-mark-3`, with what
  changes it (e.g. `data-mark-3="strtoupper($value) 'FOO@BAR.COM'"`).
  When the value of an option depends on another option (e.g. a lazy option reading it), mark the option it depends on
  with `data-mark-1`, the option read with `data-mark-2` and its computed value with `data-mark-3`, e.g.
  `data-mark-1="get 'firstName'" data-mark-2="'key'" data-mark-3="strtoupper 'FOO'"` for a lazy option `'key'` giving
  `'FOO'` (`strtoupper($options->get('firstName'))`) when `'firstName'` is `'foo'`.

- When an example calls several methods whose order could matter (e.g. `set()` and `setNormalizer()`, an option and
  the lazy option reading it, `set()` and `get()`), say in its description whether the order of the calls matters,
  checked by running the code in the other order, e.g. "The order of the calls to `set()` and `setNormalizer()` does
  not matter: the normalizer can be set before the value.".

- Define an option with `setRequired()` when its value is given to `resolve()` and its default value plays no part
  in the example: `setDefaults()` only when the example is about the default value (or about `setDefaults()`).

- The result is the one the version gives, keys in their order: check it by running the code with the version of the
  package (clone `https://github.com/symfony/options-resolver` at the latest patch release of the version, e.g.
  `v2.1.13` for 2.1, never `v2.1.0`, in the scratchpad directory, then run the code in the official `php` Docker image
  of each PHP version offered, with `.claude/skills/php/run-blocks.py`, see the `php` skill).
  E.g. in 2.1, the given options come after the default ones in the result.

## Validation of the changes

The changes of `symfony/options-resolver` to validate are listed in the issue
[#9](https://github.com/steevanb/codebase/issues/9), by version, one checkbox per change (hidden changes excluded),
in the order of the settings file of the version.
When a change is validated (its `"validated": false` removed), check its box in the issue: read its body with
`gh issue view 9 --json body -q .body`, replace `- [ ] <message>` by `- [x] <message>`, and write it back with
`gh issue edit 9 --body-file <file>`.
The title of each version gives the percentage of its boxes checked, rounded to the nearest integer, e.g.
`### [2.1](https://codebase.watch/releases/symfony/options-resolver/2.1/) 55%`: update it in the same edit.
A change missing from the issue is added at its place, with the links to its
example pages:
``- [x] <message> ([`<slug>`](https://codebase.watch/releases/symfony/options-resolver/<version>/<slug>/))``.
