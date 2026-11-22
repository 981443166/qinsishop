# -*- coding: utf-8 -*-
"""Page cleanups: home TMS card, sale smart SMS, client marketing fields, home spacing."""
import io
import os
import re
import shutil

ROOT = r"D:\AI Demo\QINSI\work\apk"
OUT = r"D:\AI Demo\QINSI\work\patch\out"


def prepare(rel):
    dst = os.path.join(OUT, *rel.split("/"))
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, *rel.split("/")), dst)
    return dst


def load(path):
    return io.open(path, encoding="utf-8", newline="").read().split("\n")


def dump(path, lines):
    io.open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))


def body(l):
    return l[:-1] if l.endswith("\r") else l


def eol(l):
    return "\r" if l.endswith("\r") else ""


def hide(lines, n, needle):
    line = body(lines[n - 1])
    if needle not in line:
        raise SystemExit("line %d mismatch: %r" % (n, line))
    if 'ng-if="false"' in line:
        return
    if 'ng-if="' in line:
        line = re.sub(r'ng-if="[^"]*"', 'ng-if="false"', line, count=1)
    else:
        line = line.replace("<div ", '<div ng-if="false" ', 1)
    lines[n - 1] = line + eol(lines[n - 1])


def add_class(lines, n, needle, cls):
    line = body(lines[n - 1])
    if needle not in line:
        raise SystemExit("line %d mismatch: %r" % (n, line))
    if cls in line:
        return
    m = re.search(r'class="([^"]*)"', line)
    if not m:
        raise SystemExit("line %d has no class" % n)
    line = line[: m.start()] + 'class="' + m.group(1) + " " + cls + '"' + line[m.end():]
    lines[n - 1] = line + eol(lines[n - 1])


# 1) 首页：删销货宝卡片
p = prepare("assets/www/html/homePage/customFunction.html")
L = load(p)
hide(L, 75, 'class="lb-main-tmsShop')
dump(p, L)
print("customFunction: TMS card hidden")

# 2) 开单页：删智能短信模块
p = prepare("assets/www/html/sale/edit.html")
L = load(p)
hide(L, 625, '<div class="list">')
dump(p, L)
print("sale/edit: smart SMS hidden")

# 3) 客户详情：会员卡号、公众号通知、充值明细、优惠券、积分
p = prepare("assets/www/html/client/detail.html")
L = load(p)
hide(L, 81, 'class="lb-edit-row"')
hide(L, 120, "componentUserDTO.nickName != null")
hide(L, 139, "!(componentUserDTO && componentUserDTO.nickName != null)")
hide(L, 265, "clientDepositRecord();")
hide(L, 271, "openCouponListModal();")
hide(L, 283, '<div class="list mb10">')
dump(p, L)
print("client/detail: marketing fields hidden")

# 4) 首页顶部间距：Banner 删除后给消息条补 mt10
p = prepare("assets/www/html/main.html")
L = load(p)
add_class(L, 41, 'class="lb-main-message', "mt10")
dump(p, L)
print("main: message row spacing adjusted")

print("CLEANUP2 OK")
