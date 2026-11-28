[app]

title = Binance AI Trading Bot
package.name = binancebot
package.domain = org.drakilla

source.dir = android_app
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 36
android.minapi = 24
android.arch = arm64-v8a

p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
