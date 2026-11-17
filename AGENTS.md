# AGENTS

本项目用 MukiDoc 维护长期上下文，先读协议 MUKIDOC_PROTOCOL.md。

## 本项目

- 上级约定见 Worlds 根目录的 `AGENTS.md`。这个仓库在 Worlds 里两台机器同步：不要在 Mac 和 Jetson 上同时跑 git，只看一眼用 `git --no-optional-locks status`。
- 网站长期由 Blog Bot（blog-bot）照看，节点 `MUKIMASTA/BLOG` 的负责人是 Hanlin。改动先告诉他，他同意了再推到 `master`；推上去就是公开发布。
- 内容是 Hanlin 的：`content/` 里的文字不改意思、不改文风，也不替他写。排版、呈现和网站本身可以提议、动手。
- 改样式先读 `mukidoc/design/VISUAL_DESIGN.md`，那里的规则是和 Hanlin 一起定下的。
- 本地预览和构建见 `mukidoc/implementation/BUILD.md`。改动推上去之前，先在本地构建一次，挑几类页面截图看过。
- 别把 `public/` 提交进 git（原因见 `mukidoc/DECISION.md`）。
