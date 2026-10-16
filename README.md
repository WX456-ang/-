# W.ang.X- 个人作品集网站（预览版）

黑底、极简、瀑布流排版的个人网站预览。所有页面元素都是静态文件，不需要构建工具。

## 怎么看

方式一：直接双击 `index.html`（用浏览器打开即可，图片和脚本都是相对路径）。

方式二：本地起一个服务（推荐，行为与正式上线一致）：

```powershell
python -m http.server 5173 --bind 127.0.0.1 --directory .
```

然后访问 <http://127.0.0.1:5173/index.html>。

## 页面结构

| 区块 | 内容 |
| --- | --- |
| 首屏 | 纯黑背景，鼠标（或手指）在首屏移动时，7 张作品图按轨迹依次出现又淡出；右侧大字英文名 `W.ang.X-`、浅灰小字「视觉传达设计：汪馨」、草绿色能力与风格描述、分类标签 |
| 作品精选 | 瀑布流从左到右、从上到下依次排布，并按项目分组：花神海报 12 → 花神明信片 12 → 长江索道 12 → 川剧变脸 9 → 标志与 CIS 10 → 娃哈哈插画 3 → 电子书 11 → 二十四节气 3 → 西湖龙井 3 → 剪纸 2 → 赣州 2 → 动物动图 3 → 敦煌 2（共 84 张，浏览器宽度决定 2/3/4 栏）；缝隙 3px，直角无圆角，可按分类筛选，点击看大图（支持 ← → 与 Esc）。顺序在 `scripts/build_data.py` 的 `SLUG_ORDER` 里改 |
| 关于 | 一段自述 + 擅长方向与工作方式 |
| 联系 | 邮箱 / 微信电话 / 所在地 |

## 文件说明

| 路径 | 作用 |
| --- | --- |
| `index.html` | 页面结构与文案（改文案只动这里） |
| `styles.css` | 全部样式，含颜色变量 `--grass`、缝隙大小 `--gap` |
| `main.js` | 首屏轮播、瀑布流渲染、筛选、大图弹层 |
| `data.js` | 作品数据（由脚本生成，不要手改） |
| `assets/` | 压缩后的作品图（长边 1500px，JPEG q80） |
| `scripts/prepare_assets.py` | 从原始作品文件夹重新导出图片 |
| `scripts/build_data.py` | 生成 `data.js`，含挑选与顺序规则 |
| `scripts/preview_shot.js` | 无头浏览器截图（本地自检用） |

## 重新生成素材

原始作品在「作品集」总文件夹下（脚本 `scripts/prepare_assets.py` 顶部的 `SRC` 指向它，换电脑时改这一行即可）。改完原始文件后依次运行：

```powershell
python scripts/prepare_assets.py   # 重新压缩导出图片 + 生成 .review 预览图
python scripts/build_data.py       # 重新生成 data.js
```

`.review/` 只存放校对用的拼版图，不影响网站。

### 改完代码记得升版本号

`index.html` 里给 `styles.css`、`main.js`、`data.js` 都带了 `?v=7`。改动这三个文件后，把数字加一（`?v=8`），浏览器才不会继续用缓存里的旧版本；只换图片、不改代码时不用动。自己本地预览遇到样式没生效时，按 `Ctrl + F5` 强制刷新即可。

素材来源分三类：

| 来源 | 说明 |
| --- | --- |
| 图片文件夹 | 电子书设计、花神、花神明信片、插画、敦煌、二十四节气、信息可视化、剪纸、赣州、AN 动图 |
| PDF 指定页 | 标志与CIS（前 8 页）、川剧变脸（第 1/4/8/9/10/19/20/22/25 页）、长江索道（第 1/3/20/27/35/44/53/57/64/69/74/76/86 页）。页码写在 `scripts/prepare_assets.py` 的 `pages` 里 |
| 首屏跟随图 | 桌面「图片」文件夹里的 11 张（娃哈哈插画、西湖龙井信息图、芙蓉花、剪纸魅力、立春、赣州脐橙、书籍 7/8/11、梦回敦煌、杏花），清单在 `scripts/prepare_assets.py` 的 `HERO_TRAIL`，只用于首屏、不进入瀑布流 |
| 手工替换 | `source-overrides/` 存放单独指定的替换图（例如 `sichuan-opera-01.png` 换掉了川剧变脸 deck 的封面），在 `scripts/prepare_assets.py` 对应项目里用 `"replace": {序号: 路径}` 指定替换第几张 |
| 渲染目录 | 中间产物放在 `.review/render/`，删掉也没关系，重跑脚本会再生成 |

挑选 PDF 页码之前，先用总览脚本把整份 PDF 拼成一张预览图：

```powershell
python scripts/pdf_overview.py "C:\path\to\deck.pdf" ".review\overview.jpg" --columns 12 --tile 180
```

## 已知取舍

- 每个项目的张数在 `scripts/prepare_assets.py` 里指定：花神明信片 12 张全用；电子书取 12 页（其中一页是空白扉页，不显示，实际 11 张）；标志与 CIS 从 37 页里挑 10 页；长江索道从 86 页里挑 12 页；川剧变脸从 26 页里挑 9 页。
- 图片统一压到长边 1500px、JPEG q80，A4 跨页的小字在放大后略软；需要更清晰可以调 `MAX_LONG_EDGE` 和 `JPEG_QUALITY`。
- 首屏跟随图共 11 张，导出时压到长边 1000px（因为是预加载，体积要小），横图自动给更大尺寸；出现密度、停留时间在 `main.js` 的 `HOLD_MS` 与 `minDistance`；出现速度（0.15 秒、直接清晰）和淡出速度（0.5 秒缓出）在 `styles.css` 的 `.hero__item` 与 `.hero__item.is-out`。
- 缝隙与列数：缝隙 3px（`--gap`）、桌面三栏、≥1600px 四栏。

## 部署到 GitHub Pages

仓库已配置远程 `origin`，推送到 `main` 分支后：

1. 打开仓库的 **Settings → Pages**；
2. **Source** 选 `Deploy from a branch`，**Branch** 选 `main` + `/ (root)`，保存；
3. 等一分钟，站点地址是 `https://wx456-ang.github.io/-/`。

仓库里的 `.nojekyll` 让 Pages 原样输出文件（不经过 Jekyll 处理）。
