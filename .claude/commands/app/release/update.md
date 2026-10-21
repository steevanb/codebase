---
description: Update the settings files (JSON) of the releases of a repository: changes, maintenance and sources of each version
argument-hint: <vendor> <repository> [<version>]   (e.g. symfony options-resolver 8.0)
---

# Update the settings of the releases

Update the settings files of `config/releases/` for one repository: what changed in each version compared to the
previous one, its maintenance and its sources. **Only the JSON files are written**: the pages of `docs/` are built
from them by `/app:site:update`, run it afterwards.

## Parameters

Arguments given: `$ARGUMENTS`

They are, in this order:

1. **Vendor**: the GitHub account, e.g. `symfony`
2. **Repository**: the GitHub repository of the account, e.g. `options-resolver` (`symfony/options-resolver` on GitHub)
3. **Version** (optional): a minor version `X.Y`, e.g. `8.0`. Without it, every version of the repository is updated:
   from the first one containing the package to the one in development.

If the vendor or the repository is missing, ask for it with the `AskUserQuestion` tool before doing anything else,
in a single call.

## Project knowledge

This command is common to every vendor and every language. What is specific comes from two skills,
to load with the `Skill` tool before anything else:

- **The skill of the vendor**, named after the GitHub account (e.g. `symfony`):
  - which repository holds the history (e.g. a monorepo) and the directory of the package in it,
  - how versions, branches and tags work, and what the previous version of a version is,
  - where the maintenance of a version comes from (LTS, end of bug fixes and of security fixes),
  - where to find the changelog, the documentation and the articles (blog...) about a change,
  - how to classify the commits (commit message conventions...) and how to write the labels of the changes,
  - how to name the project and the package.
- **The skill of the language** of the repository, named after it (e.g. `php`, given by the `language` of
  `vendor.json`, or found in the repository): package names, where the dependencies are declared,
  how deprecations and BC breaks look.

If one of them does not exist, find the answers (in the repository for a vendor: README, CONTRIBUTING, branches, tags,
changelog), ask the user what you cannot find, then create the skill in `.claude/skills/<name>/SKILL.md`
with the same sections as the `php` or `symfony` skill, so the next run does not have to look again.

## Settings files

```
config/releases/
└── <vendor>/
    ├── vendor.json                     the vendor
    └── <repository>/
        ├── package.json                the package
        └── <version>.json              one file per minor version, e.g. 8.1.json
```

`vendor.json`, created once:

```json
{
    "name": "Symfony",
    "language": "PHP",
    "description": "Components and bundles of the Symfony framework",
    "subtitle": "What is new in the releases of the Symfony components."
}
```

`package.json`, created once:

```json
{
    "name": "symfony/options-resolver",
    "type": "component",
    "repository": "https://github.com/symfony/options-resolver",
    "history": "https://github.com/symfony/symfony"
}
```

- `name`: the name of the package, as given by the vendor skill.
- `type`: what the package is, in lowercase (`component`, `bundle`, `bridge`, `package`...).
- `repository`: the repository of the package on GitHub.
- `history`: the repository holding the commits (the monorepo for a subtree split), used to link the commits.

`<version>.json`:

```json
{
    "previous": "8.0",
    "release": {
        "ref": "v8.1.0",
        "date": "2026-05-29"
    },
    "maintenance": {
        "bugFixesUntil": "2027-01",
        "securityFixesUntil": "2027-01"
    },
    "sources": [
        {
            "title": "Comparison of 8.0 and v8.1.0",
            "url": "https://github.com/symfony/options-resolver/compare/8.0...v8.1.0"
        }
    ],
    "checkedOn": "2026-10-19",
    "changes": [
        {
            "message": "Add the `foo` option",
            "section": "new-features",
            "commits": [
                {
                    "hash": "df4804a0650e6177d2fa85df6d97b88471173968",
                    "pullRequest": "https://github.com/<owner>/<repository>/pull/<number>"
                }
            ],
            "links": [
                {
                    "title": "Symfony blog: A Week of Symfony #962",
                    "url": "https://symfony.com/blog/a-week-of-symfony-962-june-2-8-2025"
                }
            ],
            "pages": [
                {
                    "type": "example",
                    "slug": "foo-option"
                }
            ]
        },
        {
            "message": "Deprecate the `bar` option, use `foo` instead",
            "section": "other",
            "commits": [
                {
                    "hash": "df4804a0650e6177d2fa85df6d97b88471173968",
                    "pullRequest": "https://github.com/<owner>/<repository>/pull/<number>"
                }
            ]
        },
        {
            "hidden": true,
            "commits": [
                {
                    "hash": "6128512ec5903dd700a59f6fcae6a102490a4ccd"
                }
            ]
        }
    ]
}
```

Keys whose value is the default are omitted: `"hidden": false`, `"lts": false`, `"links": []`, `"pages": []`.

- `previous`: the version it is compared to, given by the vendor skill; omitted for the first version of the package.
- `release`: `ref` is the tag of the first release (`v8.1.0`) and `date` its date (`YYYY-MM-DD`). For a version in
  development, `ref` is its branch (`8.2`) and `version` its current version (e.g. `8.2.0-DEV`), without `date`.
- `maintenance`: from the source given by the vendor skill: `lts` (`true` for a long-term support version),
  `bugFixesUntil` and `securityFixesUntil` (end of bug fixes and of security fixes, `YYYY-MM`).
  They change over time: update them in every file of the repository each time this command runs.
- `sources`: the links of the `The sources.` section of the release page, as `{"title": "...", "url": "..."}`, in this
  order: comparison on GitHub (`Comparison of <previous> and <ref>`, or the commits of the tag for a first version),
  documentation of the package (`<package> documentation`), changelog of the version (`<package> CHANGELOG`) when it
  exists. Check that each URL answers `200` (`curl -sL`) and prefer the final URL of a redirection.
- `checkedOn`: today (`YYYY-MM-DD`), each time the file is checked.
- `changes`: see [Changes](#changes).

## Changes

The entry point is the change (a modification of the package), not the commit: a commit is an information of the
change, the one that made it. A commit doing several things gives several changes, a change made by several commits
lists them all. Changes are sorted by the date of their first commit, oldest first. Each change has:

- `message`: the label of the change shown in the pages, written from the diff and the commit message, following the
  label rules of the vendor skill. It starts with a capital letter. Write code between backticks.
  Two changes of the same commit have different labels.
  For a `dependencies` change, add the previous requirement at the end (e.g. ``Require PHP `>= 8.4` (was `>= 8.2`)``).
- `section`: the type of the change:
  - `bc-breaks`: can break existing code when upgrading (removed features or BC layers, changed signatures or
    behaviors...). A dependency change is never a BC break;
  - `new-features`: new capabilities;
  - `improvements`: enhancements of existing features;
  - `dependencies`: changes of the required version of the language, of its extensions or of other packages
    (the language skill says where they are declared);
  - `other`: everything else (bugfixes, deprecations, tests, coding standards, documentation, CI...).
- `hidden`: `true` to leave the change out of the pages. Hide the change of every commit that only changes tests in the
  directory of the package (the vendor skill says where they are): list its files with
  `git show --stat --format= <hash> -- <directory>`. Such a commit has a single, hidden change, holding only `hidden`
  and the `hash` of its `commits`. It stays in the file so that the commit is never asked again, and is counted in
  the `Commits` stat of the release page.
- `commits`: the commits that made the change, oldest first, each with:
  - `hash`: the full hash of the commit;
  - `pullRequest`: full URL of the pull request that merged the commit, `null` when it was pushed directly.
    Find it with `git rev-list --first-parent --ancestry-path <hash>..<ref> | tail -1`: if the commit itself is on the
    first-parent line, it was pushed directly; otherwise this merge commit's message holds `#<number>`.
    If this command returns nothing, take the oldest commit that is both in `git rev-list --ancestry-path <hash>..<ref>`
    and in `git rev-list --first-parent <ref>`.
- `links`: other pages that talk about the change, its commits or their pull requests, as `{"title": "...", "url": "..."}`.
  Always search the sources listed by the vendor skill (blog...); other articles are welcome.
  They are shown in the sources of the example pages of the change, with the title in the format given by the vendor skill.
- `pages`: the pages our site builds for the change, each with a `type` and a `slug` (its directory, lowercase words
  separated by `-`). The only type for now is `example`: a page showing the change with code, written by
  `/app:site:update`. Add one only when the user asks for it.

### What counts as a new feature

Only new features and improvements of existing features: never bugfixes, deprecations, tests, coding standards or CI.
The commits are the starting point: they list every modification of the version. The changelog of the version helps
to find the features, but never replaces the commits.

The message of a commit is not enough: always read its diff (`git show <hash> -- <directory>`) to check that its
label tells everything it does. A message can be vague, or forget a part of the change (e.g. "Remove BC layer" that also
changes a signature). Write the label from what the diff does. When a commit does several things (e.g. a new option and
a deprecation), give it one change per thing, each with its own label and type.

## Finding the commits

1. Find the repository that holds the history, and the directory of the package in it, from the vendor skill
   (by default: the repository itself, its root directory).
2. Clone it in the scratchpad directory, without blobs to stay fast:
   `git clone --filter=blob:none --no-checkout <url>`, then fetch the branches and tags you need.
3. Previous version: given by the vendor skill (by default the previous minor version).
4. Commits of the version, merge commits excluded, limited to the directory of the package:
   - released: `git log --no-merges <previous branch>..<tag of the first release> -- <directory>`
   - in development: `git log --no-merges <previous branch>..<version branch> -- <directory>`

A change is stored in the file of the version in which `git log` finds its commits.
Every commit of the version is in at least one change.

## Steps

For each version to update (the one given, or all of them, oldest first):

1. Create `vendor.json` and `package.json` if they do not exist.
2. Create the file of the version if it does not exist, with `"changes": []`, and update its `previous`, `release`,
   `maintenance`, `sources` and `checkedOn`.
3. List the commits of the version (see [Finding the commits](#finding-the-commits)) that are in no change of its file yet.
4. If there are some, read the diff of each of them, write its changes (label and type of each) yourself, then ask the
   user to confirm with the `AskUserQuestion` tool, 4 changes per call: one question per change, its header being the
   short hash, the question showing the label (and saying when the commit has several changes), and the options being
   your proposed section first (marked `(Recommended)`) then the 3 next most likely sections (the user can pick the 5th
   one through "Other"). When there are many commits (e.g. every version of a repository), ask the user first whether
   to confirm each change or to classify them yourself.
   When a commit continues a change already in the file (e.g. a fix of a feature of the same version), add it to the
   `commits` of that change instead of creating a new one.
   Commits that only change tests are not asked: write their change directly as `hidden`, and list them in the summary.
5. Write the changes in the file of the version, keeping them sorted.
6. Changes already in a file are never asked again: they are kept as they are.

## Checks

1. Every file is valid JSON, and every commit of each version is in a change of its file.
2. Check with `curl -L` that the new URLs (sources, pull requests, links) answer `200`.
3. Do not touch `docs/`, do not commit.
4. Summarize to the user, per version: features found, changes by type, changes added (and the commits split in
   several changes), choices you made. Then tell them to run `/app:site:update` to build the pages.
