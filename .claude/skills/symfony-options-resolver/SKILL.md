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

- Define an option with `setRequired()` when its value is given to `resolve()` and its default value plays no part
  in the example: `setDefaults()` only when the example is about the default value (or about `setDefaults()`).

- The result is the one the version gives, keys in their order: check it by running the code with the version of the
  package (clone `https://github.com/symfony/options-resolver` at its tag in the scratchpad directory, then run the
  code in the official `php` Docker image of each PHP version offered, with `.claude/skills/php/run-blocks.py`, see the
  `php` skill).
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
