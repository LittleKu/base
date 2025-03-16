# Chromium base
## Install depot_tools
Install depot_tools [here](https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html#_setting_up)

## Setting up Windows

### Visual Studio
*   Install [Visual Studio 2022](https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-notes) (>=17.13)

*   Install [Windows 10 SDK](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)

## Setting up Mac OS
*   A Mac, Intel or Arm.
    ([More details about Arm Macs](https://chromium.googlesource.com/chromium/src.git/+/main/docs/mac_arm64.md).)
*   [Xcode](https://developer.apple.com/xcode/). Xcode comes with...
*   The macOS SDK. Run

command:
```
gclient config --unmanaged --name=src https://github.com/LittleKu/base.git

gclient sync

cd src

set NINJA_SUMMARIZE_BUILD=1

# MacOS:
export CHROMIUM_BUILDTOOLS_PATH=`pwd`/buildtools
gn gen out/Debug --filters://base "--args=is_debug=true target_os=\"mac\"" --ide=xcode --filters://examples
autoninja -C out/Debug default

# Windows:
set CHROMIUM_BUILDTOOLS_PATH=%cd%\buildtools
gn gen out/Debug_x86 --filters://base --args=is_debug=true --ide=vs2022 --sln=example --filters://examples
autoninja -C out/Debug_x86 default
```