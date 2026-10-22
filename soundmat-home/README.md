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
