[app]

# (str) Title of your application
title = Eye Tracking App

# (str) Package name
package.name = eyetracking

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code directory where main.py is located
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = kivy,opencv-python,mediapipe,numpy

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

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

# (int) Android API to use
android.api = 31

# (int) Android target API to use
android.targetapi = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (str) Android SDK version to use
android.sdk = 31

# (str) Android entry point, default is ok for Kivy apps
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy apps
#android.theme = @android:style/Theme.NoTitleBar

# (str) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android/*.so
#android.add_libs_arm64_v8a = libs/android/*.so
#android.add_libs_x86 = libs/android/*.so
#android.add_libs_x86_64 = libs/android/*.so

# (bool) Android logging
android.log = True

# (str) Android additional jar files to copy into libs
#android.add_jars = foo.jar,bar.jar

# (str) Android additional java source files
#android.add_src =

# (str) Android AAR files to copy
#android.add_aars =

# (str) Android res files to copy (images, xmls)
#android.add_res =

# (str) Android assets to copy
#android.add_assets =

# (str) Android Gradle dependencies (may be blank)
#android.gradle_dependencies =

# (str) Android extra manifest.xml entries
#android.manifest.extra =

# (str) Android meta-data to add
#android.meta_data =

# (str) Android intent filters to add
#android.intent_filters =

# (str) Android services to declare
#android.services =

# (str) Android service class name
#android.service_class_name = org.kivy.android.PythonService

# (str) Android extra jars to copy
#android.add_jars =

# (str) Android extra gradle dependencies
#android.gradle_dependencies =

# (str) IOS deploy
#ios.deploy =

# (str) IOS code sign
#ios.codesign =

# (str) IOS profile
#ios.profile =

# (str) IOS additional frameworks
#ios.add_frameworks =

# (str) IOS embed frameworks
#ios.embed_frameworks =

# (str) IOS additional source files
#ios.add_src =

# (str) IOS additional libraries
#ios.add_libs =

# (str) OSX deploy
#osx.deploy =

# (str) OSX code sign
#osx.codesign =

# (str) OSX app category
#osx.app_category =

# (str) OSX additional frameworks
#osx.add_frameworks =

# (str) OSX additional source files
#osx.add_src =

# (str) OSX additional libraries
#osx.add_libs =

# (str) Windows deploy
#windows.deploy =

# (str) Windows code sign
#windows.codesign =

# (str) Windows additional libraries
#windows.add_libs =

# (str) Windows additional source files
#windows.add_src =

# (str) Linux deploy
#linux.deploy =

# (str) Linux additional libraries
#linux.add_libs =

# (str) Linux additional source files
#linux.add_src =

# (str) Windows additional source files
#windows.add_src =

# (str) Linux additional source files
#linux.add_src =