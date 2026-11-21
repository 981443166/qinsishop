# -*- coding: utf-8 -*-
"""Disable all online-update paths in the already-patched H5 assets.

Targets (asset-level only; native plugins stay installed but are never driven):
  * CodePush hot update: Tools.appHotUpdate / appHotUpdateSilent / boot check /
    about-page current package
  * Native whole-APK update: $rootScope.updateApp + checkForUpdate
  * Account page "检查更新" entry
"""
import io
import os
import shutil

ROOT = r"D:\AI Demo\QINSI\work\apk"
OUT = r"D:\AI Demo\QINSI\work\patch\out"
JS = os.path.join(OUT, r"assets\www\js\app.min.js")
ACC = os.path.join(OUT, r"assets\www\html\account\main.html")
ACC_SRC = os.path.join(ROOT, r"assets\www\html\account\main.html")
MARK = "在线更新已移除"


def load(path):
    with io.open(path, encoding="utf-8", newline="") as f:
        return f.read().split("\n")


def body(line):
    return line[:-1] if line.endswith("\r") else line


def eol(line):
    return "\r" if line.endswith("\r") else ""


def dump(path, lines):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))


def find_exact(lines, text):
    hits = [i for i, l in enumerate(lines) if body(l).strip() == text]
    if len(hits) != 1:
        raise SystemExit("anchor %r matched %d lines" % (text, len(hits)))
    return hits[0]


def guard_return(lines, text, comment):
    idx = find_exact(lines, text)
    nxt = body(lines[idx + 1]) if idx + 1 < len(lines) else ""
    if MARK in nxt:
        print("skip (already patched):", comment)
        return
    lines.insert(idx + 1, "    return; // " + MARK + "（" + comment + "）" + eol(lines[idx]))
    print("patched:", comment)


js = load(JS)

guard_return(js, "function appHotUpdate(showTips) {", "热更新")
guard_return(js, "function appHotUpdateSilent() {", "静默热更新")
guard_return(js, "$rootScope.updateApp = function (isManual) {", "原生整包更新")
guard_return(js, "var checkForUpdate = function checkForUpdate() {", "自动检查更新")
guard_return(js, "var appHotUpdate = function appHotUpdate(isManual) {", "账号页热更新")

# boot-time CodePush check: keep block structure, never enter it
boot = [
    i
    for i, l in enumerate(js)
    if body(l).strip() == "if (window.cordova && window.codePush) {"
    and "commonDataInterface.getCodepushDeploymentKey" in body(js[i + 1])
]
if not boot:
    already = [
        i
        for i, l in enumerate(js)
        if body(l).strip() == "if (false) {"
        and "commonDataInterface.getCodepushDeploymentKey" in body(js[i + 1])
    ]
    if already:
        print("skip (already patched): boot codePush check")
    else:
        raise SystemExit("boot codePush guard not found")
elif len(boot) != 1:
    raise SystemExit("boot codePush guard matched %d" % len(boot))
else:
    i = boot[0]
    js[i] = body(js[i]).replace("if (window.cordova && window.codePush) {", "if (false) {") + eol(js[i])
    print("patched: boot codePush check")

# about page: stop reading the installed CodePush package
about = [i for i, l in enumerate(js) if body(l).strip() == "if (window.codePush) {"]
if not about:
    already = [
        i
        for i, l in enumerate(js)
        if body(l).strip() == "if (false) {"
        and "window.codePush.getCurrentPackage" in body(js[i + 1])
    ]
    if already:
        print("skip (already patched): about page current package")
    else:
        raise SystemExit("about page codePush guard not found")
elif len(about) != 1:
    raise SystemExit("about page codePush guard matched %d" % len(about))
else:
    i = about[0]
    js[i] = body(js[i]).replace("if (window.codePush) {", "if (false) {") + eol(js[i])
    print("patched: about page current package")

dump(JS, js)

# account page: hide the manual "检查更新" entry
if not os.path.exists(ACC):
    os.makedirs(os.path.dirname(ACC), exist_ok=True)
    shutil.copyfile(ACC_SRC, ACC)
acc = load(ACC)
i = None
for idx, l in enumerate(acc):
    if 'ng-click="updateApp(true);"' in body(l):
        i = idx
        break
if i is None:
    raise SystemExit("account update entry not found")
line = body(acc[i])
for cond in (
    'ng-if="platformIsAndroid || !isExceptionForAppStore || !isExceptionForGoogle"',
):
    if cond in line:
        line = line.replace(cond, 'ng-if="false"')
if 'ng-if="false"' not in line:
    raise SystemExit("account update entry condition not found: %r" % line)
acc[i] = line + eol(acc[i])
print("patched: account 检查更新 entry hidden")
dump(ACC, acc)

print("REMOVAL PATCH OK")
