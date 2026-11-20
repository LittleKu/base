# Chromium base

[简体中文](README.zh-CN.md)

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

For a `.bat` file, replace `%I` with `%%I`.

Linux / macOS:

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
