---
title: "系统设计：AI 私聊答疑助手"
date: 2026-11-18
draft: false
---


{{< side img="11-chat-list.svg" width="60%" align="center" >}}
**聊天**　运营同时对着几十个商家，未读常常 99+，很多问题规则文档里其实有答案。
{{< /side >}}

{{< side img="12-authorize.svg" width="60%" align="center" >}}
**接入**　扫码授权、打开开关就能用，只监听授权名单里的商家。
{{< /side >}}

{{< side img="13-settings.svg" width="60%" align="center" >}}
**AI 回复设置**　选回复风格和知识库，常见问题可以直接写成模板。
{{< /side >}}

{{< side img="14-workbench.svg" width="60%" align="center" >}}
**工作台**　有把握的 AI 直接回，拿不准的交给运营确认后再发。
{{< /side >}}

{{< side img="15-dashboard.svg" width="60%" align="center" >}}
**管理台**　看收到、回复、发出的数量和采纳率。
{{< /side >}}

{{< side img="16-review.svg" width="60%" align="center" >}}
**评测台**　对照依据和理由，一条条判断 AI 回得对不对。
{{< /side >}}

## 它怎么运作

![架构设计](21-architecture.svg)

{{< side img="22-servers.svg" width="60%" align="center" >}}
**多机服务**　4 台服务器，每次请求随机分到一台执行，所以不能指望上一次在哪台。
{{< /side >}}

{{< side img="23-cloud-db.svg" width="60%" align="center" >}}
**云端数据库为唯一依据**　状态全存在云端，服务器重置换了一台，运营也不用重新登录。
{{< /side >}}

{{< side img="24-cli-service.svg" width="60%" align="center" >}}
**分布式聊天软件 CLI 服务**　把 CLI 包成登录、登出、续期、调用四个入口，每次调用前从云端拉凭证，业务代码像在单机上一样用。
{{< /side >}}

{{< side img="25-cli-conflicts.svg" width="60%" align="center" >}}
**要处理的冲突**　没有它，凭证散在各台机器上，会出现未登录和凭证失效；有了它，还要处理同时续期、续期时登出、发送超时等冲突。
{{< /side >}}

{{< side img="26-session-state.svg" width="60%" align="center" >}}
**按会话，不按消息**　商家常把一个问题拆成几条发，所以等 15 秒没有新消息才交给 AI；运营自己接话了，AI 就让开。
{{< /side >}}

{{< side img="27-ai-io.svg" width="60%" align="center" >}}
**相信 AI**　不用规则限制它，而是讲清身份、给足上下文和配置，让它用 JSON 回复什么、回哪条、依据、理由和把握。
{{< /side >}}

{{< side img="28-optimize.svg" width="60%" align="center" >}}
**优化回复策略**　用自动化评测、人工打分和用户访谈找问题：回复方式不对就改提示词（共 14 版），知识库缺了就协调补上。采纳率从约 10% 提到 35%。
{{< /side >}}

