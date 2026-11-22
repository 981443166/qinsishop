# 首页 Banner 与入口移除说明

> 目标：删除首页顶部 Banner、「生意赋能」与「邀请有礼」入口。
> 修改文件：`assets/www/html/main.html`、`assets/www/html/homePage/customFunction.html`

---

## 1. 改动

| # | 模块 | 文件 / 原位置 | 改动 |
|---|---|---|---|
| 1 | 顶部 Banner 轮播 | `main.html` 32–39 行 | `ng-if="false"` |
| 2 | Banner“收起/新功能”切换条 | `main.html` 53–58 行 | `ng-if="false"` |
| 3 | 千人千面活动横幅 | `main.html` 68–73 行 | `ng-if` 改为 `false` |
| 4 | 生意赋能（旧布局） | `customFunction.html` 42–48 行 | `ng-if="false"` |
| 5 | 邀请有礼（旧布局） | `customFunction.html` 59–68 行 | `ng-if="false"` |
| 6 | 生意赋能（新布局） | `customFunction.html` 154–160 行 | `ng-if="false"` |
| 7 | 邀请有礼（新布局） | `customFunction.html` 171–180 行 | `ng-if="false"` |

`customFunction.html` 里同一入口有两种布局（普通宽度与 `customFunction-wdith-25`），两处都隐藏，避免不同首页版本下残留。

## 2. 没有改什么

- 顶部消息条、版本提示、试用/升级提示保留；
- 常用功能里的其他入口（数据统计、销售图表、金融服务、慧店通、更多功能等）保留；
- `goRecommend()`、`goToPaymentList()`、`getInviteGiftStyle()` 等 JS 方法未删除，只是没有入口；
- 活动位数据、角标配置仍在服务端，客户端不再展示。

## 3. 验证

| # | 检查 | 预期 |
|---|---|---|
| 1 | 首页顶部 | 没有 Banner 轮播，也没有“收起/新功能”切换条 |
| 2 | 首页 | 没有“千人千面”活动横幅 |
| 3 | 首页常用功能 | 没有“生意赋能”“邀请有礼”，其余图标排列正常 |
| 4 | 首页消息条、版本提示 | 正常显示 |
| 5 | 开单、盘点、报表 | 正常 |

## 4. 构建信息

| 项 | 值 |
|---|---|
| 输出 APK | `dist/qinsilk_5.31.5_no-marketing-optimized.apk` |
| SHA-256 | `4FADA7D1A456FB11A94BC4CC772EF296D3570C05B48CF6FDE465CBC11F271CEC` |
| 签名 | v1 + v2 + v3，`apksigner verify` 通过 |
