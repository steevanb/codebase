---
description: Review with the user the changes of config/releases/ that are not validated yet: label, section, example page (written), validation
argument-hint: [<vendor> [<repository> [<version>]]]   (e.g. symfony options-resolver 8.1)
---

# Review the changes

Show the user, one by one, the changes of the settings files of `config/releases/` that are not validated yet, and
ask them to check each one. The JSON files are written, and the example pages asked during the review; the other
pages of `docs/` are built from the JSON by `/app:site:update`.

The format of the files and of their changes is described in `/app:release:update`
(`.claude/commands/app/release/update.md`): read it first. Load with the `Skill` tool the `changes` skill (labels
and sections of the changes), the skills of the vendor (e.g. `symfony`) and of the language (e.g. `php`), and the
skill of the package when it exists (`<vendor>-<package>`, e.g. `symfony-options-resolver`).

## Parameters

Arguments given: `$ARGUMENTS`

They are, in this order, all optional, each one narrowing the search:

1. **Vendor**: the directory of `config/releases/`, e.g. `symfony`
2. **Repository**: the directory of the vendor, e.g. `options-resolver`
3. **Version**: a minor version `X.Y`, e.g. `8.1`

Without arguments, every file of `config/releases/` is searched.

## Changes to review

The changes of `config/releases/<vendor>/<repository>/<version>.json` with `"validated": false`, hidden changes
excluded (they are not shown in the pages). A change without `validated` is validated. They are reviewed by vendor,
by repository, by version (oldest first), then in the order of the file.

If there is none, say so and stop. Otherwise, tell the user how many changes there are to review, per version.

## For each change

1. Show the link to the release page holding the change, before anything else:
   `http://localhost:25100/releases/<vendor>/<repository>/<version>/`. If it does not answer (`curl -s -o /dev/null`),
   run `bin/dev/start.py` first.
2. Show its information:
   - its id (the key of the change) and the file;
   - `message`, as it is in the JSON;
   - `section`;
   - `commits`: the short hash with a link to the commit (`<history of package.json>/commit/<hash>`), and the pull
     request (or `pushed directly` when it is `null`);
   - `links` and `pages`, when there are some.
3. Ask with the `AskUserQuestion` tool whether to review this change (header `Review`). Options: `Review`, then
   `Skip` (go to the next change, nothing is written: it will be asked again next time).
4. Ask with the `AskUserQuestion` tool, in a single call, these three questions in this order:
   - **Label** (header `Label`): whether to change the `message` of the change, the question showing it. The options
     are `Keep` first, then up to 2 labels you propose (following the `changes` skill and the skills of the vendor and
     of the language), each one shown in full in its label; the user can write their own through "Other".
   - **Section** (header `Section`): the question lists the 5 sections that can be chosen (`bc-breaks`,
     `new-features`, `improvements`, `dependencies`, `other`) and says which one the JSON has. The options are the
     section of the JSON first, marked `(current)`, then the 3 next most likely sections for this change (the user can
     pick the 5th one through "Other").
   - **Example page** (header `Example`): whether to create a page of type `example` for the change. The options are
     `No` first, then `Yes` with a slug you propose in its description (lowercase words separated by `-`, e.g.
     `nested-options`); the user can give another slug through "Other". When the change already has example pages,
     the question lists them.
5. Write the answers in the JSON right away: the new `message` and the new `section` if they changed, and
   `{"type": "example", "slug": "<slug>"}` added to `pages` if a page was asked.
6. If a page was asked, write it now, as `/app:site:update` does (`.claude/commands/app/site/update.md`, sections
   `Rules` and `Example pages`): run `bin/dev/site.py` so that the release page links to it, write
   `docs/releases/<vendor>/<repository>/<version>/<slug>/index.html`, run `bin/dev/highlight.py` on it, and check
   that it answers `200`. Show its link (`http://localhost:25100/releases/<vendor>/<repository>/<version>/<slug>/`),
   then ask with the `AskUserQuestion` tool whether the page is correct (header `Page`). Options: `Yes`, then `No`
   (the user says what to fix through "Other", or is asked for it). Fix the page and ask again until it is correct.
7. Then ask with the `AskUserQuestion` tool whether to validate the change (header `Validate`), the question
   recalling its message, its section and its pages after the answers. Options: `Yes`, then `No` (it will be asked
   again next time). On `Yes`, remove `"validated": false` from the change.
   When the user answers through "Other" (e.g. a new label), apply what they ask, then ask again.

The user can stop the review at any time: the changes already answered stay written.

## Checks

1. Every file is valid JSON, with the same format: 4 spaces of indentation, non-ASCII characters kept as they are,
   a final newline.
2. In `docs/`, only touch the example pages written and what `bin/dev/site.py` builds. Do not commit.
3. Summarize to the user: changes validated, changes skipped, labels changed, sections changed, example pages
   written, changes left to validate. If a label or a section changed, tell them to run `/app:site:update` to build
   the pages.
