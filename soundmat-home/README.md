# SoundMat 主页

`mukii.space/soundmat/`（中文）和 `/soundmat/en/`（英文）这两页的源文件。这个页面不使用 Hugo 主题：由 `build.py` 生成静态文件，放进 `static/soundmat/`，Hugo 只负责原样复制。

| 文件 | 管什么 |
|---|---|
| `content.toml` | 全部文案，中英文成对写在一起；标记写法见文件开头 |
| `page.html` | 页面结构（Jinja 模板），用 `t.xxx` 引用文案 |
| `style.css` / `main.js` | 样式、交互 |
| `img/` | 照片原图，构建时生成多种尺寸的 WebP |
| `fonts/` | 完整字体（不进 git，首次构建时从 google/fonts 下载） |

## 改完之后

```bash
uv run soundmat-home/build.py
```

在博客仓库根目录运行。会生成：

- `static/soundmat/index.html`、`static/soundmat/en/index.html`
- `static/soundmat/home/`：带内容指纹的 CSS、JS、裁剪过的字体、各尺寸图片

把生成结果和源文件一起提交，推到 master，Cloudflare 会自动发布。不要直接改 `static/soundmat/index.html`，下次构建时会被覆盖。

## 构建时会检查

- 每条文案都有中文和英文，缺一个就报错
- `[文字]^id` 引用的注释都存在，`[notes]` 里每条都被用到
- `doc:` 链接和 `doc =` 指向的文档在 `content/soundmat/docs/` 里存在
- 引用的图片在 `img/` 里存在

## 放视频

在 `content.toml` 的 `[film]` 里填 `src`（R2 上的视频地址）和 `poster`（`img/` 里的封面图），占位框就会换成播放器。

R2 上的视频文件名要带版本号（如 `soundmat-film-2026-10.mp4`），换视频时传新文件、改 `src`，**不要覆盖旧文件**：GYDC 快照还引用着它。

## GYDC 比赛版（冻结快照）

GYDC 参赛材料里的链接指向一份冻结的主页副本，以后改主页不影响它：

> 当前状态（2026-10-23）：快照功能已就绪，**正式快照还没打**，要等主视频放进 `[film]`、主页定稿后再打。PDF 里的链接已改指向下面的网址，在快照上线前这两个网址是 404。

| 网址 | 内容 |
|---|---|
| `mukii.space/soundmat/gydc/` | GYDC 中文版，中文 PDF 里的“项目主页”链接指向这里 |
| `mukii.space/soundmat/gydc/en/` | GYDC 英文版，英文 PDF 里的链接指向这里 |

**它是怎么冻结的：**

- 页面和它用到的全部文件（CSS、JS、字体、图片）都复制在 `static/soundmat/gydc/` 里，和主页的 `static/soundmat/home/` 互不共用。平时运行 `build.py` 只动主页，不会改、也不会清理这个文件夹。
- 每次打快照会给当时的提交打上 git 标签 `soundmat-gydc`，记录快照对应的源文件版本。
- 快照页面不让搜索引擎收录（noindex），canonical 指向主页，中英切换只在 `gydc/` 和 `gydc/en/` 之间跳。HTML 开头有一行注释，写着它来自哪个提交、哪天打的。

**没有冻结的东西：**

- 页面里指向 `/soundmat/docs/…` 的链接走的是线上文档，文档以后改了，从 GYDC 页面点进去看到的也是新版。
- 视频在 R2 上，见上面“放视频”：旧视频文件不能覆盖。

**打快照（第一次）：**

```bash
git add soundmat-home && git commit        # 快照必须对应一个提交，有未提交的改动会拒绝
uv run soundmat-home/build.py --snapshot gydc
git add static/soundmat/gydc && git commit -m "GYDC snapshot"
git push origin master --tags
```

**以后要修 GYDC 版本（比如改错字）：** 不要直接改快照里的 HTML，也不要在主页的新改动上重打。从标签取出当时的源文件，改完重打：

```bash
git switch -c gydc-fix soundmat-gydc      # 回到快照时的源文件
# 改 soundmat-home/ 里的文件，提交
uv run soundmat-home/build.py --snapshot gydc --replace
git add static/soundmat/gydc && git commit -m "Update GYDC snapshot"
git switch master
git checkout gydc-fix -- static/soundmat/gydc   # 只把新快照拿回 master，主页源文件不受影响
git commit -m "Update GYDC snapshot"
git push origin master --tags                   # 标签 soundmat-gydc 已指向 gydc-fix 上的提交
```

已有快照时不带 `--replace` 会拒绝覆盖，防止误改比赛版本。
