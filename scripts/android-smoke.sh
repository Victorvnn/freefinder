#!/usr/bin/env bash
set -euo pipefail
mkdir -p public/screenshots
capture_failure() {
  adb shell screencap -p /sdcard/failure.png || true
  adb pull /sdcard/failure.png public/screenshots/failure.png || true
  adb logcat -d -s AndroidRuntime:E > public/screenshots/runtime.txt || true
  adb shell cat /sdcard/window.xml > public/screenshots/window.xml || true
  cat public/screenshots/runtime.txt
  cat public/screenshots/window.xml
}
trap capture_failure ERR
adb logcat -c
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb shell settings put system font_scale 1.0
adb shell cmd uimode night no
adb shell am start -W -n org.freefinder.design/org.freefinder.app.MainActivity
# Wait for the actual app screen rather than assuming boot/network speed.
for attempt in $(seq 1 20); do
  adb shell uiautomator dump /sdcard/window.xml >/dev/null 2>&1 || true
  if adb shell cat /sdcard/window.xml | grep -q 'Encuentra algo'; then break; fi
  sleep 2
done
adb shell cat /sdcard/window.xml | grep -q 'Encuentra algo'
# Let the first background catalog sync complete (no account or forms).
for attempt in $(seq 1 15); do
  adb shell uiautomator dump /sdcard/window.xml >/dev/null 2>&1 || true
  if adb shell cat /sdcard/window.xml | grep -q '11'; then break; fi
  sleep 2
done
adb shell screencap -p /sdcard/home.png
adb pull /sdcard/home.png public/screenshots/home-light.png
adb shell input swipe 540 1800 540 800 500
sleep 2
adb shell screencap -p /sdcard/products.png
adb pull /sdcard/products.png public/screenshots/products-light.png
adb shell cmd uimode night yes
sleep 2
adb shell screencap -p /sdcard/dark.png
adb pull /sdcard/dark.png public/screenshots/products-dark.png
adb shell settings put system font_scale 1.3
sleep 2
adb shell screencap -p /sdcard/large.png
adb pull /sdcard/large.png public/screenshots/large-text.png
if adb logcat -d -s AndroidRuntime:E | grep -q 'FATAL EXCEPTION'; then
  adb logcat -d -s AndroidRuntime:E
  exit 1
fi
