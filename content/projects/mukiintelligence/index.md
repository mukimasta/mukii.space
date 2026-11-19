---
title: "MukiIntelligence：我的个人 AI 体系"
date: 2026-11-18
draft: false
---

**Agent 公司**

从同步的、一次性的、基于任务的、被动的 Agent，到异步的、持久的、基于项目与职责的、自主的 Agent。
每个 Bot 拥有长期职责，24 小时自主推进项目。

![MukiIntelligence 架构](0-architecture.svg)

{{< side img="1-world.svg" width="60%" align="center" >}}
**MukiWorld**　我的个人上下文：学业、工作、项目、生活都在一棵节点树里，Mac 和 Jetson 两边自动同步。
{{< /side >}}

{{< side img="2-doc.svg" width="60%" align="center" >}}
**[MukiDoc](https://github.com/mukimasta/mukidoc)**　给 Agent 用的文档协议：理念、架构和设计链都有固定的结构，AI 写代码时一起维护文档。
{{< /side >}}

{{< side img="3-bots.svg" width="60%" align="center" >}}
**MukiBots**　常驻的 Agent，有身份和记忆，自己醒来、推进负责的项目，做完写下记忆再睡去。
{{< /side >}}

{{< side img="4-coflow.svg" width="60%" align="center" >}}
**CoFlow**　每个项目节点记着负责人和状态，负责人可以是我，也可以是一个 Bot。
{{< /side >}}

{{< side img="5-cards.svg" width="60%" align="center" >}}
**MukiCards**　人和 Agent 之间异步来往的卡片：一件事一个线程，加一张卡片就叫醒对方。
{{< /side >}}

{{< side img="6-board.svg" width="60%" align="center" >}}
**MukiBoard**　电脑上的看板和桌上的墨水屏，所有卡片一眼看到，点一下就回应。
{{< /side >}}
