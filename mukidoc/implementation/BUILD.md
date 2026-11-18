# Build

当前怎样构建、预览和发布网站，以及容易踩到的地方。

### 发布

推到 `master`，Cloudflare Workers 运行 `build.sh`：下载并安装 Dart Sass、Go、Hugo（0.156.0 extended）、Node.js，然后 `pip install fonttools brotli`，运行 `scripts/build_fonts.py` 裁剪字体，最后 `hugo build --gc --minify`。产物目录是 `public/`，由 `wrangler.toml` 指定。

Hugo 生成 `public/` 时不会先清空它。`public/` 一旦被提交进 git，里面的旧文件就会跟着每次发布留在线上。所以 `public/` 在 `.gitignore` 里，不能提交。

### 字体

`scripts/build_fonts.py` 从 google/fonts 下载 Inter 和思源黑体的可变字体，放在 `.fontcache/`（不进 git），扫描 `content/`、`layouts/`、`themes/mukii/layouts/` 和 `hugo.toml` 里出现的字符，裁剪后写成 `themes/mukii/static/fonts/inter.woff2` 和 `noto-sans-sc.woff2`。另外固定保留 ASCII、拉丁扩展和常用中英文标点。

生成的两个字体文件也提交进仓库：Cloudflare 上 pip 或下载失败时，`build.sh` 跳过裁剪，用仓库里的版本照常发布，只是新文章里新出现的汉字会退回系统字体。本地加了新文章想预览，跑一次 `python3 scripts/build_fonts.py`。

2026-11 时 Inter 裁剪后约 62 KB，思源黑体约 620 KB（2693 字）。Jetson 系统自带的 fonttools 版本较旧（4.29），无法把思源黑体的字重范围裁到 400–600（它的默认字重是 100），所以思源黑体保留了完整的字重轴；Cloudflare 上 pip 装的新版行为相同，因为脚本里没给它设范围。

### 本地预览

Jetson 上的 Hugo 在 `~/.local/hugo-0.156/hugo`（和 Cloudflare 同版本）。在仓库根目录：

```sh
~/.local/hugo-0.156/hugo server --bind 100.124.252.60 --port 1313 --baseURL http://100.124.252.60:1313/
```

绑在 Jetson 的 Tailscale 地址上，Hanlin 在 Mac 上用 `http://100.124.252.60:1313/` 打开；只在 Jetson 本机看可以绑 `127.0.0.1`。

### 视频

文章里的 HTML 会被 Hugo 删掉（没开 `unsafe`），视频用短代码嵌入，模板在 `layouts/shortcodes/`：

```
{{< video src="https://media.mukii.space/目录/文件.mp4" poster="封面图" caption="说明" >}}
{{< bilibili BV1k14y1U7LQ >}}
{{< youtube vNwYtllyt3Q >}}
```

`poster`、`caption` 可以不写；`bilibili` 可以加 `page="2"` 选分 P，`youtube` 可以加 `start="30"` 从第几秒开始。`youtube` 覆盖了 Hugo 自带的同名短代码，好让三种的版式一样。

视频文件放在 `media.mukii.space`（Cloudflare R2），不放进仓库：Cloudflare Workers 的静态文件单个上限 25 MiB，大了构建会失败，而且仓库会一直背着它。文件名用英文，免得网址被转码。

### 主题的来源

`themes/mukii` 是从 dario（GrantBirki/dario，MIT）复制进来改的，原许可保留在 `themes/mukii/LICENSE`。模板骨架、深色模式和脚注脚本、分享预览图沿用 dario 的结构；样式整份重写。

### Worlds 同步

仓库在 Worlds 里，Mac 和 Jetson 自动同步。不要在两台机器上同时跑 git。Worlds 同步不传名字叫 `build`、`dist`、`target` 的文件夹。
