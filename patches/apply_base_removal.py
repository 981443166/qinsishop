# -*- coding: utf-8 -*-
"""Hide base-page (mine tab) entries: 生意赋能/秦丝微信服务/邀请有礼/招商合作/智能短信."""
import io
import os
import re
import shutil

ROOT = r"D:\AI Demo\QINSI\work\apk"
OUT = r"D:\AI Demo\QINSI\work\patch\out"
MINE = os.path.join(OUT, r"assets\www\html\tab\mineTab.html")
MINE_ORIG = os.path.join(ROOT, r"assets\www\html\tab\mineTab.html")

if not os.path.exists(MINE):
    os.makedirs(os.path.dirname(MINE), exist_ok=True)
    shutil.copyfile(MINE_ORIG, MINE)

lines = io.open(MINE, encoding="utf-8", newline="").read().split("\n")


def body(l):
    return l[:-1] if l.endswith("\r") else l


def eol(l):
    return "\r" if l.endswith("\r") else ""


def hide_anchor(n, needle):
    line = body(lines[n - 1])
    if needle not in line:
        raise SystemExit("line %d mismatch: %r" % (n, line))
    if 'ng-if="false"' in line:
        return
    if 'ng-if="' in line:
        line = re.sub(r'ng-if="[^"]*"', 'ng-if="false"', line, count=1)
    else:
        line = line.replace("<a ", '<a ng-if="false" ', 1)
    lines[n - 1] = line + eol(lines[n - 1])


hide_anchor(244, 'ng-click="gotoVaService();"')
hide_anchor(269, 'ui-sref="eventmenu.weChatPublic"')
hide_anchor(279, 'ng-click="goToRecommend();"')
hide_anchor(289, 'ng-click="goToInvestmentCooperation();"')

# 智能短信 menu item: exclude from both menu lists
for n in (138, 147):
    line = body(lines[n - 1])
    old = "ng-show=\"(mineTabMenuList[item].name === '智能短信' && isShowSmartSms) || mineTabMenuList[item].name !== '智能短信'\""
    if old not in line:
        if "ng-show=\"mineTabMenuList[item].name !== '智能短信'\"" in line:
            continue
        raise SystemExit("line %d smartSms filter not found" % n)
    lines[n - 1] = line.replace(old, 'ng-show="mineTabMenuList[item].name !== \'智能短信\'"') + eol(lines[n - 1])

io.open(MINE, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("BASE REMOVAL OK")
