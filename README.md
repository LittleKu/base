# Chromium base
## Install depot_tools
Install depot_tools [here](https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html#_setting_up)

## Setting up Windows

### Visual Studio
*   Install [Visual Studio 2019](https://docs.microsoft.com/en-us/visualstudio/releases/2019/release-notes) (>=16.0.0)

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
gn gen out/Debug --filters://base "--args=is_debug=true target_os=\"mac\"" --ide=xcode
autoninja -C out/Debug default

# Windows:
gn gen out/Debug_x86 --filters://base "--args=is_debug=true target_os=\"win\" target_cpu=\"x86\"" --ide=vs2019
autoninja -C out/Debug_x86 default
```