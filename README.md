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
| 作品精选 | 三栏（≥1600px 四栏）瀑布流，缝隙 3px，直角无圆角，可按分类筛选，点击看大图（支持 ← → 与 Esc） |
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

素材来源分三类：

| 来源 | 说明 |
| --- | --- |
| 图片文件夹 | 电子书设计、花神、花神明信片、插画、敦煌、二十四节气、信息可视化、剪纸、赣州、AN 动图 |
| PDF 指定页 | 标志与CIS（前 8 页）、川剧变脸（第 1/4/8/9/10/19/20/22/25 页）、长江索道（第 1/3/20/27/35/44/53/57/64/69/74/76/86 页）。页码写在 `scripts/prepare_assets.py` 的 `pages` 里 |
| 渲染目录 | 中间产物放在 `.review/render/`，删掉也没关系，重跑脚本会再生成 |

挑选 PDF 页码之前，先用总览脚本把整份 PDF 拼成一张预览图：

```powershell
python scripts/pdf_overview.py "C:\path\to\deck.pdf" ".review\overview.jpg" --columns 12 --tile 180
```

## 已知取舍

- 电子书只取了 12 页、花神明信片取 8 张作为节选（`prepare_assets.py` 里各项目的 `limit`），原始文件里的其余页面没有全部上图。
- 图片统一压到长边 1500px、JPEG q80，A4 跨页的小字在放大后略软；需要更清晰可以调 `MAX_LONG_EDGE` 和 `JPEG_QUALITY`。
- 首屏跟随图共 7 张，列表在 `scripts/build_data.py` 的 `HERO`；出现密度、停留时间在 `main.js` 的 `HOLD_MS` 与 `minDistance`。
- 缝隙与列数：缝隙 3px（`--gap`）、桌面三栏、≥1600px 四栏。

## 部署到 GitHub Pages

仓库已配置远程 `origin`，推送到 `main` 分支后：

1. 打开仓库的 **Settings → Pages**；
2. **Source** 选 `Deploy from a branch`，**Branch** 选 `main` + `/ (root)`，保存；
3. 等一分钟，站点地址是 `https://wx456-ang.github.io/-/`。

仓库里的 `.nojekyll` 让 Pages 原样输出文件（不经过 Jekyll 处理）。
