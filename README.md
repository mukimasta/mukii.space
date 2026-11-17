# mukii.space

Hanlin 的个人网站。Hugo 构建，主题是仓库自己的 `themes/mukii`（从 [dario](https://github.com/GrantBirki/dario) 改出来）。

## 发布

推到 `master`，Cloudflare Workers 自动跑 `build.sh`（装 Hugo 等，裁剪字体，再 `hugo build`），发布 `public/`。配置在 `wrangler.toml`。

本地预览：`hugo server`（需要 Hugo extended）。

## 目录

| 位置 | 内容 |
|---|---|
| `content/` | 文章：`blogs/professional/`（技术）、`qingyeshu/`（青叶树）、`articles/`（散文）、`soundmat/docs/`（SoundMat 文档） |
| `themes/mukii/` | 主题：模板、样式（`assets/css/default.css`）、深色模式和脚注的 JS、字体 |
| `layouts/` | 只属于个别页面的模板：Journey、Professional、SoundMat 文档、短代码、mermaid 和公式渲染 |
| `scripts/build_fonts.py` | 把 Inter 和思源黑体裁成全站用到的字，写进 `themes/mukii/static/fonts/` |
| `static/` | 原样复制的文件：图片、SoundMat 主页、LifeLab 页面 |
| `soundmat-home/` | SoundMat 主页的源文件，不走 Hugo，见 [它的 README](soundmat-home/README.md) |

各目录的 `_index.md` 里，文章列表是手写的链接，加文章时要一起更新。

## 字体

Inter（英文）+ 思源黑体（中文），网站自带，不依赖访问者的电脑。中文字体只保留站上用到的字：Cloudflare 构建时会自动重新裁剪；本地加了新文章想预览，跑一次 `python3 scripts/build_fonts.py`（需要 fonttools、brotli）。生成的字体也提交进仓库，裁剪失败时照样能用。

## 注意

- 仓库在 Worlds 里，Mac 和 Jetson 两边同步：不要在两台机器上同时跑 git。
