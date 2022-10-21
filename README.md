# base
chromium base

```
gclient config --unmanaged --name=src https://github.com/LittleKu/base.git

gclient sync

cd src

gn gen out\Build --filters://base "--args=is_debug=true" --ide=xcode

autoninja -C out\Build default