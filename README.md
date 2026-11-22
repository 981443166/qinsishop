# qinsishop — 勤策 5.31.5 定制包

基于 `qinsilk_5.31.5_pro_unlocked.apk` 的 H5 资源定制与重打包工程。

- 包名：`com.qinsilk.appUniverse`
- 版本：5.31.5（versionCode 53105031）
- 原始 APK SHA-256：`671D875BE41AF53D02100F85EA8918F70B88EAE40F92E6402103B050981D98C6`

## 已做的修改

| # | 修改 | 说明 |
|---|---|---|
| 1 | 盘点·单品模式搜索优化 | 输入改为本地过滤，回车/“查询全部分类”才走服务端；局部 loading，不回顶、不重置分类 |
| 2 | 移除在线更新 | 关闭 CodePush 热更新、原生整包更新、“检查更新”入口 |
| 3 | 移除营销菜单 | 删除 19 个营销菜单项，隐藏销售 Tab 的营销区块及“生意圈/秦丝商学院”；收银台优惠算价逻辑保留 |
| 4 | 移除首页模块 | 删除首页“智能客户分群营销”“便捷服务”“切换到旧版首页”按钮 |
| 5 | 移除首页 Banner 与入口 | 删除顶部 Banner、活动横幅、“生意赋能”“邀请有礼” |
| 6 | 移除基础页入口 | 删除“招商合作、邀请有礼、秦丝微信服务、生意赋能”及“智能短信”菜单项 |

详细说明见 `docs/`。

## 产物

- `dist/qinsilk_5.31.5_no-marketing-optimized.apk`
  - SHA-256：`BC6BE3A83458F143EC9B8E393DCE27F4F403B9F2BD0A165A51D4B70A34ED312E`
  - 签名：v1 + v2 + v3（自签名证书 `CN=Qinsilk Debug`）
  - 与原包签名不同，安装前需卸载旧包

## 构建

```bash
python patches/apply_h5_patch.py
python patches/apply_update_removal.py
python patches/apply_marketing_removal.py
python patches/apply_business_removal.py
python patches/apply_home_removal.py
python patches/apply_home2_removal.py
python patches/apply_base_removal.py
python patches/repack_apk.py
zipalign -p -f 4 ...unsigned.apk ...aligned.apk
apksigner sign --ks qinsilk-debug.jks --ks-type JKS --ks-key-alias qinsilk \
  --ks-pass pass:qinsilk123 --key-pass pass:qinsilk123 \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out ...signed.apk ...aligned.apk
```

> 补丁脚本按原始 APK 的行号/原文断言定位，升级新版本时需重新校准。

## 目录

```
docs/       修改说明与差异
patches/    补丁与重打包脚本
dist/       构建产物
```
