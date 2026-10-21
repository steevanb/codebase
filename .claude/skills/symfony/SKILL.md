---
name: symfony
description: Knowledge about the Symfony project (symfony/* packages) for codebase.watch - where their history lives, how versions work, where to find their changelog, documentation and blog posts, how to name them. Load it before working on a page about a symfony/* package, e.g. from /app:release:update or /app:site:update.
---

# Symfony

What `/app:release:update` and `/app:site:update` need to know about the `symfony/*` packages (components, bundles, bridges, contracts).

## Repository and history

- Every `symfony/<package>` repository is a **read-only subtree split** of the monorepo `symfony/symfony`:
  never read the history from the split repository, its hashes are rewritten and it has no pull request.
- Clone `https://github.com/symfony/symfony.git` (without blobs, see `/app:release:update`).
- Directory of a package in the monorepo, from its name:

  | Package | Directory |
  |---|---|
  | Component, e.g. `symfony/options-resolver` | `src/Symfony/Component/OptionsResolver` |
  | Sub-component, e.g. `symfony/security-http` | `src/Symfony/Component/Security/Http` |
  | Component bridge, e.g. `symfony/slack-notifier` | `src/Symfony/Component/Notifier/Bridge/Slack` |
  | Bundle, e.g. `symfony/framework-bundle` | `src/Symfony/Bundle/FrameworkBundle` |
  | Bridge, e.g. `symfony/twig-bridge` | `src/Symfony/Bridge/Twig` |
  | Contracts, e.g. `symfony/service-contracts` | `src/Symfony/Contracts/Service` |

  When in doubt, find the directory whose `composer.json` has `"name": "symfony/<package>"`.
- The tests of a package are in the `Tests/` directory of its directory (e.g. `src/Symfony/Component/OptionsResolver/Tests`).
- Link the commits and pull requests to the monorepo: `https://github.com/symfony/symfony/commit/<hash>`,
  `https://github.com/symfony/symfony/pull/<number>`.
- The comparison link can use the split repository, it is easier to read:
  `https://github.com/symfony/<package>/compare/<previous branch>...v<version>.0`.

## Versions

- One minor version every 6 months: `X.0` in November, `X.1` in May, ..., up to `X.4` (LTS) in November.
- Each version has a branch `X.Y` and its releases are tagged `vX.Y.Z`. The version in development has a branch but
  no `vX.Y.0` tag: its version is in `src/Symfony/Component/HttpKernel/Kernel.php` (`VERSION`, e.g. `8.2.0-DEV`).
- Previous version: `X.Y-1`, or `(X-1).4` for an `X.0` (e.g. `8.0` → `7.4`).
- A major version (`X.0`) adds no feature: it only removes what was deprecated in `(X-1).*` and can raise the minimum
  PHP version. Its features come with `(X-1).4`, released the same day.
- Older branches are merged up into newer ones ("Merge branch '7.4' into 8.0"): always compare with the previous
  branch (`git log <previous branch>..<tag>`), never between two tags, or the bugfixes of the previous branch come in.
- The feature freeze of a minor version happens about 2 months before its release.

## Maintenance status

The status of each version (shown as badges on the page of a package) comes from the Symfony release API:
`curl -s https://symfony.com/releases/<X.Y>.json`, e.g. `https://symfony.com/releases/7.4.json`
(the same data as the "Releases" page, `https://symfony.com/releases/<X.Y>`).
Call it with `curl`: it answers `403 Forbidden` to the default user agent of Python's `urllib`
(from a script, run `curl -sf <url>` with `subprocess`, or send a browser-like `User-Agent` header).

| API | Badge |
|---|---|
| version without a `vX.Y.0` tag (see Versions) | `In development` |
| otherwise | `Released` |
| `is_eomed: false` | `Bug fixes` and `Security fixes`: bugs and security issues are still fixed |
| `is_eomed: true`, `is_eoled: false` | `Security fixes`: only security issues are fixed (e.g. 5.4) |
| `is_eoled: true` | `Unmaintained` |
| `is_lts: true` | `LTS` (in addition to the maintenance badge) |

The same API gives the end dates, as `MM/YYYY`: `eom` (end of bug fixes) and `eol` (end of security fixes).
Store them in the `maintenance` of the settings file of the version, as `YYYY-MM`: `lts` from `is_lts` (omitted when `false`),
`bugFixesUntil` from `eom`, `securityFixesUntil` from `eol`.

The status changes over time: fetch it again for every version each time the page of the package is updated.

## Classifying the commits

- The merge commit of a pull request starts with its type: `feature #<number>` (new feature, improvement or
  deprecation), `bug #<number>` (bugfix), `minor #<number>` (no visible change: tests, coding standards, docs...),
  `tidy #<number>`. It helps, but read the diff: a `feature` can be a deprecation (`other`), a `minor` can raise the
  required PHP version (`dependencies`).
- `src/.../<Package>/CHANGELOG.md` has a section per minor version (`8.2`, then `---`): the main source of the
  new features. `UPGRADE-X.Y.md` at the root of the monorepo lists the deprecations and BC breaks of each version.
- A deprecation message has the form `Since symfony/<package> X.Y: ...`.

## Labels of the changes

The `message` of a change in the settings file, written from the diff and the commit message:

- Remove the tag of the component, bundle or bridge that starts the commit message (e.g. `[OptionsResolver]`,
  `[Form]`): the page is already about the package.
- Start with a capital letter, with a verb when possible (`Add`, `Remove`, `Make`, `Require`...).
- Write code between backticks: methods with their parentheses (`setDefault()`), classes, options, versions.
- Remove the class name when it is redundant: name it once instead of before each method.
  E.g. ``Add `OptionsResolver::isKnown()` and `OptionsResolver::isRequired()` `` becomes
  ``Add `isKnown()` and `isRequired()` to `OptionsResolver` ``.
  Keep `Class::method()` when the label names a single method and the class is needed to know which one.
- Two changes of the same commit have different labels.
- For a `dependencies` change, end with the previous requirement, in backticks:
  ``Require PHP `>= 8.2` (was `>= 8.1`)``. When the same version changes a requirement twice, the second change gives
  the value it replaces.

## Documentation

- Component page: `https://symfony.com/doc/<version>/components/<package_with_underscores>.html`,
  e.g. `https://symfony.com/doc/8.0/components/options_resolver.html` (sections have anchors, e.g. `#nested-options`). Not every package has a component page: search `https://symfony.com/doc/<version>/`.
- CHANGELOG: `https://github.com/symfony/symfony/blob/v<version>.0/src/Symfony/.../<Package>/CHANGELOG.md`
  (`blob/<branch>/...` when in development).

## Blog posts

Search `symfony.com/blog` for every commit or pull request, and add what you find to `links`:

- **"New in Symfony X.Y: ..."**: a dedicated post with examples, the best source when it exists.
- **"Symfony X.Y.0-BETA1 released"**: lists every `feature` pull request of the version.
- **"A Week of Symfony #NNN (dates)"**: lists the main merges of the week, by branch ("8.0 changelog"), with the
  hash of the merge commit (not of the commit itself). Find it from the date of the merge.

Title of the links: `Symfony blog: <title of the post>`, e.g. `Symfony blog: A Week of Symfony #962`.

## Naming

- Project: `Symfony`. Package: its repository name, `symfony/<package>`, e.g. `symfony/options-resolver`,
  never a class-style name like `OptionsResolver` (keep class names only in code and in `<code>` about a class).
- Page title: `symfony/<package> <version>`, e.g. `symfony/options-resolver 8.0`.
- In the texts, name the package when it is about the package (`symfony/options-resolver 8.0 removes...`,
  `For symfony/options-resolver 7.2 and older`), and Symfony only when it is about the whole project, which should
  be rare (`the Symfony 8.2 feature freeze`, `Symfony 8 requires PHP 8.4`).
