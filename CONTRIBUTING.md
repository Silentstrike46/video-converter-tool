# Contributing

How work gets into this repo: issues, branches, commits, pull requests and releases. For what is being built and why, see [docs/design.md](docs/design.md).



## Workflow (GitHub flow)

1. **Start from an issue.** Every change has a GitHub issue describing what and why.
   Since we do not have a ticket-tracking board (Jira, ClickUp, etc.), treat these issues as your ticket. As such, each issue should have sufficient information on:
   - the context
   - why the change is needed
   - what needs to change
   - acceptance criteria
2. **Branch off `main`.** `main` is the only long-lived branch.
3. **Open a pull request into `main`.** Keep it as a draft while work is in progress; CI only runs once it is marked ready for review.
4. **Squash merge.** The branch is deleted automatically after merging.



## Branch names

**Two options:**

1. [Conventional Branches](https://github.com/conventional-branch/conventional-branch/) style with issue number: `<type>/<issue#>-<slug>`.
   - For example, `chore/6-add-design-documentation`.
2. The shorter `<issue#>-<slug>` (GitHub's "create a branch" default) is also accepted.
   - For example, `6-add-design-documentation`.

Either is fine, so long as it includes the issue number, and is still both concise yet descriptive.

Some common types for the Conventional Branches approach:

| Type | For |
|---|---|
| `feat` | New behaviour |
| `fix` | Bug fixes |
| `chore` | Tooling, dependencies, docs, housekeeping |
| `refactor` | Restructuring without behaviour changes |



## Commit messages

Every commit, including the squash commit, follows the **50/72 rule:**

- **Subject:** at most 50 characters, imperative mood ("Add", "Fix", "Remove", not "Added" or "Fixes"), no trailing full stop.
- **One blank line** between the subject and the body.
- **Body:** wrap lines at 72 characters. Explain what changed and why, not how.

If [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) ([Cheatsheet](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13)) is used, the type prefix counts towards the 50 characters; e.g. `feat: add convert screen (#12)`.

Ultimately, keep things clean and concise (while still having sufficient information), and use your judgement.



## Pull requests

- **The PR title becomes the squash commit subject.** GitHub appends ` (#<PR number>)`, which counts towards the 50 characters, so keep PR titles to about 44 characters prior to this.
- **The PR description by default becomes the squash commit body. Before merging, condense it in the merge dialog and wrap it at 72 characters.**
- Link the issue in the description (e.g. `Closes #6`).
- CI must pass before merging.



## Code quality

- **TDD.** Write the tests for a requirement before the implementation (see the testing layers in [docs/design.md](docs/design.md)).
- **Hooks.** Install the prek hooks after cloning (`prek install`) and never bypass them (don't use `git commit --no-verify`).
- **No silenced warnings by default.** Fix the underlying problem rather than adding `# noqa`, `# type: ignore`, `eslint-disable` or similar, or loosening the lint config. When a suppression is genuinely right (a known false positive, a missing third-party stub), keep it as narrow as possible: the specific rule code, on a single line, with a comment explaining why.
- **Generated frontend output** (`src/vct/gui/web/`) is never edited by hand. Change `frontend/` and rebuild. On merge conflicts in the output, rebuild instead of resolving by hand.



## Repository rules

- **"Protect Main" ruleset:** no deletion or force pushes, linear history, changes only through pull requests (0 approvals required while we're short on people), squash merges only.
- **"Release tags" ruleset** on `v*`: tags can't be deleted, moved or force-pushed.



## Releases

Releases are tags named `v<major>.<minor>.<patch>` (e.g. `v1.0.0`) on `main`.



## Editor-specific Notes

Some helpful editor-specific notes (mostly for my own reference so I don't re-discover the solution to the same issue over and over):

- **basedpyright on Code-OSS**: Use Open VSX `detachhead.basedpyright` extension and `"python.languageServer": "None"`.

