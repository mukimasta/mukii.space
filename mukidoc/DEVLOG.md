# Devlog

### 2026-03-11

1. 用 Hugo 和 dario 主题建站，部署到 Cloudflare Workers。之后陆续加入分布式系统和算法文章、《青叶树》、在西雅图的写作、Professional 与 Journey 两页、SoundMat 主页和文档。

### 2026-11-16

1. Blog Bot 开始长期照看网站，第一次巡检：站内 140 个页面全部正常。补了仓库 README，清理了 `.DS_Store` 和一个残留的模板副本。
2. 发现提交进 git 的 `public/` 会随每次构建留在线上（见 DECISION 1），移出 git 后七十多个老网址下线。

### 2026-11-17

1. 改版：网站换成从 dario 改出来的自有主题 `themes/mukii`，样子参考 paco.me。单栏、一种字色、两种字号，Inter 加思源黑体并按用字裁剪，深色模式默认跟随系统，`---` 显示为空心菱形。设计前后做了六轮样稿，试过衬线（Palatino 加宋体）和几款英文字体后定下。规则记在 `design/VISUAL_DESIGN.md`。
2. 网站标题改为 mukii.space，页脚保留 © MUKIMASTA。页头暂时去掉 Professional 和 Journey 的入口。
3. 项目开始用 MukiDoc 维护文档。
4. 加了 `video`、`bilibili` 短代码，并覆盖了自带的 `youtube`，三种视频版式一样。视频文件放在 `media.mukii.space`。
