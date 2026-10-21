---
name: symfony-options-resolver
description: Knowledge about the symfony/options-resolver package for codebase.watch - how to write its examples. Load it before writing or reviewing an example page of symfony/options-resolver, e.g. from /app:site:update or /app:changes:review.
---

# symfony/options-resolver

What the example pages of `symfony/options-resolver` need, in addition to the skills `symfony` and `php`.

## Examples

- Every block of code that configures an `OptionsResolver` ends with a call to `resolve()`, its result in a comment
  just above it, written with the syntax of the block:

  ```php
  // array('gender' => 'male', 'firstName' => 'John')
  $options = $resolver->resolve(array('firstName' => 'John'));
  ```

- The result is the one the version gives, keys in their order: check it by running the code with the version of the
  package (clone `https://github.com/symfony/options-resolver` at its tag in the scratchpad directory, then run the
  code in the official `php` Docker image of the closest available PHP version, e.g. `php:5.6-cli` for 2.1).
  E.g. in 2.1, the given options come after the default ones in the result.
