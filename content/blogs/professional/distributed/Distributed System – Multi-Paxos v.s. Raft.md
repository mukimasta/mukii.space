---
aliases:
  - /professional/distributed/distributed-system--multi-paxos-v.s.-raft/
---

## 本质关系

Raft 本质上是 Multi-Paxos 的一个特化实现。Lamport 提出 Paxos 时只定义了单值共识，Multi-Paxos 是将多轮 Paxos 串联成连续日志的工程延伸，但论文没给出完整的工程规范，留下了大量实现空间。Raft 的贡献在于：用"可理解性优先"的设计哲学，把这些空间填上了，给出了一个开箱即用的完整协议。

## 从 Multi-Paxos 到 Raft：三条约束的演进

### 起点：Multi-Paxos

Multi-Paxos 把多轮 Basic Paxos 串联成连续的日志槽位（log slots），每个 slot 独立运行一轮共识。它非常自由：

- 任何节点都可以做 proposer
- 多个 proposer 可以并发提案
- 不同 slot 可以被不同 proposer 决议
- 日志允许出现空洞

这种自由带来了极大的灵活性，但也带来了工程上的极大挑战：空洞填补、乱序提交、多 proposer 冲突、leader 切换后状态恢复……Lamport 的论文没有给出这些问题的标准答案。

Raft 的做法是：在 Multi-Paxos 的基础上，加三条约束，从设计层面优化这些问题。

### 约束一：强制单 Leader（Strong Leader）

Multi-Paxos： leader 是可选优化。没有 leader 时，任何节点都可以 Prepare → Accept，多个 proposer 靠 proposal number 竞争，可能活锁。实践中大家都会选一个 stable leader 来跳过 Prepare 阶段，但协议本身不保证唯一性。

Raft： 每个 term 内最多一个 leader，所有客户端写请求必须经过 leader。这不再是优化，而是协议的核心不变量。

消灭了什么问题： 多 proposer 冲突、活锁、提案冲突解决。

### 约束二：日志连续，不允许空洞（No Gaps）

Multi-Paxos： 每个 slot 独立决议，slot 5 可能已经 committed 但 slot 3 还是空的。新 leader 上任后，需要对每一个空洞 slot 重新跑一轮 Paxos 来确认值。

Raft： 日志必须严格连续。Leader 用 `prevLogIndex` + `prevLogTerm` 做一致性检查，follower 不匹配就拒绝，leader 回退 `nextIndex` 直到找到分歧点，然后覆盖写。

消灭了什么问题： 空洞填补逻辑、乱序提交、快照截断的边界情况。日志变成了一个简单的 append-only 数组。

### 约束三：选举限制（Election Restriction）

Multi-Paxos： 任何节点都可以尝试成为新 leader。新 leader 上任后，必须对所有未确认的 slot 跑 Prepare 阶段，从多数派收集可能已经 accept 的值，然后 re-propose，以确保不丢失已提交的决议。正确但复杂。

Raft： 候选人的日志必须"至少和多数派一样新"（比较 lastLogTerm 和 lastLogIndex）才能赢得选举。这就从选举阶段直接保证了：新 leader 一定已经拥有所有已提交的条目，不需要额外的日志恢复流程。

消灭了什么问题： leader 切换后的日志恢复（最复杂也最容易出 bug 的部分）。

## 共识算法的工业应用：从 Paxos 到 Raft

### Paxos 时代（2006–2013）

Paxos 1990 年提出，但真正进入工业界是 2006 年 Google 发表 Chubby 和 Spanner 论文之后。问题是 Lamport 只定义了 Basic Paxos（单值共识），Multi-Paxos 怎么工程化，论文里几乎没写。结果每家实现出来的都不一样，GitHub 上大量 Paxos 实现被发现有正确性问题。这个阶段能驾驭 Paxos 的基本只有 Google 级别的团队。

同期 ZooKeeper 的 ZAB 协议走了折中路线：类 Multi-Paxos 思想 + 大量工程简化，成了 Hadoop 生态的标配。ZAB 的成功其实已经说明了一件事：工业界需要的不是理论优雅，而是能用、能懂、能调试。

### Raft 及其生态（2014 至今）

2014 年 Raft 论文发表，本质就是在 Multi-Paxos 上加三条约束（强制单 Leader、日志无空洞、选举限制），换来完整的伪代码级规范，照着论文就能实现正确的版本。此后新项目几乎一边倒选 Raft：

- **etcd** — Raft 的标杆实现，后来成了 Kubernetes 的核心存储，整个云原生基础设施的心脏
- **TiKV / TiDB** — Multi-Raft 架构（每个数据分片一个 Raft 组），分片的 split/merge/调度全靠日志连续性才可控
- **CockroachDB** — 定位开源版 Spanner，但选了 Raft 而不是 Multi-Paxos，因为开源项目需要社区贡献者能看懂代码
- **百度 braft** — 国内 C++ 生态的事实标准 Raft 库，大量国内大厂的分布式存储底层在用

行业共识基本是：**除非有特殊理由，否则默认选 Raft。**

### 仍然坚持 Paxos 的，都有充分理由

**Google Spanner** — 全球级跨数据中心部署，需要精细控制副本放置和 leader 地理位置偏好，Multi-Paxos 的灵活性是刚需，而且 Google 有能力驾驭其复杂性。

**OceanBase（蚂蚁）** — 2024 VLDB 的 PALF 论文解释了原因：Raft 要求候选人日志必须最新才能当选，在三副本场景下，用户指定的高优先级副本可能因为日志稍旧而无法当选。Multi-Paxos 没有这个限制，新 leader 通过 Reconfirmation 补齐日志即可。对金融级数据库来说，"哪个机房优先接管"是硬需求。不过 OB 实际上也大量借鉴了 Raft 的设计，已经是两者的混血。

**微信 PaxosStore / PhxPaxos（腾讯）** — 微信存储对并发写入要求极高，Multi-Paxos 天然支持并发提案，Raft 的强制单 Leader 做不到。但 PhxPaxos 开源后几乎没有外部项目敢用——Paxos 出了 bug，日志看不懂。

一个反向案例：**PolarDB（阿里云）** 用 Parallel-Raft，在 Raft 基础上放松日志连续性约束，允许乱序复制和提交，相当于从 Raft 往 Multi-Paxos 方向退了一步，用实现复杂度换并发性能。


Paxos 开创了共识算法但太难实现，Raft 通过加约束让它可工程化，拿下了绝大多数场景。仍然选 Paxos 的团队，需要的恰恰是 Raft 为了简洁而牺牲掉的灵活性——并且有能力为这些灵活性买单。
