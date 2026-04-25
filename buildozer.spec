[app]

# (str) Title of your application
title = Eye Commander

# (str) Package name
package.name = eyecmd

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code directory where main.py is located
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy,mediapipe,opencv-python,numpy,cython==0.29.33

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait
fullscreen = 0

# (list) Permissions
android.permissions = CAMERA, INTERNET, FOREGROUND_SERVICE, BIND_ACCESSIBILITY_SERVICE

# (str) Android manifest extra
android.manifest.extra = <service android:name="org.test.myapp.MyAccessibilityService" android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"> <intent-filter> <action android:name="android.accessibilityservice.AccessibilityService" /> </intent-filter> <meta-data android:name="android.accessibilityservice" android:resource="@xml/accessibility_config" /> </service>

# (str) Android additional source files
android.add_src = src/

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.zip
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a

# (str) Android API to use
android.api = 33

# (str) Android target API to use
android.targetapi = 33

# (int) Minimum API your APK will support
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK version to use
android.sdk = 33