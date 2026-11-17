# Overview

mukii.space 是 Hanlin 的个人网站：放他的写作、作品和技术文章，也是别人认识他的一个入口。它用 Hugo 从仓库里的 Markdown 生成，推到 GitHub 后由 Cloudflare 自动构建发布。

**解决什么问题。** Hanlin 写的东西散在不同时期、不同地方：中学到大学的散文已经编成了《青叶树》，在西雅图又写了新的；学分布式系统时留下了一系列笔记；SoundMat 这样的项目有自己的主页和十几篇文档。它们需要一个属于他自己、长期可访问、读起来舒服的地方，而不是借别人的平台和别人的样子。

**交付物。**

1. 网站 mukii.space：首页、技术文章（Professional）、《青叶树》、在西雅图的写作、SoundMat 文档，以及 Professional、Journey 两个专页。
2. SoundMat 主页（`/soundmat/`、`/soundmat/en/`）：同一个站点下的独立单页，有自己的设计和生成脚本。
3. 网站自己的主题 `themes/mukii`：版式、字体、深色模式等，规则见 `design/VISUAL_DESIGN.md`。

**用户场景。** Hanlin 在西雅图写完一篇散文，把 Markdown 放进 `content/articles/seattle-writing/`，在目录页加一行链接，推上去。几分钟后文章出现在网站上，用和全站一致的字体和排版。他把链接发给朋友，朋友在手机上打开，读完顺着返回链接回到"在西雅图的写作"，又点开了另外几篇。

mukii.space 希望 Hanlin 的文字和作品有一个清楚、安静、属于他自己的家。

当前状态：网站在线。2026-11 完成改版，换成了从 dario 改出来的自有主题；Professional 和 Journey 两页暂时没有站内入口。
