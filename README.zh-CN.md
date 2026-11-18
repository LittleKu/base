# Chromium base

[English](README.md)

使用 GN 和 Ninja，在浏览器工程之外独立构建 Chromium 的 `base`。本仓库包含独立构建入口、固定版本的依赖配置和示例。

源码和依赖固定为 **Chromium 158.0.8127.37**，对应提交
[`b8c2be851f62f6a394ec57955d7f31335d7cb6d4`](https://chromium.googlesource.com/chromium/src/+/b8c2be851f62f6a394ec57955d7f31335d7cb6d4)。
默认构建配置使用 Chromium 固定版本的 Clang、Rust 和 C++ 标准库。不同 Chromium 版本之间不保证二进制 ABI 稳定。

## 环境要求

安装 Git 和 Python 3。各平台的工具要求与固定的 Chromium 版本保持一致：

| 平台 | 工具 |
| --- | --- |
| Windows x64 | Visual Studio 2026，安装“使用 C++ 的桌面开发”、MFC/ATL，以及 Windows 11 SDK 10.0.28000.2270 或 28000 SDK 的后续维护版本。参见[固定版本的上游要求](https://chromium.googlesource.com/chromium/src/+/b8c2be851f62f6a394ec57955d7f31335d7cb6d4/docs/windows_build_instructions.md)。 |
| Linux x64 | Git、Python 3 和 `pkg-config`。同步依赖时会下载固定版本的 Linux sysroot 和编译工具链。 |
| macOS | Xcode 及其 macOS SDK，使用 `xcode-select` 选择。固定的上游工具链在 Intel 上使用 Xcode 26.6 / SDK 26.5，在 Apple Silicon 上使用 SDK 27.0；参见[上游 SDK 配置](https://chromium.googlesource.com/chromium/src/+/b8c2be851f62f6a394ec57955d7f31335d7cb6d4/build/config/mac/mac_sdk.gni)。 |

## 获取源码和依赖

在同一个工作区中，将 `depot_tools` 和 `src` 放在同一级目录。先克隆最新的 depot_tools 仓库，再切换到 Chromium 158 的 `DEPS` 固定的提交：`b86fc981b72ab966f8260f73b4eca600b3b12677`。
调用其中的工具前，设置 `DEPOT_TOOLS_UPDATE=0`，防止自动更新。

Windows（`cmd.exe`）：

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

将这些命令保存为 `.bat` 文件时，请把 `%I` 替换为 `%%I`。

如果你的 depot_tools 安装使用 `depot_tools.bat` 环境脚本，请在运行 gclient 前，在同一个 shell 中调用该脚本，然后确保工作区内固定版本的 `depot_tools` 位于 `PATH` 最前面。脚本路径使用你实际的安装路径。

Linux 和 macOS：

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

gsutil 命令会在 gclient 开始并行下载依赖前初始化下载器，避免首次安装时发生竞争。

依赖同步前的钩子会使用 `DEPS` 中的提交版本运行 `scripts/sync_chromium.py`。脚本从同一个 Chromium 提交导入 `base`、`build`、`buildtools`、`testing`、`third_party` 和 `tools`，排除 `third_party/blink`。`chrome` 下只导入用于构建元数据的 `chrome/VERSION`。本仓库还提供 `base/version_info` 所需的 Chromium 品牌元数据。
随后，gclient 获取所需依赖。导入的源码由 `.chromium.git` 单独跟踪，本项目的根目录文件和 Git 历史会保留。同步时不要使用 `--noprehooks`。

可通过 `GIT_CACHE_PATH` 或 `git config cache.cachepath` 复用已有的 Chromium Git 缓存。在此工作副本使用期间，请始终保留其引用的缓存。项目源码、工具链和构建产物都位于工作区内；构建产物写入 `src/out`。

如果已有工作副本由旧版拆分仓库的 DEPS 创建，请改用新目录。源码同步脚本会拒绝覆盖那些源码目录，也会拒绝替换已经修改的导入源码；变更固定提交版本前，请先保留自己的修改。

## 构建和运行

在固定版本的 depot_tools 环境仍然生效的情况下，从 `src` 目录执行以下命令。这些命令会为宿主 CPU 构建 Debug 静态库配置。`default` 包含原有日志示例和冒烟测试。`use_siso=false` 用于选择 Ninja。

独立提取使用 `build_with_chromium=true`，保留 Chromium 158 的 base 所需的上游集成目标，包括 `libperfetto`。`.gn` 文件设置了 `root_patterns = [ "//:default" ]`，将生成的构建图限制为 `default` 及其传递依赖，其中包括 base、示例和冒烟测试。

Windows（`cmd.exe`）：

```bat
buildtools\win\gn.exe gen out\Debug --args="is_debug=true use_siso=false use_remoteexec=false"
third_party\ninja\ninja.exe -C out\Debug default
out\Debug\base_smoke_test.exe
start /wait "" out\Debug\example.exe
```

Linux：

```sh
buildtools/linux64/gn gen out/Debug --args='is_debug=true use_siso=false use_remoteexec=false'
third_party/ninja/ninja -C out/Debug default
out/Debug/base_smoke_test
out/Debug/example
```

macOS：

```sh
buildtools/mac/gn gen out/Debug --args='is_debug=true use_siso=false use_remoteexec=false'
third_party/ninja/ninja -C out/Debug default
out/Debug/base_smoke_test
out/Debug/example
```

如果版本元数据、临时文件 I/O、JSON 解析和序列化、ThreadPool/RunLoop 回调或关闭时的任务完成检查失败，冒烟测试会以错误退出。成功运行会输出 `base smoke test passed`。原有示例会写入一条日志；在 Windows 上，输出文件为 `out/Debug/example.log`。

## 验证和更新

[CI 工作流](.github/workflows/build.yml) 配置了在 Windows x64、Linux x64 和 macOS Intel 上构建并运行两个目标。存在工作流文件不代表运行已经通过，请查看所用提交版本的工作流结果。Apple Silicon、Release/component 构建和完整的上游 `base_unittests` 测试套件不在此工作流的覆盖范围内。

GN 检查沿用固定上游版本在严格依赖迁移期间保留的例外项。

如需生成额外的测试目标，可在 `gn gen` 时覆盖根目标匹配规则，例如使用 `--root-pattern=//:default --root-pattern=//base:base_unittests`。这些参数会替换 `.gn` 中的默认值。额外目标可能需要提取范围之外的源码或依赖，必须单独验证构建。

Windows CI 会安装 SDK 10.0.28000.2526，因为所选 VS 2026 runner 镜像目前自带的是 SDK 26100。安装程序的哈希值固定为 [Microsoft 软件包清单](https://github.com/microsoft/winget-pkgs/blob/master/manifests/m/Microsoft/WindowsSDK/10/0/28000/10.0.28000.2526/Microsoft.WindowsSDK.10.0.28000.installer.yaml)中记录的值。

更新 Chromium 时，应根据同一份上游 `DEPS` 同步更新源码提交、depot_tools 固定版本以及第三方依赖和工具链的固定版本，检查独立构建的覆盖配置，并重新执行三个平台的构建和冒烟测试。不要只更新 `base` 的源码提交。

源码同步脚本提供独立的本地自测：

```text
python3 scripts/sync_chromium_test.py
```
