# -*- coding: utf-8 -*-
"""Remove marketing module entries (menus + sales-tab marketing blocks).

Scope agreed with the user: remove marketing modules / entry points only;
checkout pricing (coupon/discount/integral) is intentionally left untouched.
"""
import io
import os
import shutil

ROOT = r"D:\AI Demo\QINSI\work\apk"
OUT = r"D:\AI Demo\QINSI\work\patch\out"
JS = os.path.join(OUT, r"assets\www\js\app.min.js")
JS_ORIG = os.path.join(ROOT, r"assets\www\js\app.min.js")
TAB = os.path.join(OUT, r"assets\www\html\tab\salesTab.html")
TAB_ORIG = os.path.join(ROOT, r"assets\www\html\tab\salesTab.html")

KEYS = [
    "TMSDETAIL", "TMSGOODSLIST", "WECHATSELFORDER", "TMSORDER", "CLIENTPOINT",
    "RECHARGE", "COUPON", "MEMBERCARD", "WECHATMEMBERCARD", "WECHATPLATFORM",
    "FLASHSALE", "PROMOTIONDISCOUNT", "GOODSALBUM", "SMSERVICE", "INTELLIGENTCARD",
    "TMSDISTRIBUTION", "ECOMMERCE", "PASSENGERVOLUME", "MARKETINGCENTER",
]


def read(path):
    with io.open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def find_block(text, key):
    """Find `KEY: {` and return (start_of_line, end_after_closing_comma)."""
    marker = "\n    " + key + ": {"
    i = text.find(marker)
    if i < 0:
        raise SystemExit("menu block not found: " + key)
    start = i + 1
    brace = text.find("{", i)
    depth = 0
    j = brace
    while j < len(text):
        ch = text[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    if depth != 0:
        raise SystemExit("unbalanced block: " + key)
    k = j + 1
    while k < len(text) and text[k] in " \t":
        k += 1
    if k < len(text) and text[k] == ",":
        k += 1
    if k < len(text) and text[k] == "\r":
        k += 1
    if k < len(text) and text[k] == "\n":
        k += 1
    return start, k


text = read(JS)
before = text.count("menuType: MenuType.marketingType.val") + text.count("menuType: MenuType.tmsShopType.val")
print("marketing menu entries before:", before)

for key in KEYS:
    removed = 0
    while True:
        try:
            s, e = find_block(text, key)
        except SystemExit:
            break
        text = text[:s] + text[e:]
        removed += 1
    print("removed menu %s x%d" % (key, removed))

active = []
for line in text.split("\n"):
    s = line.strip()
    if s.startswith("//"):
        continue
    if "menuType: MenuType.marketingType.val" in line or "menuType: MenuType.tmsShopType.val" in line:
        active.append(line)
print("active marketing menu entries after:", len(active))
if len(active) == 1 and "AIASSISTANT" in text[text.find(active[0]) - 400:text.find(active[0])]:
    print("kept AIASSISTANT menu (not a marketing module)")
elif active:
    raise SystemExit("marketing menu entries still present: %r" % active)
write(JS, text)

# sales tab: hide the marketing feature blocks
if not os.path.exists(TAB):
    os.makedirs(os.path.dirname(TAB), exist_ok=True)
    shutil.copyfile(TAB_ORIG, TAB)
lines = read(TAB).split("\n")


def body(l):
    return l[:-1] if l.endswith("\r") else l


def eol(l):
    return "\r" if l.endswith("\r") else ""


def expect(n, needle):
    actual = body(lines[n - 1])
    if needle not in actual:
        raise SystemExit("line %d mismatch: %r" % (n, actual))
    return actual


# 1) 销货宝/微商城、商品相册、电商/营销中心 三个卡片区
for n, needle in [
    (78, 'class="lb-tab-list-area lb-tab-list-area-border mt10"'),
    (99, 'class="lb-tab-list-area lb-tab-list-area-border"'),
    (128, 'class="lb-tab-list-area lb-tab-list-area-border mt10"'),
]:
    line = expect(n, needle)
    if 'ng-if="false"' not in line:
        lines[n - 1] = line.replace("<div ", '<div ng-if="false" ', 1) + eol(lines[n - 1])

# 2) 电商权限分支里的“商家名片”单格
line = expect(173, "gotoIntelligentCard();")
if 'ng-if="false"' not in line:
    lines[172] = line.replace("<div ", '<div ng-if="false" ', 1) + eol(lines[172])

write(TAB, "\n".join(lines))
print("MARKETING REMOVAL OK")
