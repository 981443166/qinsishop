# -*- coding: utf-8 -*-
"""Hide the remaining 生意圈 / 秦丝商学院 blocks in the sales tab."""
import io
import os

TAB = r"D:\AI Demo\QINSI\work\patch\out\assets\www\html\tab\salesTab.html"

lines = io.open(TAB, encoding="utf-8", newline="").read().split("\n")


def body(l):
    return l[:-1] if l.endswith("\r") else l


def eol(l):
    return "\r" if l.endswith("\r") else ""


# 1) 生意圈 + 商学院 区块（无电商权限分支）
n = 155
line = body(lines[n - 1])
if 'class="lb-tab-list-area lb-tab-list-area-border"' not in line:
    raise SystemExit("line 155 mismatch: %r" % line)
if 'ng-if="false"' not in line:
    lines[n - 1] = line.replace("<div ", '<div ng-if="false" ', 1) + eol(lines[n - 1])
    print("hidden: business community/school block")

# 2) 商学院 单独区块（有电商权限分支）
n = 189
line = body(lines[n - 1])
if "getUserAccResource(menuList['ECOMMERCE'].authority)" not in line:
    raise SystemExit("line 189 mismatch: %r" % line)
lines[n - 1] = line.replace(
    "ng-if=\"getUserAccResource(menuList['ECOMMERCE'].authority)\"", 'ng-if="false"'
) + eol(lines[n - 1])
print("hidden: business school block")

io.open(TAB, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("BUSINESS REMOVAL OK")
