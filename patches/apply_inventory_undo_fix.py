# -*- coding: utf-8 -*-
"""Inventory history: undo the selected count sheet instead of the latest one."""
import io

JS = r"D:\AI Demo\QINSI\work\patch\out\assets\www\js\app.min.js"

text = io.open(JS, encoding="utf-8", newline="").read()

if "撤销当前单据" in text:
    print("SKIP: inventory undo fix already applied")
    raise SystemExit(0)

start_marker = "  // 撤销盘点单操作\n  $scope.destroyStoreOrder = function () {"
end_marker = "  $scope.$on('$ionicView.beforeEnter', function () {"

start = text.find(start_marker)
if start < 0:
    raise SystemExit("start marker not found")
end = text.find(end_marker, start)
if end < 0:
    raise SystemExit("end marker not found")

new_block = '''  // 撤销盘点单操作（撤销当前单据，不再限制必须是最后一张）
  $scope.destroyStoreOrder = function () {
    var currentOrder = $scope.orderDetail && $scope.orderDetail.order;
    var updateTime = currentOrder && currentOrder.updateTime;
    if (updateTime && !Tools.isInDays(updateTime, Date.parse(new Date()), 7)) {
      $ionicPopup.alert({
        template: "<div class='tc'>该单生成时间已超过7天，不支持撤销</div>",
        okText: '确定'
      });
      return false;
    }
    var confirmPopup = $ionicPopup.confirm({
      template: "<div class='tc'>单据撤销将本单原来的盘亏/盘盈数量进行恢复，是否确认撤销该单据?</div>",
      cancelText: '取消',
      okText: '确认'
    });
    confirmPopup.then(function (res) {
      if (res) {
        destroyStoreOrderServe();
      }
    });
  };

'''

text = text[:start] + new_block + text[end:]
io.open(JS, "w", encoding="utf-8", newline="").write(text)
print("inventory undo fix applied")
