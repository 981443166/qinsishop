# -*- coding: utf-8 -*-
"""Rebuild the APK with patched H5 assets, preserving original zip metadata."""
import io
import os
import zipfile

SRC = r"D:\AI Demo\QINSI\qinsilk_5.31.5_pro_unlocked.apk"
PATCH = r"D:\AI Demo\QINSI\work\patch\out"
OUT_DIR = r"D:\AI Demo\QINSI\work\build"
OUT = os.path.join(OUT_DIR, "qinsilk_5.31.5_single-mode-search-unsigned.apk")

REPLACEMENTS = {
    "assets/www/js/app.min.js": os.path.join(PATCH, r"assets\www\js\app.min.js"),
    "assets/www/html/store/selectGoodMulByUnit.html": os.path.join(
        PATCH, r"assets\www\html\store\selectGoodMulByUnit.html"
    ),
    "assets/www/html/account/main.html": os.path.join(
        PATCH, r"assets\www\html\account\main.html"
    ),
    "assets/www/html/tab/salesTab.html": os.path.join(
        PATCH, r"assets\www\html\tab\salesTab.html"
    ),
}
# old v1 signature material is replaced by apksigner
DROP_PREFIX = ("META-INF/ANDROIDD.SF", "META-INF/ANDROIDD.RSA", "META-INF/MANIFEST.MF")

os.makedirs(OUT_DIR, exist_ok=True)
if os.path.exists(OUT):
    os.remove(OUT)

src = zipfile.ZipFile(SRC, "r")
with zipfile.ZipFile(OUT, "w", allowZip64=True) as dst:
    for info in src.infolist():
        if info.filename in DROP_PREFIX:
            continue
        if info.filename in REPLACEMENTS:
            with io.open(REPLACEMENTS[info.filename], "rb") as f:
                data = f.read()
        else:
            data = src.read(info.filename)

        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zi.internal_attr = info.internal_attr
        zi.create_system = info.create_system
        zi.comment = info.comment
        dst.writestr(zi, data)

print("unsigned:", OUT)
print("size:", os.path.getsize(OUT))

# integrity check: every original entry (except signatures) must keep its CRC
out = zipfile.ZipFile(OUT)
bad = out.testzip()
print("testzip:", bad)
missing = []
changed = []
for info in src.infolist():
    if info.filename in DROP_PREFIX:
        continue
    try:
        o = out.getinfo(info.filename)
    except KeyError:
        missing.append(info.filename)
        continue
    if info.filename in REPLACEMENTS:
        changed.append((info.filename, info.CRC, o.CRC))
    elif info.CRC != o.CRC:
        changed.append((info.filename, info.CRC, o.CRC))
print("missing:", missing)
print("changed:", changed)
print("entries:", len(out.infolist()))
