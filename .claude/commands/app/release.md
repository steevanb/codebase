---
description: Create or update the codebase.watch page listing what is new in a release
argument-hint: <language> <repository> <version>   (e.g. php symfony/options-resolver 8.0)
---

# Create a release page

Create (or update) the page that lists the new features and improvements of one version of one repository,
compared to the previous version.

## Parameters

Arguments given: `$ARGUMENTS`

They are, in this order:

1. **Language**: e.g. `php`
2. **Repository**: e.g. `symfony/options-resolver`, in the `<vendor>/<package>` form of GitHub
3. **Version**: e.g. `8.0`, always a minor version `X.Y`

If a parameter is missing, ask for it with the `AskUserQuestion` tool before doing anything else.
Ask for all the missing parameters in a single call.

## Project knowledge

This command is common to every language and every project. What is specific comes from two skills,
to load with the `Skill` tool before anything else:

- **The skill of the language**, named after it (e.g. `php`): package names, where the dependencies are declared,
  how deprecations and BC breaks look, how to write and color code in the pages.
- **The skill of the vendor**, named after the vendor of the repository (e.g. `symfony` for `symfony/options-resolver`):
  - which repository holds the history (e.g. a monorepo) and the directory of the package in it,
  - how versions, branches and tags work, and what the previous version of a version is,
  - where to find the changelog, the documentation and the articles (blog...) about a change,
  - how to classify the commits (commit message conventions...),
  - how to name the project and the package in the pages.

If one of them does not exist, find the answers (in the repository for a vendor: README, CONTRIBUTING, branches, tags,
changelog), ask the user what you cannot find, then create the skill in `.claude/skills/<name>/SKILL.md`
with the same sections as the `php` or `symfony` skill, so the next run does not have to look again.

## Site architecture

The site is hosted on GitHub Pages from the `docs/` directory of the `master` branch,
with the custom domain `codebase.watch`.

```
docs/
├── CNAME                   codebase.watch
├── .nojekyll               files are served as is
├── 404.html
├── index.html              home page
├── assets/css/main.css     styles shared by every page
└── releases/
    ├── index.html                                  list of languages
    └── <language>/
        ├── index.html                              list of vendors
        └── <vendor>/
            ├── index.html                          list of packages
            └── <package>/
                ├── index.html                      list of versions, newest first
                └── <version>/index.html            the release page
```

- One URL = one directory containing an `index.html`: `https://codebase.watch/releases/<language>/<vendor>/<package>/<version>/`.
- Links are absolute from the site root (`/releases/<language>/`, `/assets/css/main.css`), never relative.
  The site cannot be browsed through `file://`: run `bin/dev/start.py` (http://localhost:25100, served in the
  background by the `codebase-server` container), stop it with `bin/dev/stop.py`.
- Links to another site (GitHub, documentation, blog posts...) open in a new tab: `target="_blank" rel="noopener"`.
  Links inside the site do not.
- Name what the text is about: the package when it is about the package, the project only when it is about the whole
  project, which should be rare. The vendor skill gives the names and examples.
  Quoted texts (commit messages, deprecation messages) are left as they are.
- Every mention of a package in a text links to our page of the version it talks about
  (`/releases/<language>/<vendor>/<package>/<version>/`), or to the page of the package
  (`/releases/<language>/<vendor>/<package>/`) when we have no page for this version. Never link a page to itself.
- Every page is written in English, and uses only `/assets/css/main.css`: no inline style, no external dependency.
  Add the classes a page needs to `main.css` instead of duplicating styles.
- Every page has a breadcrumb linking each level: `codebase.watch / releases / <language> / <vendor> / <package> / <version>`.

## Reference page

Use `docs/releases/php/symfony/options-resolver/8.0/index.html` as the template: same structure, same classes.

1. Breadcrumb.
2. Title as given by the vendor skill (e.g. `<Project> <Package> <version>`), with a badge:
   `Released` if the version has been released (tag of its first release), `In development` otherwise.
3. Subtitle: `New features and improvements of the <code><repository></code> <component, package...>, compared to <previous version>.`
4. Stats: compared versions (`7.4 → 8.0`), number of new features and improvements, number of commits,
   date of the first release of the version (or the current version, e.g. `8.2.0-DEV`, when in development).
5. Section `New features and improvements`: one entry per new feature or improvement of an existing feature.
   Explain each one shortly, with a code example when it helps understanding how to use it.
   If there is none, keep the section with an `empty` block explaining why
   (e.g. maintenance release, major version that only removes deprecated code, branch identical to the previous one).
6. Section `Commits`, split in groups, in this order. Each group is a `section` value of the settings file
   (see [Commit settings](#commit-settings)):
   - `bc-breaks`, title `BC breaks`: changes that can break existing code when upgrading (removed features or BC layers,
     changed signatures or behaviors...). A dependency change is never a BC break.
   - `new-features`, title `New features`: new capabilities.
   - `improvements`, title `Improvements`: enhancements of existing features.
   - `dependencies`, title `Dependencies`: changes of the required version of the language, of its extensions or of
     other packages (the language skill says where they are declared).
   - `other`, title `Other`: everything else (bugfixes, deprecations, tests, coding standards, documentation, CI...).
   Each group shows its number of commits. **A group without any commit is not displayed at all.**
   If there is no commit at all, display an `empty` block instead of the groups.
   Each commit shows its message, its author and its date (no hash: the commit is reached through its icon).
   When the commit has an example page, the whole row links to it and the message ends with an `Example` tag
   (`<a class="commit-main">`); otherwise the row is not a link (`<div class="commit-main">`).
   On the right of the row, `commit-links` holds one icon link (inline SVG, with `title` and `aria-label`, the commit one titled `Commit <10 first characters of the hash>`) for:
   the commit on GitHub, its pull request (if `pullRequest` is set), and each of its `links`.
   Copy the markup and the SVG icons from the reference page.
7. Section `Sources`: comparison on GitHub, changelog of the version, documentation of the package.
8. Footer: `Last checked on <today, YYYY-MM-DD>.`

## What counts as a new feature

Only new features and improvements of existing features: never bugfixes, deprecations, tests, coding standards or CI.
The changelog of the version is the main source, the commits confirm it. Read the diff of a commit when its
message is not enough to classify it.

## Finding the commits

1. Find the repository that holds the history, and the directory of the package in it, from the vendor skill
   (by default: the repository itself, its root directory).
2. Clone it in the scratchpad directory, without blobs to stay fast:
   `git clone --filter=blob:none --no-checkout <url>`, then fetch the branches and tags you need.
3. Previous version: given by the vendor skill (by default the previous minor version).
4. Commits of the version, merge commits excluded, limited to the directory of the package:
   - released: `git log --no-merges <previous branch>..<tag of the first release> -- <directory>`
   - in development: `git log --no-merges <previous branch>..<version branch> -- <directory>`
5. Link the commits to the repository that holds them (`https://github.com/<owner>/<repository>/commit/<hash>`).

## Commit settings

The classification of the commits is stored in `config/releases/<language>/<vendor>/<package>/settings.json`,
the same path as the pages in `docs/`, one file per package for all its versions.
The page is built from this file: never classify a commit only in the page.

```json
{
    "commits": {
        "df4804a0650e6177d2fa85df6d97b88471173968": {
            "message": "Add an option to ...",
            "section": "new-features",
            "pullRequest": "https://github.com/<owner>/<repository>/pull/<number>",
            "links": [],
            "pages": [
                {
                    "type": "example",
                    "slug": "new-option"
                }
            ]
        }
    }
}
```

- Key: the full hash of the commit.
- `message`: first line of the commit message, only to make the file readable.
- `section`: `bc-breaks`, `new-features`, `improvements`, `dependencies` or `other`.
- `pullRequest`: full URL of the pull request that merged the commit (e.g. `https://github.com/<owner>/<repository>/pull/<number>`),
  `null` when the commit was pushed directly.
  Find it with `git rev-list --first-parent --ancestry-path <hash>..<tag or branch> | tail -1`: if the commit itself is
  on the first-parent line of the branch, it was pushed directly; otherwise this merge commit's message holds `#<number>`.
- `links`: other pages that talk about the commit or its pull request, as `{"title": "...", "url": "..."}` objects,
  `[]` if none. Always search the sources listed by the vendor skill (blog...); other articles are welcome.
  The title is shown as the tooltip of the icon, in the format given by the vendor skill.
- `pages`: the pages our site builds for the commit, `[]` if none. Each page has a `type` and a `slug`
  (its directory, lowercase words separated by `-`). The only type for now is `example`,
  see [Example pages](#example-pages).

The version whose page displays a commit is not stored: it is the version in which `git log` finds the commit
(see [Finding the commits](#finding-the-commits)).

Before building the page:

1. If the settings file does not exist, create it with `{"commits": {}}`.
2. List the commits of the version (see [Finding the commits](#finding-the-commits)) that are not in the file yet.
3. If there are some, classify each of them yourself (read its diff when the message is not enough), then ask the user
   to confirm with the `AskUserQuestion` tool, 4 commits per call: one question per commit, its header being the short
   hash, the question showing the message, and the options being your proposed section first (marked `(Recommended)`)
   then the 3 next most likely sections (the user can pick the 5th one through "Other"). Their `pages` is `[]`.
4. Write the answers in the settings file, keeping the commits sorted by date, oldest first, then build the page.
5. Commits already in the file are never asked again: their settings are used as they are.

## Example pages

A commit can have example pages, listed in its `pages` setting with the `example` type, and stored in
`docs/releases/<language>/<vendor>/<package>/<version>/<slug>/index.html`.
Use `docs/releases/php/symfony/options-resolver/8.0/nested-options/index.html` as the template:

- Breadcrumb down to the slug, title with the badge of the section (`BC break` uses `badge-danger`).
- Code showing how it worked before and how it works now, with the versions concerned.
  **Only the code that changed**, a few lines: never a full implementation (no class, no unrelated options),
  use `// ...` for the rest. One block for the old way, one block for the new way, each with every syntax concerned.
  Their titles have no link and give the versions as inline code: `<h2>Before <code>&lt;= 7.2</code></h2>`,
  `<h2>Now <code>&gt;= 7.3</code></h2>`.
  Write code as `<pre class="code"><code class="language-<Pygments lexer>">` (the language skill gives it, e.g.
  `language-php`; other text as `language-text`), then run
  `bin/dev/highlight.py <page>`: it colors the code blocks with Pygments in the HTML itself (no JavaScript,
  no flicker on load), inside the `codebase-python` Docker image built by `bin/dev/start.py` (run it first). It rebuilds every block from its text, so it can be run again.
  Show what changed by listing the names (methods, classes, options...) on the `<code>` tag, separated by spaces:
  `data-removed="oldMethod"` on the "before" blocks (red), `data-added="newMethod"` on the "after" blocks (green).
- For a BC break, what happens if the code is not migrated (`callout` block).
- Sources: documentation of the package (always with the anchor of the section when there is one), pull requests, commit,
  and every article that talks about it (search the sources listed by the vendor skill).

The release page links to an example page from the row of its commit, see the `Commits` section.

## Parent pages

When the page is new, update every level above it:

- `docs/releases/<language>/<vendor>/<package>/index.html`: add the version, newest first,
  with `Released on YYYY-MM-DD, compared to X.Y` or `In development, compared to X.Y`.
- Create the missing `index.html` of the package, vendor and language levels, and link them from the level above.
- `docs/index.html`: add the page to `Latest releases`, and the project to `Projects` if it is new.

## Checks

1. Run `bin/dev/start.py` (it returns once the server is up, leave it running for the user) and check with `curl` that the new page and every parent page answer `200`.
2. Check with `curl -L` that the external links (comparison, commits, pull requests, changelog, articles) answer `200`.
3. Do not commit.
4. Summarize the page to the user: features found, commits by group, commits added to the settings file, choices you made.
