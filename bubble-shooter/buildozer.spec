[app]

# (str) Title of your application
title = Element Bubble Arena

# (str) Package name
package.name = elementbubblearena

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas

# (list) List of inclusions using pattern matching
source.include_patterns = asset/*.jpg,asset/*.png,asset/*.jpeg

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,md

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, __pycache__

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,pillow

# (str) Custom source folders for requirements
#requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/asset/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1


#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
#fullscreen = 0

# (string) Presplash background color (for android)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 35

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android SDK version to use
#android.sdk = 21

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path = /home/aminz/.buildozer/android/platform/android-ndk-r25b

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
# android.accept_sdk_license = False

# (str) The android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# Pixel 9 requires arm64-v8a (64-bit)
android.arch = arm64-v8a

