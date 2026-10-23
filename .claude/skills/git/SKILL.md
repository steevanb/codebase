---
name: git
description: Git in codebase.watch - when to commit, the single commit of a pull request, how to write the pull requests (title, the "Changes" and "Pages changed" sections). Load it before committing, pushing, or creating or updating a pull request, e.g. at the end of /app:release:update, /app:changes:review or /app:site:update.
---

# Git

When to commit, how to build the single commit of a pull request, and the format of the pull requests of the
project. The global rules also apply (no attribution, no merge commit).

## Commits

- The commands of the project (`/app:release:update`, `/app:changes:review`, `/app:site:update`) never commit: they
  leave their changes in the working tree. Commit, push and create a pull request only when the user asks for it.
- A single commit per pull request, on top of `origin/master` (see the global rules): `git fetch --prune origin`
  first (the branch of a merged pull request is deleted on GitHub, and a stale `origin/<branch>` makes
  `git push --force-with-lease` fail), then `git reset --soft origin/master` and one commit, then
  `git push --force-with-lease -u origin <branch>`.
- The previous pull requests of a branch are squash-merged: before a new pull request, check that the branch has no
  difference with `origin/master` besides the new work (`git diff --stat origin/master HEAD`), then rebuild its
  single commit as above.

## Pull requests

Title: a short sentence saying what the pull request adds or changes, e.g. `Add resolve() examples`.

The description has two sections, in this order:

```markdown
## Changes

- `resolve()`: new examples about the merge of the options, their order in the result and the steps of the resolution.
- `clone`: `'foo'` and `'bar'` marked in blue in the examples "Clone" and "Original resolver".

## Pages changed

- [2.1/resolve](http://localhost:25100/releases/symfony/options-resolver/2.1/resolve/)
- [2.1/clone](http://localhost:25100/releases/symfony/options-resolver/2.1/clone/)
```

### Changes

One line per change, the page or the method it is about first (in inline code), then what changed.

- When the pull request changes pages of `docs/` (HTML, CSS), list only what changes in the pages: what a reader of
  the site sees (examples, marks, layout, icons...). The changes of the tools, the skills and the commands
  (e.g. `bin/dev/highlight.py`, `.claude/`) are left out, even when they produced the changes of the pages.
- When the pull request changes no page, list every change (tools, skills, commands, settings files...).

### Pages changed

Every page of `docs/` changed by the pull request, one per line, linked to the local server (`bin/dev/start.py`,
`http://localhost:25100/`): `[<path>](http://localhost:25100/<path>/)`, the path relative to `docs/` without
`index.html` (e.g. `releases/symfony/options-resolver/2.1/resolve`), shortened to the part after the package when
every page is from the same package (e.g. `2.1/resolve`).
List them with `git diff --name-only origin/master HEAD -- docs/`.
When some pages only change for a reason shared by all of them (e.g. a new icon on every example page), group them
in a second list under a line saying it (e.g. `Link icon only:`), after the pages whose content changed.
Without any page changed, write `None.`
