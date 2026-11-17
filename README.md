# mukii.space

Hanlin 的个人网站。Hugo 构建，主题 [dario](https://github.com/GrantBirki/dario)（submodule，在 `themes/dario`）。

## 发布

推到 `master`，Cloudflare Workers 自动跑 `build.sh`（装 Hugo 等，再 `hugo build`），发布 `public/`。配置在 `wrangler.toml`。

本地预览：`hugo server`（需要 Hugo extended）。

## 目录

| 位置 | 内容 |
|---|---|
| `content/` | 文章：`blogs/professional/`（技术）、`qingyeshu/`（青叶树）、`articles/`（散文）、`soundmat/docs/`（SoundMat 文档） |
| `layouts/` | 自己写的模板，覆盖主题；Journey、Professional 两页各有专门的 layout |
| `assets/css/custom.css` | 自定义样式 |
| `static/` | 原样复制的文件：图片、SoundMat 主页、LifeLab 页面 |
| `soundmat-home/` | SoundMat 主页的源文件，不走 Hugo，见 [它的 README](soundmat-home/README.md) |

各目录的 `_index.md` 里，文章列表是手写的链接，加文章时要一起更新。

## 注意

- 仓库在 Worlds 里，Mac 和 Jetson 两边同步：不要在两台机器上同时跑 git。
- Worlds 同步不传名为 `build` 的东西，所以 `themes/dario/script/build` 在本地总是显示删除，这不是真的改动，别提交。
