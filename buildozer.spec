[app]
title = FindMyCar
package.name = findmycar
package.domain = com.findmycar
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.110
requirements = python3,kivy,kivymd,plyer,pyjnius,pillow==12.2.0,sdl2_fix
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0

presplash.filename = assets/logo.png
android.presplash_color = #131315

android.api = 34
android.minapi = 21
android.ndk = 25c
android.archs = arm64-v8a
android.permissions = ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_BACKGROUND_LOCATION, CAMERA, INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.gradle_api_version = 34
android.wakelock = True
android.add_background_location = True
android.accept_sdk_license = True
android.gradle_dependencies = androidx.core:core:1.12.0
android.add_src = src
p4a.local_recipes = .p4a/recipes

icon = assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
