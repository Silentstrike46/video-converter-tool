# Video Converter Tool - Design

This document serves as the original scoping, specification and design for the Video Converter Tool. This document may be later broken down into more concrete ADRs as time goes on, but shall serve as the basis on which the rest is built.

(TL;DR: Keeping ideas in head for years was not working out well, so written design spec it is.)



------

## 1. Purpose and context

A desktop wrapper around FFmpeg for art students, who are not developers / would prefer not running everything via a Command Line Interface (CLI). Many of the university projects required converting of video files between different formats before uploading, or condensing a folder of image files into a video file at a specific framerate. Not all the software the students used offer such conversions built in, and some students resorted to uploading the files to sketchy third-party sites to make it work.

This project is aimed to be an alternative that students can run locally to easily convert the files, without worrying about their personal information/work being leaked.

- **Local only.** Files are large, internet is often slow, and keeping students' private work off third-party sites is the reason the project exists. Nothing is uploaded anywhere; FFmpeg reads files where they are.
- **Platforms:** Windows and Linux. macOS support is not a focus for initial releases.
- **Licence:** GPLv3. Will become more of a concern later when we bundle FFmpeg in releases as we need to match their licensing, and different variations of FFmpeg come with different licensing requirements. See "Licensing and Distribution" chapter later.



------

## 2. Scope

- **v1.0:**
  - Convert a video between formats.
  - Images to video, with automatic pattern suggestion, and user-chosen frame rate.
  - Trim a video.
  - All three usable from the GUI and from a plain command-line tool.
- **v1.0 is clone-and-run.** It is finished when the features work from a clone of the repo, set up by following the README. Users need `uv` and `FFmpeg`; `Node/npm` only for frontend development (the built frontend is committed, see 7.3). There are no packaged releases in v1.
- **v1.1**: package release with FFmpeg bundled (section 12) so users do not need to install `uv` or local FFmpeg version.
- **Later features, as needed:** video to images, GIF export, user-customisable encoding settings, compress or resize, etc.
- **Optional visible console:** If the user would like to still see the console while it runs (e.g. to see explicitly what ffmpeg is doing), we can also consider making that an optional toggle if needed.



------

## 3. Architecture

```
          +-------------------+      +--------------------+
          |  GUI (pywebview)  |      |  CLI (vct <cmd>)   |
          |  TS frontend      |      |  argparse          |
          |  + Python bridge  |      |                    |
          +---------+---------+      +---------+----------+
                    |                          |
                    +------------+-------------+
                                 v
                    +------------------------+
                    |  core (all behaviour)  |
                    |  requests, features,   |
                    |  settings, errors      |
                    +-----------+------------+
                                v
                    +------------------------+
                    |  runner -> ffmpeg /    |
                    |  ffprobe subprocesses  |
                    +------------------------+
```

- **Rule:** all behaviour lives in `core`. The GUI and the CLI are thin layers over it. `core` never imports from `cli` or `gui`.
- **Core is synchronous.** Blocking functions with callbacks; the caller handles threads. The GUI bridge is the only place that creates threads.



------

## 4. Repo layout

```
src/vct/
  core/        # all behaviour
  cli/         # plain command-line tool (argparse subcommands)
  gui/         # pywebview bridge (Python)
    web/       # built frontend (generated, committed)
frontend/      # TypeScript source, Vite config, package.json
tests/
docs/
cli.py, utils/, run_cli.*   # legacy menu CLI, removed once GUI/new CLI is finalised
```

- **Names:** project `video-converter-tool`, import package `vct`, command `vct` (via `[project.scripts]`).
- **Legacy code:** the old menu CLI (`cli.py`, `utils/`, using `ffmpeg-python` and `easygui`) stays working and untouched until the new GUI and CLI cover all three features, so the app is usable at every step of the migration. It is then deleted in one follow-up PR.



------

## 5. Core

### 5.1 Talking to FFmpeg: hybrid

**TLDR**: `typed-ffmpeg` offers typing that reduces the amount of manual work we'd need to do for validation (as well as offers hints for when building out new functionality). However, its runners do not expose all the settings we'd need (e.g. it doesn't offer a hidden Windows console, and offers no progress parsing). So we'll opt for using `typed-ffmpeg` for building out the commands, but then rely on our own runners to give the exact execution control we need.

- **typed-ffmpeg builds commands** with `.compile(cmd=ffmpeg_path, overwrite_output=...)`, which returns a `list[str]`. Its typed, documented options make features and arguments discoverable without reading FFmpeg's man pages.
- **Our own small runner runs them** (ffmpeg and ffprobe). This allows us to have more control over how we run `ffmpeg` than what `typed-ffmpeg` offers (such as a hidden Windows console, progress parsing, graceful cancel, etc.)
  - Thus, **Never use** typed-ffmpeg's `.run()`, `.run_async()` or `ffmpeg.probe()` here.
- **Version tie:** `typed-ffmpeg` depends on `typed-ffmpeg-v9` (types for FFmpeg 9) and `ffmpeg-core`. Lock it in `uv.lock` and update deliberately, as it releases often.

**Runner requirements (each requires a test):**

1. **No pipe deadlock.** Read stdout and stderr concurrently (stderr on its own thread). Test: a job writing more than 64 KB to stderr completes.
2. **Process cleanup.** Cancel or shutdown sends `q` on stdin, then `terminate()`, waits with a timeout, then `kill()`, and closes the pipes. No orphaned `ffmpeg` after the GUI closes.
3. **Useful error.** Exit code, command and captured stderr tail.
4. **Hidden Windows console.** `creationflags=subprocess.CREATE_NO_WINDOW` on Windows only; the only platform branch we'd require. Otherwise on Windows, the user will get a terminal popup and likely panic.
5. **Binary lookup** only through the resolver (5.2), with a clear error when FFmpeg isn't found.
6. **Explicit overwrite policy.** Every command gets `-y` or `-n` (a required argument of our build helper). FFmpeg always gets its own stdin pipe, so it never prompts.
7. **Progress.** `-progress pipe:1` via `global_args(progress="pipe:1")`; parse the `key=value` blocks.
8. **Decoding.** Read pipes as bytes, decode with `errors="replace"`.
9. **Showing a command.** `subprocess.list2cmdline` on Windows, not typed-ffmpeg's POSIX `compile_line()`.
10. **ffprobe.** Arguments built by us, run through the runner, parsed with `json.loads`.

**Implementation notes:**

- Image-sequence frame rate is an input option (`input(..., extra_options={"framerate": 24})`), not an output option.
- **Keep v1 off filter graphs where possible.** Simple options (`-ss`, `-to`, `-vcodec`, `-crf`, ...) leave FFmpeg's automatic stream selection on, so video and audio are carried over without extra work. typed-ffmpeg always emits filters as a filter graph (`-filter_complex`), and once a filter graph is used, every stream must be mapped explicitly with `-map`. A forgotten audio map produces a silent video with no error.
  - Trim with `-ss`/`-to` as input options, not the `trim`/`atrim` filters (which would also need `setpts`/`asetpts` and explicit maps for both streams). typed-ffmpeg places both before `-i`, e.g. `ffmpeg -to 12 -ss 5 -i in.mov ...`.
  - The even-dimensions crop (5.4) is the one filter in v1, so it brings in explicit mapping. See the audio-mapping note there.



### 5.2 FFmpeg resolution

- **v1 uses a system FFmpeg** installed by the user. The app does not redistribute FFmpeg in v1. That'll come as a follow up once we figure out the licensing and distribution sides.
- **One resolver function** decides which binary to use. Nothing else calls `shutil.which`. Bundling later only changes the resolver and the packaging.
- **Startup check:** FFmpeg must exist, else `FFmpegNotFound` with clear install steps for Windows and Linux. If its major version isn't 9 (matching `typed-ffmpeg-v9`), **warn and continue**; real incompatibilities surface as `FFmpegFailed`. v1's commands are basic (libx264, AAC, `-ss`/`-to`, one crop filter, `-progress`), so older versions are expected to work but are untested.
- **The FFmpeg binary never goes in the repo.**



### 5.3 Job model

- **Shape of each feature:**
  - A typed request dataclass (`ConvertRequest`, `TrimRequest`, `MergeRequest`), validated on creation so bad input fails before FFmpeg starts.
  - `build_*_args(request) -> list[str]`.
  - The shared runner.
  - A `Result`.
- **Call shape:** e.g. `convert(request, on_progress=..., cancel=threading.Event()) -> Result`. Blocks until done; raises on failure.
- **Progress:** frozen dataclass `Progress(fraction: float | None, elapsed_s: float, eta_s: float | None, speed: float | None)`.
  - `fraction` is 0-1; `None` means the total is unknown (indeterminate bar, never a guess).
  - Totals: convert uses the ffprobe duration; trim uses `end - start`; merge uses the frame count. Each feature passes its total to the runner, which doesn't know which feature is running.
  - Updates arrive at FFmpeg's pace (about every 0.5 s). Core doesn't throttle; the bridge may.
  - No "done" update: success is the return value, failure is an exception.
- **Errors:** base `VctError` with `.message` (plain English for students) and optional `.details`.
  - `FFmpegNotFound`
  - `InvalidRequest`: checked before FFmpeg runs (missing input, missing output folder, fps <= 0, trim start >= end, no matching images, missing frames, output path equal to input path, ...).
  - `OutputExists`: output exists and `overwrite=False`. Core checks before starting; the GUI asks "Overwrite?" and retries with `overwrite=True`. Commands still pass `-n` as a safety net.
  - `JobCancelled`: raised, not returned.
  - `FFmpegFailed`: `.returncode`, `.command`, `.stderr_tail` (last ~20 lines).
- **Partial outputs:** FFmpeg writes `out.mp4.part`, renamed on success, deleted on cancel or failure, so an existing file being overwritten survives a failed job. The container format is given explicitly (`f=`) because FFmpeg can't infer it from `.part`.
- **Concurrency:** one job at a time in v1.



### 5.4 Features

- **Encoding defaults (all features):** H.264 (`libx264`, `crf 20`, `yuv420p`), AAC audio, `+faststart` for mp4/mov. Guaranteeing playback on an instructor's PC matters more than speed or size. No user-customisable settings in v1.
- **Odd dimensions (all features):** `crop=trunc(iw/2)*2:trunc(ih/2)*2`, because `yuv420p` needs even sizes. No-op for even sources. The only filter in v1. Later: revisit crop vs pad vs scale.
  - **Audio mapping gotcha:** with the crop in a filter graph, typed-ffmpeg compiles `-map [s0] -map 0:a` (checked with typed-ffmpeg 4.6.2). `-map 0:a` **fails when the input has no audio track** ("matches no streams"), which is common for renders and screen recordings. Map audio only when the ffprobe result (already fetched for the duration) reports an audio stream. The alternative, passing the crop as a plain `-vf` option through `extra_options`, keeps automatic stream selection but bypasses typed-ffmpeg's filter API.
- **Convert:** always re-encodes. Output formats mp4, mov, mkv. Later possibility: stream copy when codecs already suit the target.
- **Trim:** precise only (re-encode at the exact times). Times accepted as `HH:MM:SS.mmm`, `MM:SS` or plain seconds.
- **Images to video (merge):**
  - The user picks **one image** of the sequence; core finds the siblings whose names share its shape (`shotA_0001.png` -> `shotA_%04d.png`). This avoids guessing when a folder holds several sequences.
  - Prediction (#4) returns pattern + first frame number + frame count. `start_number` is passed as `-start_number`, since FFmpeg only searches 0-4 for the first frame by default.
  - Frame rate 24 by default; positive; fractional allowed (e.g. 23.976). **Must** be configurable by the user at run-time.
  - Image types: png, jpg/jpeg, tif/tiff, webp, bmp; one type per sequence.
  - Missing frames: core checks the sequence is complete before running and raises `InvalidRequest` naming the gaps (FFmpeg would otherwise stop quietly at the gap).
  - No audio. PNG transparency becomes black. Mixed image sizes are left to `FFmpegFailed`.



### 5.5 Settings

| Setting                          | v1 default                                                   | Notes                                                        |
| -------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| FFmpeg source                    | System FFmpeg                                                | Read by the resolver. The bundled/system choice arrives with bundling. |
| Output folder                    | Same folder as the input                                     | Or a fixed folder. Selectable.                               |
| Output file name                 | Input name + suffix (`_converted`, `_trimmed`); the pattern prefix for merge | Editable before starting.                                    |
| Last-used folder per file dialog | Remembered                                                   | An on/off switch is deferred to the distribution work (shared-PC privacy). |

- **Output must never equal input** (`InvalidRequest`).

- **Storage:** TOML, read with `tomllib`, written with `tomli-w`. Missing or broken file -> defaults.

- **Ownership:** core owns the `Settings` dataclass, load/save and output naming.

- **Location, via one `settings_path()` resolver:** next to the executable if writable (for a future AppImage, next to the `.AppImage` file via `$APPIMAGE`); otherwise the platform folder via `platformdirs` (Linux `~/.config/vct/`, Windows `%APPDATA%\vct\`). Tests pass an explicit path; development uses a git-ignored file in the repo.



------

## 6. Command-line tool

- argparse subcommands: `vct convert`, `vct trim`, `vct merge`, each a thin wrapper over core, added in the same PR as its feature.
- The legacy menu CLI coexists until we finalise the GUI and new CLI approach, and can be removed after. The original CLI used a menu-based CLI, which was a middle ground between normal CLI and GUI - worse for developers who would want to run things exactly as they want to, and worse for art students than a GUI. Once the GUI is done, we can opt to remove the legacy menu CLI in favour of a standard CLI tool that can be interacted with by other scripts.



------

## 7. GUI

**NOTE**: This is my initial attempt at a native application while still using webdev tooling - a middle ground between a webapp and a native application. If we run into issues on this, we can definitely look at changing the design.

Using an actual frontend stack and compiling down to static files is definitely overkill for a project of this size (compared to just hand-writing HTML/JS/CSS files). But for the sake of expandability and reducing errors, I would like the frontend tooling + Typescript for my own sanity.



### 7.1 Framework

- **pywebview** (GTK backend on Linux, Edge WebView2 on Windows) with our own frontend. JS calls Python through `js_api`.
- **File selection** is always the native dialog (`create_file_dialog`), which returns real paths. Nothing is uploaded or copied.
- **Serving:** the built `index.html` is loaded by plain path, so pywebview serves it from its built-in static server bound to `127.0.0.1`. That server only serves our frontend folder. `file://` is avoided (CSS failed to load in an earlier prototype).
- **Other findings from an earlier prototype:** start with `webview.start(gui="gtk")` explicitly on Linux (otherwise it tries Qt first, noisily). Keep the window reference in a private attribute (`_window`), because public attributes of the API object are exposed to JS.
- **Linux dependency:** `pygobject; sys_platform == "linux"`, built against the system `webkit2gtk-4.1`.



### 7.2 Frontend stack

- **TypeScript + Vite**, no framework. Source in `frontend/`, built into `src/vct/gui/web/` with `base: "./"`.
- **Node 26 LTS**, pinned in `.nvmrc` and `engines`; **npm**.
- **Checks:** `tsc --noEmit`; ESLint with `typescript-eslint` type-aware rules (notably `no-floating-promises` and `no-misused-promises`, since every bridge call returns a Promise); Prettier with `eslint-config-prettier`.
- **TS config:** use Vite's split `tsconfig.app.json` / `tsconfig.node.json` (including `vite.config.ts` without Node types breaks `tsc`).
- **Development:** point pywebview at the Vite dev server (`http://localhost:5173`) for hot reload; the bridge works there too.



### 7.3 Committed build output

The built frontend is committed, so a clone runs without Node/npm. Guards:

1. CI runs `npm ci && npm run build` and fails on `git diff --exit-code src/vct/gui/web/`.
2. A prek hook rebuilds when `frontend/` files are staged.
3. Vite builds with unhashed file names and no minification, for stable, readable diffs.
4. `.gitattributes` marks `src/vct/gui/web/**` as `linguist-generated`.
5. ESLint and Prettier ignore the output folder.

On merge conflicts in the output, rebuild rather than hand-merge. Guard 1 assumes the build is deterministic (pinned Node + lockfile); verify when scaffolding.



### 7.4 Python <-> page boundary

- **Page -> Python:** `window.pywebview.api.*` methods on one bridge class.
- **Python -> page:** pywebview's shared state. Python sets `window.state.job = {...}`; the page listens for `change` events on `pywebview.state`. Only Python writes `job`.
- **`job` shape:** a TS interface mirroring the bridge's view of a job, roughly `{ status: "running" | "done" | "failed" | "cancelled", progress: { fraction, elapsed_s, eta_s, speed }, output_path?, message?, details? }`, with `progress` matching core's `Progress`.
- The boundary is kept small and documented in one place.



### 7.5 Layout and screens

- **Sidebar navigation:** Convert, Images to video, Trim, then Settings. Each tool is its own `<section>`.
- **Job behaviour (all tools):** while running, the form locks and shows a progress bar and Cancel; switching tools is blocked. Success: "Done" with Open file and Open folder. Failure: a short message plus a collapsible details section with the end of FFmpeg's stderr. An existing output prompts "Overwrite?".
- **Shared controls:** output name and output folder (default the input's folder, "Change..." button).
- **Convert:** input video (length shown, from ffprobe), output format (mp4/mov/mkv, default mp4), output name (default `<input>_converted`), output folder, Convert.
- **Trim:** input video, Start and End text fields in core's formats. The video's length is shown and End is pre-filled with it; invalid input is flagged at the field.
- **Images to video:** pick one image; then a plain-words summary such as "shotA_####.png - frames 1001 to 1100 (100 frames) - 4.2 s at 24 fps" (never FFmpeg's `%04d`), frame rate (default 24), output name (default the pattern prefix), and a collapsed "Edit pattern" section. Missing frames are listed before anything runs.
- **Settings:** the FFmpeg found and its version (or a clear "not found" with install steps), default output folder, and the settings file's location (read-only).



------

## 8. Tooling

- **Python 3.14** (`requires-python = ">=3.14"`)
- **uv** for environments and locking.
- **Ruff** for linting and formatting, with the `S` (security) rules. The subprocess rules will fire in the runner by design. Suppressions should be avoided as far as possible (see [CONTRIBUTING.md](../CONTRIBUTING.md))
- **basedpyright** for type checking.
- **prek** (`.pre-commit-config.yaml`):
  - On commit: `ruff check --fix`, `ruff format`, `basedpyright` (local hook via `uv run`), frontend `typecheck`/`lint`/`format` via npm scripts (local hooks, so versions come from `package-lock.json`), the frontend rebuild check (ref section 7.3), basic file checks (whitespace, final newline, YAML/TOML syntax, merge markers, files over ~1 MB), and `uv lock --check`.
  - On push: `pytest`, until CI covers it.
- **Check scope during the migration:** Ruff, basedpyright and their hooks cover only `src/` and `tests/`, with a config comment explaining why. The legacy code is frozen and scheduled for deletion; the limiter is removed in the same PR, after which the whole project is checked.
- **Line endings:** `.gitattributes` with `* text=auto eol=lf`.



------

## 9. Testing

**TDD: each feature starts with its requirements as tests.**

| Layer               | What                                                         | How                                                          | Needs FFmpeg |
| ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ |
| 1. Command building | Each `build_*_args` returns the exact expected list (e.g. `-framerate` before `-i`; every command has `-y` or `-n`) | Assertions on the list                                       | No           |
| 2. Pure logic       | Progress parsing, pattern prediction, resolver, version check, settings | pytest, `tmp_path`, fake `-version` output                   | No           |
| 3. Runner           | Runner requirements 1-10                                     | A fake FFmpeg script run as a real subprocess (no `Popen` mocks) | No           |
| 4. Integration      | Each feature end to end, outputs checked with ffprobe; includes an input with no audio track and an input with odd dimensions | Tiny clips generated with `testsrc`; no media in the repo    | Yes          |
| 5. GUI bridge       | The bridge class: calls core, forwards progress, maps errors to messages | Called directly with a fake window                           | No           |
| 6. Frontend         | TS logic worth testing                                       | Open question (section 13) TODO                              | No           |

- Layer 4 is marked `@pytest.mark.ffmpeg` and skipped when FFmpeg is missing.
- `pytest-cov` for reports; no required percentage.
- No automated real-window GUI tests in v1; a manual smoke checklist on Windows and Linux instead.



------

## 10. CI (GitHub Actions)

TLDR: always ensure lints and tests pass before anything is merged into `main`.

- **`ci.yml` jobs:**
  - **lint** (Ubuntu): `prek run --all-files`.
  - **test** (Ubuntu and Windows): `uv sync`, install FFmpeg (see section 13), full pytest suite including `ffmpeg`-marked tests.
  - **frontend** (Ubuntu): `npm ci`, typecheck, lint, format check, build, and the stale-build diff check.
- **Triggers:** `pull_request` (opened, synchronize, reopened, ready_for_review; drafts skipped), `push` to `main`, `workflow_dispatch`. A `concurrency` group with `cancel-in-progress`. No CI on feature-branch pushes.
- **Once stable:** make the jobs required checks in the "Protect Main" ruleset and drop the pre-push pytest hook.
- **To sort out:** GTK/GObject dev packages for PyGObject on the Linux runner; whether layer 5 tests need a display.



------

## 11. Repo process

GitHub flow with squash merges and `v*` release tags. Branch naming, commit and PR rules, repository rulesets and the release process are in [CONTRIBUTING.md](../CONTRIBUTING.md).



------

## 12. Licensing and Distribution

NOTE: Up for discussion and can change as needed. This is the first version proposed.

- **Project licence:** GPLv3 (add the licence field to `pyproject.toml`).
- **v1 redistributes nothing of FFmpeg's.** When bundling is picked up:
  - **Build:** BtbN `gpl` variant, because `libx264` is GPL-only (the `lgpl` variant lacks it). `nonfree` is not redistributable. Static vs shared decided by real download sizes.
  - **Source obligation:** "corresponding source" covers FFmpeg and every library statically linked into the build. Options:
    - (A) BtbN prebuilt + gather each dependency's source at BtbN's pinned commits
    - **(B, most likely)** build FFmpeg in our own CI with BtbN's Docker scripts and archive every downloaded source, so correspondence holds by construction
    - (C) our own minimal build (FFmpeg + libx264 + dav1d).
  - Read ffmpeg.org/legal.html and GPLv3 section 6 first.
- **Distribution (later):** portable-only, no installers (e.g. a zip of a PyInstaller folder build for Windows; an AppImage or tarball for Linux). Open questions: WebView2 on locked-down PCs, WebKitGTK on Linux, SmartScreen and signing, antivirus false positives, FUSE for AppImage, FAT/exFAT flash drives, shared-PC privacy (incl. the "remember folders" switch), and third-party licence notices for bundled Python packages.
  - If portable-only becomes an issue, we can look into installers; but having this able to sit on a flashdrive, ready to use, would be a big win.



------

## 13. Open questions and risks

- **Windows is untested.** WebView2 loading the Vite build, `window.state` updates, the native dialog, hidden consoles. Will need to be tested on a real Windows machine once a MVP of the GUI is done.
- **pywebview threading:** `js_api` calls are believed to run off the GUI thread; verify.
- **`window.state`** was read in source (pywebview 6.2.1), not yet run.
- **Legacy CLI on Python 3.14:** `ffmpeg-python` 0.2.0 and `easygui` on 3.14 are unverified, but can be tested. Worst case I'd argue we drop the legacy CLI as opposed to not running Python 3.14, but hopefully we can do both.
- **FFmpeg in CI:** how the runners get FFmpeg 9 without us redistributing it (e.g. download BtbN's month-end build directly with a pinned SHA-256, rather than re-hosting it), and whether to add a job on Ubuntu's packaged (older) FFmpeg to exercise the version warning.
- **Custom FFmpeg path:** whether v1's Settings lets the user pick `ffmpeg.exe` directly, so Windows users can avoid editing PATH.
- **Frontend tests (layer 6):** whether to add a test runner (e.g. Vitest) and for what.
- **Build determinism** for the committed-output check.



------

## 14. Delivery plan for v1.0

One issue and one squash-merged PR per item, vertical slices after the scaffolding.

0. **Design doc** (this document).
1. **Tooling chore:** Python 3.14; empty `src/vct/` alongside the untouched legacy CLI; drop moviepy, pyqt6, pyside6, black, flake8, bandit (and the unused `moviepy` import); keep `ffmpeg-python` and `easygui`; add the new dependencies and tools; prek; delete the PySide6 files; remove the LFS rules and `tox.ini`; licence field; `eol=lf`. Success check: the legacy CLI still runs.
2. **CI** on Ubuntu and Windows.
3. **Core foundation:** resolver and version check, runner, progress parsing, errors, settings.
4. **GUI scaffold:** `frontend/` and its tooling and CI job; bridge, sidebar, `window.state`, Settings screen; first Windows check.
5. **Convert:** core + `vct convert` + screen.
6. **Trim:** core + `vct trim` + screen.
7. **Images to video:** core + pattern prediction (#4) + `vct merge` + screen.
8. **Retire the legacy menu CLI** and remove the check limiter.
9. **README rewrite**, then tag `v1.0.0`.



------

## 15. Alternatives considered

- **GUI:** PySide6/PyQt6 (dropped); Streamlit/Dash (browser upload widgets defeat the point of 'local-only'); NiceGUI native mode (fallback if pywebview fails).
- **FFmpeg wrapper:** `ffmpeg-python` (unmaintained since 2019); `typed-ffmpeg`'s own runner (too basic); raw subprocess only (loses typed options and/or need to build out all types by hand while reading the FFmpeg documentation, re-doing the work that `typed-ffmpeg` already did).
- **Frontend:** plain JS with Biome (I want the prek hooks to help with code quality, however, Biome's official prek hook needs Node anyway. Either don't use Node, or if we need node, let's rather use standard tooling); a framework (overkill for such a small UI); build output git-ignored (would force Node on every clone in a clone-and-run v1; not an issue when we have full releases, but during the initial v1, I can't expect students to need to install Node too).
- **Trim UI:** an HTML `<video>` preview (depends on the webview's codecs; mov/ProRes/mkv often won't play). Not needed for v1, and can be considered in follow up.
- **Merge input:** picking a folder (ambiguous with several sequences in the same directory); multi-selecting files (awkward at 1000+ frames).
- **FFmpeg in v1:** bundling (deferred: too much effort for v1).
- **Migration:** retiring the menu CLI first (leaves no working tool mid-migration); rewiring it to the new core (thus doing work on code being deleted).