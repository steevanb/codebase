---
description: Build every page of docs/ (codebase.watch) from the settings files (JSON) of config/releases/
argument-hint: [all]   (all: also the example pages of the validated changes)
---

# Update the site

Build the pages of `docs/` from the settings files of `config/releases/`, written by `/app:release:update`.
The JSON files are never changed by this command: to fix a label, a type or a date, change the JSON with
`/app:release:update` (or by hand), then run this command again.

## Parameters

Arguments given: `$ARGUMENTS`

By default, the example pages of the validated changes (without `"validated": false`, see `/app:changes:review`)
are not processed: they were checked by the user. With `all`, every change is processed. Never ask: only the
argument decides. `bin/dev/site.py` always builds every page it builds, whatever the argument.

## Site architecture

The site is hosted on GitHub Pages from the `docs/` directory of the `master` branch,
with the custom domain `codebase.watch`.

```
docs/
├── CNAME                   codebase.watch
├── .nojekyll               files are served as is
├── 404.html
├── index.html              home page
├── favicon.svg             icon of every page
├── assets/css/main.css     styles shared by every page
├── assets/fonts/           Poppins and JetBrains Mono, self-hosted
├── assets/favicons/        favicons of the sites we link to, named <domain>.svg (or .png)
└── releases/
    ├── index.html                              list of the vendors                    built by bin/dev/site.py
    └── <vendor>/
        ├── index.html                          list of the packages                   built by bin/dev/site.py
        └── <package>/
            ├── index.html                      versions, by major version             built by bin/dev/site.py
            └── <version>/
                ├── index.html                  the release page                       built by bin/dev/site.py
                └── <slug>/index.html           an example page of a change            written by hand
```

## Steps

1. Run `bin/dev/site.py`: it builds every page marked above, and the `Latest releases` and `Projects` lists of
   `docs/index.html`, from the JSON files. It overwrites them: **never edit these pages by hand**, change the script
   (its HTML follows the rules below) or the JSON. It lists the pages it changed.
   If it stops because a favicon is missing, add it (see [Rules](#rules)) and run it again.
2. For each change of the JSON files to process (see [Parameters](#parameters)) with a page of type `example` whose
   `docs/.../<version>/<slug>/index.html` does not exist, write it by hand: see [Example pages](#example-pages).
3. Run the checks.

## Rules

They apply to every page, built by the script or written by hand.

- One URL = one directory containing an `index.html`: `https://codebase.watch/releases/<vendor>/<package>/<version>/`.
  The language is not in the URL: `<vendor>/<package>` is the repository on GitHub, unique whatever its language.
- Links are absolute from the site root (`/releases/<vendor>/`, `/assets/css/main.css`), never relative.
  The site cannot be browsed through `file://`: run `bin/dev/start.py` (http://localhost:25100, served in the
  background by the `codebase-server` container), stop it with `bin/dev/stop.py`.
- Links to another site (GitHub, documentation, blog posts...) open in a new tab: `target="_blank" rel="noopener"`.
  Links inside the site do not.
- Name what the text is about: the package when it is about the package, the project only when it is about the whole
  project, which should be rare. The vendor skill gives the names and examples.
  Quoted texts (commit messages, deprecation messages) are left as they are.
- A message read in the code (deprecation, exception, error...) is copied exactly as the code produces it:
  same words, same punctuation, on a single line if it is a single line, never wrapped nor reformatted.
  Only the placeholders are replaced by their values (e.g. `%s` by the method name), as the code does.
- Every time the name of a package is written, it links to our site: to the page of the version it talks about
  (`/releases/<vendor>/<package>/<version>/`), or to the page of the package (`/releases/<vendor>/<package>/`)
  when it talks about no version or we have no page for this version. Never link to GitHub nor to another site
  from the name of a package. Exceptions: titles (`<title>`, `h1`, `h2`, breadcrumb, `list-title`), quoted texts
  (commit and deprecation messages), and texts that are already a link (e.g. the links of `Sources`).
  Only the page of a package links its name to its repository on GitHub, in its subtitle. Never link a page to itself.
- Every page is written in English, and uses only `/assets/css/main.css`: no inline style, no JavaScript, no external
  dependency. Add the classes a page needs to `main.css` instead of duplicating styles.
- Every page links `/favicon.svg` in its `<head>`, before `main.css`, starts with the `masthead` header (logo,
  navigation with its mobile burger menu; the `Releases` link has `nav-link-active` on every page under `/releases/`),
  and has a breadcrumb linking each level: `codebase.watch / releases / <vendor> / <package> / <version>`.
- Every `section` is a card. Its title is `<h2><span>...</span></h2>`, with one key word in `<em>` (shown with a
  gradient) and a final period, e.g. `<h2><span>New <em>features</em>.</span></h2>`. The `<span>` is required.
  The chapter number (`I`, `II`...) is added by the CSS: never write it.
  Its background color is given by a `tone-<color>` class: `indigo`, `emerald`, `amber`, `rose`, `blue`, `orange`,
  `violet`, `teal`, `slate`. `The sources.` is always white (no class).
- Types of changes and their tones: `bc-breaks` (`BC break`, `rose`), `new-features` (`New feature`, `emerald`),
  `improvements` (`Improvement`, `indigo`), `dependencies` (`Dependency`, `violet`), `other` (`Other`, `slate`).
- The links of a `Sources` section are sorted in this order: commits (and the comparison on GitHub), pull requests,
  documentation of the project, blog of the project, then the rest (changelog, other articles...).
  Each one starts with the favicon of the site it points to, inside the link:
  `<a href="https://github.com/..." target="_blank" rel="noopener"><img class="favicon" src="/assets/favicons/github.com.svg" alt="" width="16" height="16">...</a>`.
  When `docs/assets/favicons/<domain>.svg` does not exist, download the icon declared by the home page of the site
  (`<link rel="icon">`, SVG preferred), check that it contains no script, and make it visible in dark mode
  (a `prefers-color-scheme: dark` style in the SVG) if it is dark.
- Maintenance badges (`<span class="badge tone-<color>">`): `Released <date>` (`blue`), `In development` (`violet`),
  `Bug fixes` (`emerald`), `Security fixes` (`amber`), `Unmaintained` (`rose`), `LTS` (`indigo`).

## Example pages

A change can have example pages, listed in its `pages` with the `example` type, and stored in
`docs/releases/<vendor>/<package>/<version>/<slug>/index.html`. They are written by hand: load the skills of the
vendor, of the language (see `/app:release:update`) and of the package when it exists (`<vendor>-<package>`, e.g.
`symfony-options-resolver`) first, read the commits of the change and the documentation.
Use `docs/releases/symfony/options-resolver/8.0/nested-options/index.html` as the template:

- Breadcrumb down to the slug, title without badge.
- The section `At a glance.` starts with a stat `Type`, whose value is the type of the change
  (`BC break`, `New feature`, `Improvement`, `Dependency` or `Other`), with the tone of its type
  (e.g. `<div class="stat tone-rose">` for a BC break), then the versions concerned, each with the tone of what it
  says: `blue` for a version adding something (e.g. `<code>setOptions()</code> added`, `Package created`), `orange` for
  `Old way deprecated`, `rose` for `Old way removed`.
  When the old way was deprecated first, a stat `Old way deprecated` gives its version, separate from the stat of the
  version adding the new way.
  After the stats, a `section-note` sums up the change and how to migrate (no subtitle under the title).
- Then these sections, in this order, the ranges of versions titled with the versions as inline code (no link):
  - `<h2><span><em>BC break</em></span></h2>` (for a BC break, with the tone of its type: `tone-rose`): one block of
    code per syntax (e.g. one for `setDefault()`, one for the fluent `default()`), the old line followed by the new
    one, each line preceded by a comment giving the versions where it works (the language skill gives its syntax),
    the old names in `data-removed`, the new ones in `data-added`.
    The old range starts at the version that introduced it (read in the changelog of the package) and ends at the
    last version where it can be used.
    **A deprecated code can still be used**: the deprecation only warns. The old range goes up to the last
    version before the removal (here `7.4`), deprecated versions included.
    When a syntax of the old way came later (e.g. a fluent method), give its version in its comment and in a paragraph
    just above its block of code. No separate section for the new way: these blocks already show it.
  - `<h2><span><em>Deprecated</em> <code>7.3 – 7.4</code></span></h2>` (`tone-orange`, the warning color), when the old
    way was deprecated before being removed: a paragraph saying that the old code still works but triggers a
    deprecation, then the deprecation message as `language-text` code.
  - `<h2><span><em>Migration</em></span></h2>` (`tone-teal`):
    what you saw happens when the code is not migrated (error or silent change of behavior, in a `callout` block),
    the code showing it, how it fails and how to find the code to migrate (the version adding the new way is
    already in `At a glance`).
  Skip the ranges that do not apply (e.g. no `Deprecated` section for a change removed without deprecation).
  For a new feature or an improvement, the sections show what it adds, one section per thing, titled with it
  (e.g. `<h2><span><em>Lazy</em> options</span></h2>`).
  In these sections, write one sentence per paragraph (`<p>`), also inside a `callout`.
  Never describe a behavior in a sentence (e.g. "An unknown option throws an exception"): show it with an example,
  its result or its exception in a comment (the language skill gives the format). When a section has several
  examples, give each one an `<h3>` title saying the case it shows, never the name of a method (e.g.
  `<h3>Option missing</h3>`), followed by one sentence explaining it when the code alone is not enough (e.g. a
  closure with a special argument). The main method of a section goes in its title, after the words, e.g.
  `<h2><span><em>Required</em> option <code>setRequired()</code></span></h2>`.
- Two neighbouring blocks never share a color: sections, stats (a stat without tone is white, like its neighbours
  without tone: give every stat a tone)... When two of them would, change the order or the tone.
- Tones of the sections: a type of section always has the same tone. Two sections of a page can share a tone, as
  long as they do not follow each other.
  `At a glance.` is `amber`, `BC break` `rose`, `Deprecated` `orange`, `Migration` `teal`, `The sources.` white.
  The sections showing a new feature or an improvement take, in their order on the page, `emerald`, `blue`, `indigo`,
  `violet`, `teal`, then again from `emerald`.
- The example page of the first version of a package shows what the package does, one section per concept, in this
  order when they apply (e.g. for `symfony/options-resolver`): `Minimal configuration` (`slate`, the package used
  without any configuration), `Required option` (`blue`), `Default value` (`emerald`), `Optional option` (`indigo`),
  `Allowed values` (`violet`). Each section shows the normal case first, then its errors and variants, each one with
  its `<h3>` title.
- Code: **only the code that changed**, a few lines: never a full implementation (no class, no unrelated options).
  Every block is complete: it creates everything it uses (e.g. `$resolver = new OptionsResolver();`) and calls no
  function it does not define, never relying on the code of another block.
  Old and new code side by side in the same block, one block per syntax (see `BC break`).
  Give the versions where a line works in a comment only when the block compares versions (e.g. the old and the new
  code of a BC break), never when the page is about a single version (e.g. a new feature).
  A comment showing the value of a variable (e.g. the result of a call) goes on its own line, just above the line
  that sets the variable, never below it nor at the end of the line.
  Write the code with the syntax of the minimum version of the language required by the package in the version shown
  (its `dependencies`), following the language skill (syntax of each version, how to write the code).
  Write code as `<pre class="code"><code class="language-<Pygments lexer>">` (the language skill gives the lexer;
  other text as `language-text`), inside a `code-block` whose `code-meta` (top right corner) holds the links to the
  documentation of what the block shows, then the version of the language whose syntax it uses (the language skill
  says which one):

  ```html
  <div class="code-block">
      <div class="code-meta"><a href="https://symfony.com/doc/8.0/components/options_resolver.html#nested-options" target="_blank" rel="noopener" title="Symfony 8.0 documentation: Nested Options" aria-label="Symfony 8.0 documentation: Nested Options"><svg class="icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 4C6.5 3 4.5 2.5 1.5 2.5v10c3 0 5 .5 6.5 1.5 1.5-1 3.5-1.5 6.5-1.5v-10c-3 0-5 .5-6.5 1.5zM8 4v10"/></svg></a><span>PHP 8.4</span></div>
      <pre class="code"><code class="language-php">...</code></pre>
  </div>
  ```

  One link per page of documentation, as precise as possible: with the anchor of the section that documents the code
  (the vendor skill says how to find it), one per version when the block compares versions. Its title is
  `<Project> <version> documentation: <title of the section>`, its icon the book above, whatever the site.
  After the links to the documentation, add a link to the declaration on GitHub of each method or class the block is
  about (those it marks, or the method that throws the exception it shows), at the tag of the version shown, with its
  PHPDoc (e.g. `.../blob/v2.1.0/src/.../OptionsResolverInterface.php#L44-L57`; the interface when it holds the PHPDoc;
  one per version when the block compares versions), titled
  `Declaration of <Class>::<method>() in <tag>`, its icon `<svg class="icon" viewBox="0 0 16 16" aria-hidden="true">
  <path d="M5.5 4 1.5 8l4 4M10.5 4l4 4-4 4"/></svg>`.
  A `language-text` block has no `code-meta`.
  Then run `bin/dev/highlight.py <page>`: it colors the code blocks
  with Pygments in the HTML itself (no JavaScript, no flicker on load), inside the `codebase-python` Docker image built
  by `bin/dev/start.py` (run it first). It rebuilds every block from its text, so it can be run again.
  Show what changed by listing the names (methods, classes, options...) on the `<code>` tag, separated by spaces:
  `data-removed="oldMethod"` (red) and `data-added="newMethod"` (green).
  Mark the strings the example is about (e.g. `data-added="'firstName'"` for an unknown or missing option, the given
  value of an option): `bin/dev/highlight.py` marks them in the code and in the comments showing a result or an
  exception message (`// The option "firstName" does not exist.`).
  When the paragraph above a block explains one part of its code (e.g. an argument, a variable), mark this part with
  `data-added`, name it in the paragraph and use it in the code (e.g. `data-added="$previousValue"` for "A second
  argument, `$previousValue`, receives...").
- Sources: documentation of the package (always with the anchor of the section when there is one), pull requests,
  commits, and the `links` of the change.

The release page links to its example pages from the row of the change (built by the script).

## Checks

1. Run `bin/dev/start.py` (it returns once the server is up, leave it running for the user) and check with `curl` that
   every page of `docs/` answers `200`.
2. Check with `curl -L` that the external links of the new or changed pages answer `200`.
3. Do not commit.
4. Summarize to the user: pages built or changed (listed by `bin/dev/site.py`), example pages written.
