[app]
title = FindMyCar
package.name = findmycar
package.domain = com.findmycar
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,kivymd,plyer,pyjnius
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0

android.api = 34
android.minapi = 21
android.ndk = 25c
android.archs = arm64-v8a
android.permissions = ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_BACKGROUND_LOCATION, CAMERA, INTERNET
android.gradle_api_version = 34
android.wakelock = True
android.add_background_location = True

presplash.filename = assets/logo.png
presplash.bg_color = 0d1117
presplash.loading_color = 00e5ff
presplash.scale = 0.6
icon = assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
