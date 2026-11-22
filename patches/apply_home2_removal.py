# -*- coding: utf-8 -*-
"""Home: remove top banner(s), 生意赋能 and 邀请有礼 tiles."""
import io
import os
import shutil

ROOT = r"D:\AI Demo\QINSI\work\apk"
OUT = r"D:\AI Demo\QINSI\work\patch\out"
MAIN = os.path.join(OUT, r"assets\www\html\main.html")
MAIN_ORIG = os.path.join(ROOT, r"assets\www\html\main.html")
FUNC = os.path.join(OUT, r"assets\www\html\homePage\customFunction.html")
FUNC_ORIG = os.path.join(ROOT, r"assets\www\html\homePage\customFunction.html")


def load(path):
    return io.open(path, encoding="utf-8", newline="").read().split("\n")


def body(l):
    return l[:-1] if l.endswith("\r") else l


def eol(l):
    return "\r" if l.endswith("\r") else ""


def dump(path, lines):
    io.open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))


def hide(lines, n, needle, repl=None):
    line = body(lines[n - 1])
    if needle not in line:
        raise SystemExit("line %d mismatch: %r" % (n, line))
    if 'ng-if="false"' in line:
        return
    if repl:
        if repl[0] not in line:
            raise SystemExit("line %d missing %r" % (n, repl[0]))
        line = line.replace(repl[0], repl[1])
    else:
        line = line.replace("<div ", '<div ng-if="false" ', 1)
    lines[n - 1] = line + eol(lines[n - 1])


# main.html: top banner slider, its "show" toggle, personalized banner
main = load(MAIN)
hide(main, 32, 'class="lb-main-slider pr"')
hide(main, 53, 'class="lb-main-slider-show"')
hide(
    main,
    68,
    'ng-if="mainPageBannerSite.status',
    (
        'ng-if="mainPageBannerSite.status && !isExperience && !(isShowProbationalEnableEnd || isShowProbationalTime) && !isShowProbationalTime"',
        'ng-if="false"',
    ),
)
dump(MAIN, main)
print("main.html: banner blocks hidden")

# customFunction.html: 生意赋能 + 邀请有礼 in both layout variants
if not os.path.exists(FUNC):
    os.makedirs(os.path.dirname(FUNC), exist_ok=True)
    shutil.copyfile(FUNC_ORIG, FUNC)
func = load(FUNC)
hide(func, 42, 'ng-click="goToPaymentList()"')
hide(func, 59, 'ng-click="goRecommend();"')
hide(func, 154, 'ng-click="goToPaymentList()"')
hide(func, 171, 'ng-click="goRecommend();"')
dump(FUNC, func)
print("customFunction.html: 生意赋能/邀请有礼 hidden")
print("HOME2 REMOVAL OK")
