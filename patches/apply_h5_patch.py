# -*- coding: utf-8 -*-
"""Apply the 单品模式 search optimization to the extracted H5 assets.

app.min.js mixes LF and CRLF line endings, so every edit preserves the ending
of the line it replaces (or of the anchor line for insertions).
"""
import io
import json
import os

ROOT = r"D:\AI Demo\QINSI\work\apk"
JS = os.path.join(ROOT, r"assets\www\js\app.min.js")
TPL = os.path.join(ROOT, r"assets\www\html\store\selectGoodMulByUnit.html")
OUT = r"D:\AI Demo\QINSI\work\patch\out"


def load(path):
    with io.open(path, encoding="utf-8", newline="") as f:
        return f.read().split("\n")


def body(line):
    return line[:-1] if line.endswith("\r") else line


def eol(line):
    return "\r" if line.endswith("\r") else ""


def expect(lines, lineno, needle):
    actual = body(lines[lineno - 1])
    if needle not in actual:
        raise SystemExit(
            "line %d mismatch\nexpected to contain: %r\nactual: %r"
            % (lineno, needle, actual)
        )
    return actual


def replace_block(lines, start, end, new_bodies):
    """Replace 1-based inclusive [start, end] with new_bodies (list of str)."""
    ending = eol(lines[start - 1])
    lines[start - 1 : end] = [b + ending for b in new_bodies]


def insert_after(lines, lineno, new_bodies):
    """Insert new_bodies after 1-based lineno, using that line's ending."""
    ending = eol(lines[lineno - 1])
    lines[lineno:lineno] = [b + ending for b in new_bodies]


def dump(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------- app.min.js
js = load(JS)
if len(js) not in (399101, 399102):
    raise SystemExit("unexpected js line count: %d" % len(js))

# E1 clearSearch: 盘点 single mode must not fire a server query on clear
expect(js, 254272, "$scope.mulSpecData.selectGoodModel == $scope.mulSpecData.SINGLEMODEL")
expect(js, 254273, "$scope.search.goodKey = '';")
expect(js, 254274, "$scope.focused_good = 'centered';")
expect(js, 254275, "$scope.goodComfirmSearch();")
replace_block(
    js,
    254272,
    254275,
    [
        "    if ($scope.mulSpecData.selectGoodModel == $scope.mulSpecData.SINGLEMODEL) {",
        "      $scope.search.goodKey = '';",
        "      $scope.focused_good = 'centered';",
        "      if ($scope.search.orderType === 'store') {",
        "        // 盘点单清空关键字只恢复本地列表，不再触发请求",
        "        $scope.search.serverResultKey = null;",
        "        return;",
        "      }",
        "      $scope.goodComfirmSearch();",
    ],
)

# E6 local-filter helpers, inserted after filterCat end (line 254184)
expect(js, 254184, "  };")
insert_after(
    js,
    254184,
    [
        "",
        "  // 单品模式：本地关键字过滤（仅盘点单启用，输入时不再整页重查）",
        "  var singleModeSearchTextCache = {};",
        "  var singleModeLocalMatch = function (good, keyword) {",
        "    var cacheKey = good.goodsSn;",
        "    var text = singleModeSearchTextCache[cacheKey];",
        "    if (text === undefined) {",
        "      text = [good.name, good.goodsSn, good.barCode, good.specs, good.helpCode, good.pinyin, good.propertyName, good.propertyValueName]",
        "        .filter(function (item) { return item !== undefined && item !== null && item !== ''; })",
        "        .join(' ').toLowerCase();",
        "      singleModeSearchTextCache[cacheKey] = text;",
        "    }",
        "    return text.indexOf(keyword.toLowerCase()) > -1;",
        "  };",
        "  $scope.singleModeVisible = function (good) {",
        "    if (!$scope.search || $scope.search.orderType !== 'store') {",
        "      return true;",
        "    }",
        "    var rawKey = $scope.search.goodKey || '';",
        "    if (rawKey.trim() === '') {",
        "      return true;",
        "    }",
        "    if ($scope.search.serverResultKey === rawKey && $scope.search.resultSnMap) {",
        "      return !!$scope.search.resultSnMap[good.goodsSn];",
        "    }",
        "    return singleModeLocalMatch(good, rawKey.trim());",
        "  };",
        "  // 单品模式输入框：盘点单只做本地过滤；调拨单保持原有服务端搜索",
        "  $scope.onKeywordInput = function () {",
        "    if (!$scope.search || $scope.search.orderType !== 'store') {",
        "      $scope.storeOrder.searchGoodsByKeyword(false);",
        "    }",
        "  };",
    ],
)

# E7 getMore: keep the server result-set map in sync when appending a page
expect(js, 253298, "$scope.pushToGoodsGroup(data, $scope.search.orderType);")
insert_after(
    js,
    253298,
    [
        "      if ($scope.search.orderType === 'store' && $scope.search.serverResultKey === ($scope.search.goodKey || '')) {",
        "        $scope.search.resultSnMap = $scope.search.resultSnMap || {};",
        "        (data && data.optionList ? data.optionList : []).forEach(function (item) {",
        "          $scope.search.resultSnMap[item.goodsSn] = 1;",
        "        });",
        "      }",
    ],
)

# E2 finally: no scroll jump for 盘点 keyword search
expect(js, 253199, '})["finally"](function () {')
expect(js, 253200, "lbScrollDelegate.scrollTop('storeGoodModalCtrlScroll');")
expect(js, 253201, "$scope.isLoading = false;")
expect(js, 253202, "lbSpinnerDialog.hide();")
expect(js, 253203, "});")
replace_block(
    js,
    253199,
    253203,
    [
        '    })["finally"](function () {',
        "      if (!storeKeywordSearch) {",
        "        lbScrollDelegate.scrollTop('storeGoodModalCtrlScroll');",
        "      }",
        "      $scope.isLoading = false;",
        "      $scope.search.listSearching = false;",
        "      lbSpinnerDialog.hide();",
        "    });",
    ],
)

# E3 search success: remember the keyword + its server result set
expect(js, 253195, "$scope.pushToGoodsGroup(data, $scope.search.orderType);")
insert_after(
    js,
    253195,
    [
        "      if ($scope.search.orderType === 'store') {",
        "        var resultSnMap = {};",
        "        ($scope.search.goodListForSearchKey || []).forEach(function (item) {",
        "          resultSnMap[item.goodsSn] = 1;",
        "        });",
        "        $scope.search.resultSnMap = resultSnMap;",
        "        $scope.search.serverResultKey = storeRequestKey;",
        "      }",
    ],
)

# E8 early return (no affiliation): never leave the list stuck in loading state
expect(js, 253172, "$scope.search.orderType == 'store' && !$scope.selectAffiliation.id")
expect(js, 253173, "lbSpinnerDialog.hide();")
expect(js, 253174, "return false;")
expect(js, 253175, "}")
replace_block(
    js,
    253172,
    253175,
    [
        "    if ($scope.search.orderType == 'store' && !$scope.selectAffiliation.id) {",
        "      lbSpinnerDialog.hide();",
        "      $scope.isLoading = false;",
        "      $scope.search.listSearching = false;",
        "      return false;",
        "    }",
    ],
)

# E4 spinner: 盘点 keyword search uses an inline indicator instead
expect(js, 253155, "lbSpinnerDialog.show(true);")
replace_block(
    js,
    253155,
    253155,
    [
        "    if (!storeKeywordSearch) {",
        "      lbSpinnerDialog.show(true);",
        "    }",
    ],
)

# E5 head: classify keyword search before touching loading state
expect(js, 253103, "$scope.isLoading = true;")
expect(js, 253104, "$scope.search.currentPageNum = 1;")
replace_block(
    js,
    253103,
    253104,
    [
        "    // 盘点单带关键字搜索时只做局部 loading，避免整页遮罩与滚动跳动",
        "    var storeKeywordSearch = $scope.search.orderType === 'store' && !!($scope.search.goodKey || '').trim();",
        "    var storeRequestKey = $scope.search.goodKey || '';",
        "    $scope.isLoading = !storeKeywordSearch;",
        "    $scope.search.listSearching = storeKeywordSearch;",
        "    $scope.search.currentPageNum = 1;",
    ],
)

dump(os.path.join(OUT, r"assets\www\js\app.min.js"), js)

# ------------------------------------------------------- selectGoodMulByUnit.html
tpl = load(TPL)
if len(tpl) not in (385, 386):
    raise SystemExit("unexpected tpl line count: %d" % len(tpl))

# T3 empty-state "查询全部分类" -> explicit (non-debounced) server search
for lineno in (212, 200):
    expect(tpl, lineno, "查询全部分类")
    expect(tpl, lineno, 'ng-click="storeOrder.searchGoodsByKeyword(false);">')
    tpl[lineno - 1] = body(tpl[lineno - 1]).replace(
        'ng-click="storeOrder.searchGoodsByKeyword(false);">查询全部分类',
        'ng-click="goodComfirmSearch();">查询全部分类',
    ) + eol(tpl[lineno - 1])

# T2 list filter: 盘点 single mode uses the local keyword filter
expect(tpl, 156, "filter : filterCat")
tpl[155] = body(tpl[155]).replace(
    "filter : filterCat",
    "filter : (search.orderType == 'store' ? singleModeVisible : filterCat)",
) + eol(tpl[155])
if "singleModeVisible" not in tpl[155]:
    raise SystemExit("list filter replacement failed")

# T4 inline searching hint inside the single-mode block
expect(tpl, 153, 'ng-if="mulSpecData.selectGoodModel == mulSpecData.SINGLEMODEL"')
insert_after(
    tpl,
    153,
    ['\t\t\t\t\t\t<div class="tc lb-color-caption f12 p5" ng-if="search.listSearching">正在搜索全部商品…</div>'],
)

# T1 input: 盘点 filters locally, transfer keeps the original server search
expect(tpl, 43, 'ng-change="storeOrder.searchGoodsByKeyword(false);"')
tpl[42] = body(tpl[42]).replace(
    'ng-change="storeOrder.searchGoodsByKeyword(false);"', 'ng-change="onKeywordInput();"'
) + eol(tpl[42])
if "onKeywordInput" not in tpl[42]:
    raise SystemExit("input ng-change replacement failed")

dump(os.path.join(OUT, r"assets\www\html\store\selectGoodMulByUnit.html"), tpl)

print(json.dumps({"js_lines": len(js), "tpl_lines": len(tpl)}, indent=1))
print("PATCH OK")
