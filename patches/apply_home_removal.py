# -*- coding: utf-8 -*-
"""Remove home-page marketing/service modules and the old-home toggle button."""
import io
import os
import shutil

ROOT = r"D:\AI Demo\QINSI\work\apk"
OUT = r"D:\AI Demo\QINSI\work\patch\out"
MAIN = os.path.join(OUT, r"assets\www\html\main.html")
MAIN_ORIG = os.path.join(ROOT, r"assets\www\html\main.html")

if not os.path.exists(MAIN):
    os.makedirs(os.path.dirname(MAIN), exist_ok=True)
    shutil.copyfile(MAIN_ORIG, MAIN)

lines = io.open(MAIN, encoding="utf-8", newline="").read().split("\n")


def body(l):
    return l[:-1] if l.endswith("\r") else l


def eol(l):
    return "\r" if l.endswith("\r") else ""


def patch_line(n, needle, transform):
    line = body(lines[n - 1])
    if needle not in line:
        raise SystemExit("line %d mismatch: %r" % (n, line))
    lines[n - 1] = transform(line) + eol(lines[n - 1])


# 1) 智能客户分群营销卡片（原 112 行）
patch_line(
    112,
    "getUserAccResource('marketingcenter')",
    lambda l: l.replace("ng-if=\"getUserAccResource('marketingcenter')\"", 'ng-if="false"'),
)
print("hidden: 智能客户分群营销")

# 2) 便捷服务模块（原 146 行）
patch_line(
    146,
    'class="lb-this-edit-bg-ffffff p15 mt10 mb10 pr"',
    lambda l: l.replace("<div ", '<div ng-if="false" ', 1),
)
print("hidden: 便捷服务")

# 3) 切换新版/旧版首页按钮（原 176 行）
patch_line(
    176,
    'class="homePage-toggle-button"',
    lambda l: l.replace("<div ", '<div ng-if="false" ', 1),
)
print("hidden: 切换首页版本按钮")

io.open(MAIN, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("HOME REMOVAL OK")
