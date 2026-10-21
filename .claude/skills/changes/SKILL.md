---
name: changes
description: Format of the changes of the settings files of config/releases/ for codebase.watch - how to write their labels (message) and choose their section, whatever the vendor and the language. Load it before writing or reviewing a change, e.g. from /app:release:update or /app:changes:review.
---

# Changes

How to write the `message` and choose the `section` of a change of `config/releases/`, whatever its vendor and its
language. What is specific to a vendor (tags in the commit messages, names...) is in the skill of the vendor, what is
specific to a language (how to write its name, where dependencies are declared...) in the skill of the language.

## The final version only

A change describes what the users get in the released version (its `ref`), never an intermediate state of the
development. Before writing a label, check the code of the version at its `ref` (e.g. `git show <ref>:<file>`):

- A method, class or option added then renamed or changed before the release is named and described as it is in the
  release (e.g. `setNormalizers()`, not `setFilters()` renamed before 2.1.0).
- A commit that only changes something added in the same version (a rename, a fix, a change of signature) is not a
  change of its own: add it to the `commits` of the change that added the thing.

## One change per element

Each new public element is a change of its own: a class, an interface, an exception, and each method of a class, even
when they were all added by the same commits (e.g. the first version of a package). E.g. never
``Add `set()`, `get()` and `has()` to `Options` ``, but three changes ``Add `set()` ...``, ``Add `get()` ...`` and
``Add `has()` ...``. A change lists the commits that touched its element (its code or its PHPDoc), found with
`git log -L <start>,<end>:<file> <ref>` on its lines at the `ref`, and the commit that created it. The commits of the
whole package (README, composer.json...) go to the change that adds the package or the class they are about.

## Groups

A change can have a `group`, the title (Markdown, like a label) of the sub-level it is listed in on the release page,
e.g. ``"group": "`OptionsResolver`"`` for the methods of a class, or `"group": "Exceptions"`. Give the same group to the
changes of a section about the same element (the methods of a class, the exceptions of a package), with one level only.
A change on its own (e.g. the only change about a class) has no group. When all the changes of a section have the same
group, the page shows them without its title. The label does not repeat the group: ``Add `get()` to read the value of
an option``, not ``Add `Options::get()` ...``.

## Labels

The `message` of a change is its label shown in the pages, written from the diff and the commit message:

- Start with a capital letter, with a verb when possible (`Add`, `Remove`, `Make`, `Bump`...).
- Write code between backticks: methods with their parentheses (`setDefault()`), classes, options, files, versions.
- Remove the class name when it is redundant: name it once instead of before each method.
  E.g. ``Add `OptionsResolver::isKnown()` and `OptionsResolver::isRequired()` `` becomes
  ``Add `isKnown()` and `isRequired()` to `OptionsResolver` ``.
  Keep `Class::method()` when the label names a single method and the class is needed to know which one.
- Write the names of languages and tools with their official case, outside of the code between backticks
  (the skill of the language gives them, e.g. `PHP`, `PHPUnit`). When a label writes them in lowercase, fix it.
- Two changes of the same commit have different labels.

### Dependencies

The label of a `dependencies` change ends with the previous requirement, the dependency being the language (e.g.
`PHP`) or a package in backticks:

- New version of a dependency: ``Bump to <dependency> `<requirement>` (was `<previous requirement>`)``, e.g.
  ``Bump to PHP `>= 8.4.1` (was `>= 8.4`)`` or ``Bump to `symfony/deprecation-contracts` `^3` (was `^2.1`)``.
- When the new requirement allows older versions than the previous one, `Lower to` instead of `Bump to`, e.g.
  ``Lower to PHP `^7.2.5` (was `^7.2.9`)``.
- New dependency: ``Require <dependency> `<requirement>` ``, followed by `(was not required)` when the package
  already existed.
- Removed dependency: ``Remove <dependency> (was `<previous requirement>`)``.
- When the same version changes a requirement twice, the second change gives the value it replaces.

## Order

The changes of a file are sorted in a logical order, shown as is in each section of the release page:

- the most important change first (a new class or component before a new method, a removal before a type change);
- the changes of a group next to each other: the changes without a group are shown first, then each group in the order
  of its first change;
- the changes about the same subject next to each other (e.g. `setDeprecated()` then the introspector method getting
  the deprecation; a PHP version then the packages);
- in `other`: what the users see first (deprecations, fixes, messages), then the code quality (annotations, coding
  standards), then the tooling (composer.json, tests, CI, `.gitattributes`), the branch alias last.

## Sections

The `section` of a change is its type:

- `bc-breaks`: can break existing code when upgrading: removed classes, methods, arguments or BC layers, changed
  signatures (types, order of the arguments), changed behaviors. A deprecation is never a BC break (it goes in
  `other`), nor a dependency change (it goes in `dependencies`);
- `new-features`: new capabilities;
- `improvements`: enhancements of existing features;
- `dependencies`: changes of the required version of the language, of its extensions or of other packages
  (the skill of the language says where they are declared). A dependency only needed to develop the package (tests,
  tools) is not a dependency change for the users: it goes in `other`;
- `other`: everything else (bugfixes, deprecations, tests, coding standards, documentation, CI...).

New features and improvements are only new capabilities and enhancements of existing features: never bugfixes,
deprecations, tests, coding standards or CI.
