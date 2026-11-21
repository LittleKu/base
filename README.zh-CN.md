# Chromium base

[English](README.md)

## 主要功能

在独立 C++ 项目中使用 Chromium 的 `base` 基础库，提供日志、文件、字符串、JSON、时间、线程池和异步任务等能力。源码版本与依赖由 [DEPS](DEPS) 统一管理。

- 自动同步指定版本的 Chromium 源码和依赖，默认静态构建 `base`。
- 提供 GN / Ninja 构建配置，可生成 Visual Studio 工程。
- 提供 [example](examples/example.cc) 日志示例和 [base_smoke_test](examples/base_smoke_test.cc) 冒烟测试，后者覆盖文件、JSON 和线程池等功能。

## 使用方法

### Windows

#### 准备工作

以下步骤面向 Windows x64，使用本机安装的 Visual Studio 工具链。

1. 安装 [Git for Windows](https://git-scm.com/install/windows)，确保命令行可以运行 `git`。
2. 安装 [Visual Studio 2026](https://visualstudio.microsoft.com/downloads/)，选择“使用 C++ 的桌面开发”，并安装 x64/x86 生成工具和对应的 **C++ ATL** 组件。为加载下文 GN 生成的 v143 工程，同时安装 **MSVC v143 - VS 2022 C++ x64/x86 生成工具**。
3. 安装 [Windows SDK 10.0.28000.2526](https://learn.microsoft.com/en-us/windows/apps/windows-sdk/downloads)，勾选 **Debugging Tools for Windows**。该 SDK 使用的版本目录为 `10.0.28000.0`，与当前构建配置一致。
4. 确保网络可以访问 GitHub、Chromium 源码及依赖下载服务，并准备一个路径较短、不含空格的工作目录。

后续步骤会安装 `depot_tools` 管理的 Python，并同步 GN、Ninja、Clang 和 Rust 工具链。

所有命令都在**同一个 CMD（`cmd.exe`）窗口**中按顺序执行，每一步成功后再继续。以下以全新的 `X:\chromium-base` 为例，可按需替换路径。

#### 1. 创建工作目录

```bat
mkdir X:\chromium-base
cd /d X:\chromium-base
git config --global core.longpaths true

mkdir work\temp work\vpython
set "TEMP=%CD%\work\temp"
set "TMP=%TEMP%"
set "TMPDIR=%TEMP%"
set "VPYTHON_VIRTUALENV_ROOT=%CD%\work\vpython"
set "CIPD_CACHE_DIR=%CD%\cipd_cache"
```

#### 2. 安装并固定 depot_tools

```bat
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git depot_tools
git -C depot_tools checkout b86fc981b72ab966f8260f73b4eca600b3b12677

set "DEPOT_TOOLS_UPDATE=0"
set "DEPOT_TOOLS_WIN_TOOLCHAIN=0"
set "PATH=%CD%\depot_tools;%PATH%"
call depot_tools\bootstrap\win_tools.bat
```

固定版本并关闭自动更新后，需要显式执行最后一条命令，初始化 Python 等 Windows 工具。

#### 3. 拉取仓库、源码和依赖

```bat
call gclient config --unmanaged --name=src --cache-dir "%CD%\git_cache" https://github.com/LittleKu/base.git
call vpython3 depot_tools\gsutil.py version
call gclient sync --no-history
cd src
```

`gclient sync` 会创建 `src`，调用同步脚本获取固定版本的 Chromium 源码，并安装所需依赖，无需另行克隆本仓库或手动执行同步脚本。

#### 4. 生成示例工程

```bat
buildtools\win\gn.exe gen out\Debug ^
  --ide=vs2022 ^
  --sln=base ^
  --filters=//examples:* ^
  --winsdk=10.0.28000.0 ^
  --ninja-executable="%CD%\third_party\ninja\ninja.exe" ^
  --args="is_debug=true use_siso=false use_remoteexec=false"
```

生成的 `out\Debug\base.sln` 包含 `example`、`base_smoke_test` 及其依赖。当前 GN 使用 `vs2022` 格式生成工程，构建仍由 Ninja 和同步的 Clang 工具链完成。

#### 5. 编译、运行并打开工程

```bat
third_party\ninja\ninja.exe -C out\Debug default
out\Debug\base_smoke_test.exe
start /wait "" out\Debug\example.exe
type out\Debug\example.log
start "" out\Debug\base.sln
```

冒烟测试成功后会输出 `base smoke test passed`；`example` 写入 `example.log` 后退出。在 Visual Studio 中将 `example` 设为启动项目，即可调试示例。

重新打开终端时，先回到 `X:\chromium-base`，恢复第 1、2 步中的环境变量，再执行 `cd src`。从该终端启动 Visual Studio，使其继承构建环境。

### Linux

使用说明待补充。

## 升级日志

- **Chromium 158.0.8127.37**：升级 `base` 源码及配套构建配置、工具链和依赖。
