---
aliases:
  - /professional/distributed/distributed-system-blog-02--primary-backup/
---

## 0 前言

### 0.1 Lab 1 解决了什么？

上一篇 blog 里，我们解决了一个根本问题：**网络不可靠**。

通过 Client 重试（At-Least-Once）和 Server 去重（At-Most-Once），我们实现了 Exactly-Once RPC。不管网络怎么丢包、延迟、重复，每个操作恰好执行一次。

```
Client                     Server
┌──────────────┐          ┌────────────────┐
│ Retry Logic  │ Command  │ AMOApplication │
│    (ALO)     │ ───────→ │     (AMO)      │
│              │ Result   │       ↓        │
│              │ ←─────── │  Application   │
└──────────────┘          └────────────────┘
```

看起来很完美。但有一个前提我们一直没提：

**Server 不会挂。**

### 0.2 Server 挂了会怎样？

```
Client                     Server
┌──────────────┐          ┌────────────────┐
│              │ Command  │                │
│              │ ───────→ │    💀 崩溃      │
│              │          │                │
│  一直重试...  │          │  数据全没了     │
│  一直重试...  │          │  AMO 历史没了   │
│  一直重试...  │          │  余额没了       │
└──────────────┘          └────────────────┘
```

Client 会不停重试，但永远不会收到回复。

更糟的是：即使我们重启 Server，它的内存状态已经丢失——用户的余额、交易记录、AMO 去重历史，全部归零。

这就是**单点故障（Single Point of Failure）**：整个系统的可用性取决于一台机器，它挂了，服务就挂了。

### 0.3 我们的新目标

Lab 1 的目标：在不可靠的**网络**上保证正确性。

Lab 2 的目标：在不可靠的**服务器**上保证可用性。


## 1 思路：保持两份

### 1.1 最直觉的想法

怎么防止一台机器挂了导致数据丢失？

**再加一台。**

始终让两台机器维护相同的状态。一台挂了，另一台还有完整的数据，可以立刻顶上继续服务。

这就是 **Primary-Backup** 的核心思路：

```
Client                Primary            Backup
┌──────┐            ┌──────────┐       ┌──────────┐
│      │  Request   │ key-value│       │ key-value│
│      │ ─────────→ │  store   │       │  store   │
│      │  Reply     │          │       │          │
│      │ ←───────── │ (服务请求) │       │ (备份数据) │
└──────┘            └──────────┘       └──────────┘
                     状态一致 ←──────→  状态一致
```

一台叫 **Primary**，负责接收和处理请求。一台叫 **Backup**，保持与 Primary 完全相同的状态，随时准备接替。

思路很简单，但多了一台机器，就多了一个问题：

一台机器的时候，一致性是免费的——只有一份数据，不存在"不一致"。

两台机器的时候，"两份数据始终一致"变成了需要主动维护的东西。

怎么维护？

## 2 正常运行：State Machine Replication

### 2.1 核心思想

两台机器各自维护一个状态机（比如 key-value store）。如果它们：

- 从相同的初始状态出发
- 按相同的顺序
- 执行相同的操作

那么它们的状态一定相同。

这就是 **State Machine Replication**。

听起来像废话，但这三个条件给了我们一个清晰的实现思路：让 Primary 决定操作顺序，然后把这个顺序强制同步给 Backup。

### 2.2 具体怎么做？

一个请求的完整生命周期：

```
Client              Primary              Backup
  │                    │                    │
  │  Put("x", 1)      │                    │
  │ ──────────────→    │                    │
  │                    │  Forward:          │
  │                    │  Put("x", 1)       │
  │                    │ ──────────────→    │
  │                    │                    │ 执行 Put("x", 1)
  │                    │       Ack          │
  │                    │ ←────────────────  │
  │                    │ 执行 Put("x", 1)   │
  │    Reply: OK       │                    │
  │ ←────────────────  │                    │
```

关键顺序：

1. Client 把请求发给 Primary
2. Primary 把请求**转发**给 Backup
3. Backup **先执行**，回复 Ack
4. Primary 收到 Ack 后**再执行**，回复 Client

### 2.3 为什么 Primary 要等 Backup？

为什么不能 Primary 先执行，再转发给 Backup？

```
场景：Primary 先执行再转发

Client              Primary              Backup
  │  Append("x","a")  │                    │
  │ ──────────────→    │                    │
  │                    │ 执行 → {x: "a"}    │
  │                    │  Forward           │
  │                    │ ──────────────→    │
  │    Reply: "a"      │                    │
  │ ←────────────────  │                    │
  │                    │        💀 崩溃      │
  │                    │                    │
  │                    │  (Forward 没到)     │

此时 Backup 被提升为新 Primary：
  Backup 的状态: {x: ""}   ← 没有 "a"
  Client 以为:   {x: "a"}  ← Append 成功了

不一致。
```

Client 收到了"成功"，但数据只存在于已经挂掉的 Primary 上。

**Primary 必须等 Backup 确认之后再执行和回复。** 这样，只要 Client 收到了回复，数据就一定在 Backup 上有一份。Primary 挂了也不怕。

### 2.4 一次只处理一个请求

如果 Primary 同时处理两个 Client 的请求会怎样？

```
Primary                          Backup
  │  Forward: Put("a", "foo")      │
  │ ────────────────────────────→   │
  │  Forward: Put("a", "bar")      │  
  │ ────────────────────────────→   │
  │                                 │

网络不保证顺序。

Primary 执行顺序: foo → bar  →  {a: "bar"}
Backup  执行顺序: bar → foo  →  {a: "foo"}

不一致。
```

State Machine Replication 要求相同顺序。如果并发发送，网络可能乱序，Backup 的执行顺序就可能和 Primary 不同。

所以 **Primary 一次只处理一个请求**：发出 Forward，等 Ack 回来，再处理下一个。

## 3 故障来了：谁说了算？

### 3.1 正常运行时一切都很美好

上面的流程有一个隐含前提：大家都知道谁是 Primary，谁是 Backup。

但如果 Primary 挂了呢？

```
Client              Primary              Backup
  │  Request          │                    │
  │ ──────────────→   💀                   │
  │                                        │
  │  (没回复...)                            │
  │  重试...                                │
  │  重试...           还是没回复            │
```

Backup 应该接管成为新 Primary。但——

**谁来做这个决定？**

### 3.2 让两台机器自己商量？

```
A: "你还活着吗？"
B: "......"  (没回复)
A: "你没回复，你挂了，我来当 Primary"

但同时：
B: "你还活着吗？"
A: "......"  (网络延迟，消息没到)
B: "你没回复，你挂了，我来当 Primary"

结果：A 和 B 都觉得自己是 Primary
```

这就是 **Split Brain**：两台机器都认为自己是 Primary，各自独立服务客户端，状态开始分叉。

两台机器之间无法区分"对方挂了"和"网络暂时不通"。靠它们自己协商，永远可能出现两个 Primary。

### 3.3 引入第三方：ViewServer

既然两个人吵不出结果，就找一个裁判。

```
                    ViewServer
                   ┌──────────┐
           Ping    │ View:    │    Ping
      ┌──────────→ │  #1      │ ←──────────┐
      │            │  P: A    │             │
      │   ViewReply│  B: B    │ ViewReply   │
      │ ←──────────│          │──────────→  │
      │            └──────────┘             │
   Server A                             Server B
   (Primary)                            (Backup)

   Client
      │  GetView
      │ ─────────→ ViewServer
      │ ←───────── (P: A, B: B)
      │
      │  Request
      │ ─────────→ Server A
```

**ViewServer** 是一个独立的仲裁节点，维护一个 **View**：

```
View = {
    viewNum:  当前编号（递增）,
    primary:  谁是 Primary,
    backup:   谁是 Backup
}
```

规则很简单：

- 每个 Server 定期向 ViewServer 发 **Ping**（"我还活着"）
- ViewServer 如果一段时间没收到某个 Server 的 Ping，就认为它挂了
- ViewServer 根据存活情况决定新的 View，通过 Ping 的回复告知各 Server
- Client 向 ViewServer 查询当前 Primary 是谁

### 3.4 View 的切换

```
View 1: Primary=A, Backup=B    (正常运行)
            │
            │  B 不再 Ping（挂了）
            ▼
View 2: Primary=A, Backup=C    (C 是空闲 Server，顶上来)
            │
            │  A 不再 Ping（挂了）
            ▼
View 3: Primary=C, Backup=nil  (没有空闲 Server 了)
```

有一条关键约束：

**新 View 的 Primary 必须是上一个 View 的 Primary 或 Backup。**

为什么？因为只有它们有最新的数据。如果直接让一台空闲 Server 当 Primary，它的状态是空的，之前所有的数据就丢了。

```
如果违反这条规则：

View 1: Primary=A, Backup=B
  A 和 B 都有数据: {x: "hello"}

View 2: Primary=C, Backup=nil   ← C 是空闲 Server
  C 的状态: {}

Client: Get("x") → KeyNotFound   ← 数据丢了
```

## 4 Split Brain 防御

### 4.1 View 不是瞬间切换的

ViewServer 决定了新 View，问题就解决了吗？

没有。ViewServer 知道新 View，不代表所有人都知道。

```
时刻 T1: ViewServer 决定 View 2: Primary=B, Backup=C

时刻 T2: 各节点的认知：
  ViewServer:  View 2 (P=B, B=C)
  Server B:    View 2 (P=B, B=C)  ✔️ 已更新
  Server A:    View 1 (P=A, B=B)  ❌ 还以为自己是 Primary
  Client:      View 1 (P=A, B=B)  ❌ 还在找 A
```

A 没挂，只是网络暂时不通，没收到新 View。它还在正常工作，以为自己是 Primary。

如果此时 Client 也还持有旧 View，它会把请求发给 A，A 会执行并回复。与此同时 B 也在以新 Primary 的身份服务其他 Client。

**两个 Primary，两条时间线，状态分叉。这就是 Split Brain。**

### 4.2 不要试图让所有人同时切换

一个自然的想法：能不能让 ViewServer 通知所有人，等大家都确认了再切换？

做不到。这本身就是一个分布式共识问题——消息可能丢、可能延迟，你没法保证所有节点在同一时刻看到同一个 View。

所以思路不是"让所有人同时切换"，而是：

**让旧 Primary 自己发现自己过时了。**

### 4.3 转发就是检测机制

回忆 Section 2 的正常流程：Primary 每次都要把操作转发给 Backup，等 Ack 才能继续。

这个转发不只是为了同步数据，它同时是一个 **split brain 检测机制**：

```
场景：A 还以为自己是 Primary

View 1: Primary=A, Backup=B
View 2: Primary=B, Backup=C   ← A 不知道

Client → A: Put("x", 1)

A 转发给 B（A 以为 B 还是自己的 Backup）：
  A ──── Forward(view=1, Put("x",1)) ────→ B

B 检查: 我当前是 View 2 的 Primary，这条消息的 view=1，过时了
  B ──── Reject ────→ A

A 收到拒绝: Backup 不认我了，说明 View 变了，我不再是 Primary
  A ──── Error ────→ Client

Client 去 ViewServer 查新 View，找到 B
```

整个防御链条：

1. **Primary 必须转发所有操作给 Backup**——包括读操作。如果读操作不转发，旧 Primary 可以独自服务读请求，永远不会发现自己过时。
2. **Backup 检查 View 号**——只接受来自当前 View 的 Primary 的转发。View 不对就拒绝。
3. **非 Primary 拒绝客户端请求**——即使 Client 拿着旧 View 直接找到旧 Backup，旧 Backup 也不会执行。

没有任何一条规则能单独防住 split brain，三条合在一起才构成完整的防线。

### 4.4 完整的 split brain 场景

把所有参与者串起来：

```
View 1: Primary=A, Backup=B
View 2: Primary=B, Backup=C

参与者各自的认知可能不同步，但系统仍然安全：

情况 1: Client 找 A（旧 Primary）
  Client → A → A 转发给 B → B 拒绝（view 不对）→ A 返回 Error
  Client → ViewServer → 得到 View 2 → 找 B → 正常执行
  ✔️ 安全

情况 2: Client 找 B（新 Primary，但还没有 Backup C 的状态同步）
  B 在做 state transfer → 拒绝请求 → Client 重试
  ✔️ 安全

情况 3: Client 找 A，A 没有 Backup（View 2 没有把 A 列为任何角色）
  A 以为自己还是 Primary，但转发给 B 被拒绝
  A 无法完成任何操作
  ✔️ 安全
```

关键 insight：**系统不需要所有人都知道最新 View，只需要旧 Primary 无法独自完成一个操作。** 转发机制保证了这一点——它必须经过 Backup，而 Backup 会校验 View。

## 5 安全换人：State Transfer

### 5.1 新 Backup 的问题

View 切换时，新 Backup 可能是一台刚加入的空闲 Server，状态为空：

```
View 1: Primary=A, Backup=B
  A: {x: "hello", y: "world"}
  B: {x: "hello", y: "world"}

B 挂了 → View 2: Primary=A, Backup=C

  A: {x: "hello", y: "world"}
  C: {}                          ← 什么都没有
```

如果此时 A 也挂了，C 被提升为 Primary，所有数据就丢了。

所以在新 View 开始正常服务之前，Primary 必须先把完整状态发给新 Backup。这就是 **State Transfer**。

### 5.2 State Transfer 的流程

```
Primary (A)                          New Backup (C)
    │                                      │
    │  StateTransfer(完整的 AMOApplication)  │
    │ ────────────────────────────────────→ │
    │                                      │ 用收到的状态覆盖自己的状态
    │             Ack                      │
    │ ←──────────────────────────────────── │
    │                                      │
    │  (现在可以开始正常转发操作了)            │
```

传的是什么？整个 AMOApplication——包括业务状态（key-value store）和 AMO 去重历史。缺了去重历史，Backup 就无法正确去重，Exactly-Once 语义就破了。

### 5.3 Transfer 期间不能处理请求

为什么？看这个场景：

```
Primary (A)                          New Backup (C)
    │                                      │
    │  StateTransfer({x: "foo"})           │
    │ ────────────────────────────────────→ │
    │                                      │
    │         (Ack 还没回来)                 │
    │                                      │
Client → A: Put("x", "bar")               │
    │                                      │
    │  Forward: Put("x", "bar")            │
    │ ────────────────────────────────────→ │
    │                                      │ 执行 Put → {x: "bar"}
    │                                      │
    │                                      │ 然后 StateTransfer 到达
    │                                      │ 覆盖 → {x: "foo"}
    │                                      │
    │              Ack                     │
    │ ←──────────────────────────────────── │

A 执行 Put → {x: "bar"}
C 的状态:     {x: "foo"}   ← 被 StateTransfer 覆盖了

不一致。
```

**所有操作必须在 State Transfer 之前或之后，不能同时。** Primary 在 transfer 完成之前，应该拒绝客户端请求。

### 5.4 ViewServer 必须等 Primary 确认

还有一个更微妙的问题：如果 ViewServer 不等 Primary 确认就继续推进 View 会怎样？

```
View 1: Primary=A, Backup=B
  B 挂了
View 2: Primary=A, Backup=C    ← ViewServer 推进了
  A 还没来得及做 State Transfer 给 C
  A 挂了
View 3: Primary=C, Backup=nil  ← ViewServer 又推进了

C 的状态: {}   ← 从来没收到过 State Transfer
数据全丢。
```

问题出在哪？ViewServer 推进到 View 3 的时候，View 2 的 State Transfer 还没完成。C 被提升为 Primary，但它的状态是空的。

所以：**ViewServer 必须等当前 View 的 Primary 确认（Ack）之后，才能切换到下一个 View。**

Primary 的确认意味着：我已经知道当前 View 是什么，并且已经完成了 State Transfer。在此之前，Primary 用旧 View 号 Ping ViewServer，ViewServer 就知道还不能推进。

```
理想流程：

View 1: Primary=A, Backup=B
  B 挂了

ViewServer 决定 View 2: Primary=A, Backup=C
  但 A 还在 Ping(view=1) → ViewServer 不推进

A 收到 View 2 → 开始 State Transfer 给 C
  A ──── StateTransfer ────→ C
  C ──── Ack ────→ A

A 确认完成 → Ping(view=2) → ViewServer 知道 View 2 已经稳定

此后即使 A 挂了：
  View 3: Primary=C, Backup=nil
  C 有完整数据 ✔️
```

### 5.5 State Transfer 的幂等性

State Transfer 消息可能因为网络重复到达。如果 Backup 每次收到都覆盖自己的状态：

```
Primary                          Backup
    │  StateTransfer({x: "foo"})    │
    │ ────────────────────────────→ │  覆盖 → {x: "foo"}
    │                               │
    │  (正常转发操作)                 │
    │  Forward: Put("x", "bar")    │
    │ ────────────────────────────→ │  执行 → {x: "bar"}
    │                               │
    │  StateTransfer({x: "foo"})    │  ← 重复到达！
    │ ────────────────────────────→ │  覆盖 → {x: "foo"}  ← 倒退了
```

所以 **Backup 每个 View 只执行一次 State Transfer**。收到重复的 StateTransfer 消息时，不覆盖状态，但仍然回复 Ack（否则 Primary 会一直重发）。

## 6 实现视角：Server 的状态机

### 6.1 回头看：Server 在任意时刻在干什么？

整篇 blog 讲了很多规则和场景，但回到实现层面，一个 Server 在任意时刻其实只可能处于四种模式之一：

**ACTIVE**：正常工作。我是 Primary，有一个已同步的 Backup，可以接收客户端请求、转发、执行、回复。

**FORWARDING**：等待 Backup 确认。我把操作转发给了 Backup，在等 Ack。这期间不能处理下一个请求（Section 2.4，一次只处理一个）。

**TRANSFERRING**：正在做 State Transfer。我是 Primary，新 View 给了我一个新 Backup，我在把完整状态发给它。这期间必须拒绝客户端请求（Section 5.3）。

**AWAITING_TRANSFER**：等待接收 State Transfer。我是新 Backup，刚被 ViewServer 指派，但还没收到 Primary 的状态。这期间不能接受转发的操作——我的状态是空的，执行了也是错的。

### 6.2 这四种模式是互斥的

一个 Server 不可能同时在做 State Transfer 又在处理客户端请求——Section 5.3 说了，这会导致 Transfer 覆盖已执行的操作。

一个 Server 不可能同时在等 Backup 确认又在等接收 Transfer——前者是 Primary 的行为，后者是 Backup 的行为。

这种互斥性直接映射成一个 enum：

```java
enum State {
    ACTIVE,
    FORWARDING,
    TRANSFERRING,
    AWAITING_TRANSFER
}
```

不需要多个 boolean，不需要自己维护"这些状态不能同时为 true"。编译器帮你保证。

### 6.3 状态决定行为

有了这个 enum，Server 收到任何消息时的第一件事就是看自己的状态，然后决定接受还是拒绝：

```
收到客户端请求:
  ACTIVE         → 接受，转发给 Backup，进入 FORWARDING
  FORWARDING     → 拒绝（还在等上一个请求的 Ack）
  TRANSFERRING   → 拒绝（State Transfer 还没完成）
  AWAITING_TRANSFER → 拒绝（我不是 Primary）

收到 Backup 的 Forward Ack:
  FORWARDING     → 执行操作，回复 Client，回到 ACTIVE
  其他状态        → 忽略（过时的 Ack）

收到 State Transfer:
  AWAITING_TRANSFER → 覆盖状态，回复 Ack，进入 ACTIVE
  ACTIVE            → 已经同步过了，不覆盖，但回复 Ack
  其他状态           → 忽略

收到新 View（通过 Ping 回复）:
  根据新 View 里自己的角色和是否有新 Backup，
  切换到对应状态
```

前面五个 Section 讲的所有规则——转发、等待确认、拒绝请求、State Transfer 的原子性——在实现里都变成了这张表。

**每种状态定义了 Server 该接受什么、拒绝什么。** 协议的正确性，最终落在状态转换的正确性上。


## 7 局限性

Primary-Backup 能容忍一台 Server 故障。但它的容错能力到此为止，有几个没解决的问题：

**ViewServer 是单点故障。** 整套机制依赖 ViewServer 做仲裁，但 ViewServer 自己只有一台。它挂了，就没人能决定新的 View，系统卡死。讽刺的是，我们为了解决单点故障引入了 Primary-Backup，结果制造了一个新的单点故障。

**Primary 确认前挂了，系统卡死。** ViewServer 必须等 Primary 确认当前 View 才能推进。如果 Primary 在确认之前就挂了，ViewServer 永远等不到确认，也永远无法切换到下一个 View。

**不能容忍同时宕机。** 如果 Primary 和 Backup 同时挂了，数据就丢了。没有第三份副本。

**State Transfer 是全量的。** 每次换 Backup 都要把完整状态发过去。如果数据量很大，Backup 只是断网几秒钟又回来了，也得重新传全部数据。

这些问题的根源是一样的：**两台机器加一个裁判，能做的事情是有限的。**

要去掉 ViewServer 这个单点故障，就需要让多台机器自己达成共识——谁是 Primary，当前状态是什么。这正是 Lab 3 的主题：**Paxos**。

下一步：
[Distributed System Blog 03 – Paxos](/blogs/professional/distributed/distributed-system-blog-03--paxos/)