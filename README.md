# Chromium base

[简体中文](README.zh-CN.md)

Build Chromium's `base` outside the browser with GN and Ninja. This repository
contains the standalone build entry points, dependency pins, and examples.

The source and dependencies are pinned to **Chromium 158.0.8127.37**, commit
[`b8c2be851f62f6a394ec57955d7f31335d7cb6d4`](https://chromium.googlesource.com/chromium/src/+/b8c2be851f62f6a394ec57955d7f31335d7cb6d4).
The default build configuration uses Chromium's pinned Clang, Rust, and C++
standard library. It does not provide a stable binary ABI across Chromium updates.

## Prerequisites

Install Git and Python 3. Platform tools follow the pinned Chromium revision:

| Platform | Tools |
| --- | --- |
| Windows x64 | Visual Studio 2026 with Desktop development with C++, MFC/ATL, and Windows 11 SDK 10.0.28000.2270 or a later servicing release of the 28000 SDK. See the [pinned upstream requirements](https://chromium.googlesource.com/chromium/src/+/b8c2be851f62f6a394ec57955d7f31335d7cb6d4/docs/windows_build_instructions.md). |
| Linux x64 | Git, Python 3, and `pkg-config`. Dependency sync downloads the pinned Linux sysroot and compiler toolchain. |
| macOS | Xcode and its macOS SDK, selected with `xcode-select`. The pinned upstream toolchain uses Xcode 26.6 / SDK 26.5 on Intel and SDK 27.0 on Apple Silicon; see [upstream SDK settings](https://chromium.googlesource.com/chromium/src/+/b8c2be851f62f6a394ec57955d7f31335d7cb6d4/build/config/mac/mac_sdk.gni). |

## Checkout and dependencies

Use one workspace containing sibling `depot_tools` and `src` directories. First
clone the latest depot_tools repository, then check out the revision pinned by
Chromium 158's `DEPS`: `b86fc981b72ab966f8260f73b4eca600b3b12677`.
Set `DEPOT_TOOLS_UPDATE=0` before invoking its tools to prevent automatic updates.

Windows (`cmd.exe`):

```bat
mkdir chromium-base
cd chromium-base
mkdir work\temp work\vpython
set "TEMP=%CD%\work\temp"
set "TMP=%TEMP%"
set "TMPDIR=%TEMP%"
set "VPYTHON_VIRTUALENV_ROOT=%CD%\work\vpython"
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git depot_tools
git -C depot_tools checkout b86fc981b72ab966f8260f73b4eca600b3b12677
set DEPOT_TOOLS_UPDATE=0
set DEPOT_TOOLS_WIN_TOOLCHAIN=0
set "PATH=%CD%\depot_tools;%PATH%"
if not defined GIT_CACHE_PATH for /f "delims=" %I in ('git config --path --get cache.cachepath') do set "GIT_CACHE_PATH=%I"
if not defined GIT_CACHE_PATH set "GIT_CACHE_PATH=%CD%\git_cache"
set "CIPD_CACHE_DIR=%CD%\cipd_cache"
call gclient config --unmanaged --name=src --cache-dir "%GIT_CACHE_PATH%" https://github.com/LittleKu/base.git || exit /b 1
call vpython3 depot_tools\gsutil.py version || exit /b 1
call gclient sync --no-history || exit /b 1
cd src
```

When saving these commands in a `.bat` file, replace `%I` with `%%I`.

If your depot_tools installation uses a `depot_tools.bat` environment script,
call it in the same shell before running gclient, then ensure that the pinned
workspace's `depot_tools` is first on `PATH`. Use your installation's path.

Linux and macOS:

```sh
mkdir chromium-base
cd chromium-base
mkdir -p work/temp work/vpython
export TEMP="$PWD/work/temp"
export TMP="$TEMP"
export TMPDIR="$TEMP"
export VPYTHON_VIRTUALENV_ROOT="$PWD/work/vpython"
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git depot_tools
git -C depot_tools checkout b86fc981b72ab966f8260f73b4eca600b3b12677
export DEPOT_TOOLS_UPDATE=0
export PATH="$PWD/depot_tools:$PATH"
if [ -z "${GIT_CACHE_PATH:-}" ]; then
  GIT_CACHE_PATH="$(git config --path --get cache.cachepath || true)"
fi
export GIT_CACHE_PATH="${GIT_CACHE_PATH:-$PWD/git_cache}"
export CIPD_CACHE_DIR="$PWD/cipd_cache"
gclient config --unmanaged --name=src --cache-dir "$GIT_CACHE_PATH" https://github.com/LittleKu/base.git
vpython3 depot_tools/gsutil.py version
gclient sync --no-history
cd src
```

The gsutil command initializes the downloader before gclient starts parallel
dependency downloads, avoiding contention during its first installation.

The pre-dependency hook runs `scripts/sync_chromium.py` with the revision in
`DEPS`. It imports `base`, `build`, `buildtools`, `testing`, `third_party`, and
`tools` from that single Chromium commit, excluding `third_party/blink`. The only
imported file under `chrome` is `chrome/VERSION`, used as build metadata. This
repository also carries Chromium's branding metadata for `base/version_info`.
Gclient then fetches the required dependencies. The imported source is tracked separately in
`.chromium.git`; this project's root files and Git history are retained. Do not use
`--noprehooks` when syncing.

An existing Chromium Git cache can be reused through `GIT_CACHE_PATH` or
`git config cache.cachepath`. Keep the referenced cache available for the lifetime
of the checkout. Project source, toolchains, and build output remain in the
workspace; build output is written under `src/out`.

For an existing checkout created by the older split-repository DEPS, use a new
directory. The source sync script refuses to overwrite those source directories.
It also refuses to replace modified imported source; preserve your changes before
changing the pinned revision.

## Build and run

Run these commands from `src` with the pinned depot_tools environment still active.
They build a Debug static configuration for the host CPU. `default` includes the
original logging example and the smoke test. `use_siso=false` selects Ninja.

The extraction uses `build_with_chromium=true` to retain the upstream integration
targets required by Chromium 158's base, including `libperfetto`. The `.gn` file
sets `root_patterns = [ "//:default" ]`, limiting the generated build graph to
`default` and its transitive dependencies, including base, the example, and the
smoke test.

Windows (`cmd.exe`):

```bat
buildtools\win\gn.exe gen out\Debug --args="is_debug=true use_siso=false use_remoteexec=false"
third_party\ninja\ninja.exe -C out\Debug default
out\Debug\base_smoke_test.exe
start /wait "" out\Debug\example.exe
```

Linux:

```sh
buildtools/linux64/gn gen out/Debug --args='is_debug=true use_siso=false use_remoteexec=false'
third_party/ninja/ninja -C out/Debug default
out/Debug/base_smoke_test
out/Debug/example
```

macOS:

```sh
buildtools/mac/gn gen out/Debug --args='is_debug=true use_siso=false use_remoteexec=false'
third_party/ninja/ninja -C out/Debug default
out/Debug/base_smoke_test
out/Debug/example
```

The smoke test exits with an error if version metadata, temporary-file I/O, JSON parsing and
serialization, ThreadPool/RunLoop replies, or shutdown task completion fail. A
successful run prints `base smoke test passed`. The original example writes a log
message; on Windows its output is `out/Debug/example.log`.

## Validation and updates

The [CI workflow](.github/workflows/build.yml) is configured to build and run both
targets on Windows x64, Linux x64, and macOS Intel. Its presence is not evidence
that a run passed; check the workflow results for the revision you use. Apple
Silicon, Release/component builds, and the full upstream `base_unittests` suite
are outside this workflow's coverage.

GN checks use the pinned upstream strict-dependency migration exceptions.

To request additional test targets, override the root patterns during `gn gen`,
for example with `--root-pattern=//:default --root-pattern=//base:base_unittests`.
These flags replace the `.gn` defaults. Additional targets may require sources
or dependencies outside the extracted set and need separate build validation.

Windows CI installs SDK 10.0.28000.2526 because the selected VS 2026 runner image
currently ships SDK 26100. The installer hash is pinned to the
[Microsoft package manifest](https://github.com/microsoft/winget-pkgs/blob/master/manifests/m/Microsoft/WindowsSDK/10/0/28000/10.0.28000.2526/Microsoft.WindowsSDK.10.0.28000.installer.yaml).

When updating Chromium, update the source revision, depot_tools pin, and
third-party/toolchain pins from the same upstream `DEPS`, review the standalone
overrides, and repeat the three-platform build and smoke tests. Do not update only
the `base` source pin.

The source-sync script has a separate local self-test:

```text
python3 scripts/sync_chromium_test.py
```
