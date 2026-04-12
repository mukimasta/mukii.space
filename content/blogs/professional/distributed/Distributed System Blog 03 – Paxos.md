---
aliases:
  - /professional/distributed/distributed-system-blog-03--paxos/
---

（知乎好文）比喻解释 Paxos 算法：
[如何浅显易懂地解说 Paxos 的算法？ - 知乎](https://www.zhihu.com/question/19787937/answer/107750652)



Paxos 这里我遇到了两个 bug，以下是修复记录

### Bug 1 及修复：P2B 语义混淆导致错误计票

在实现 Multi-Paxos 分布式 KV Store 的过程中，我遇到了一个和消息乱序相关的 bug。这个 bug 在正常运行时不会触发，只在 leader 切换叠加网络延迟的特定时序下才会暴露，但一旦触发就会违反 Paxos 的线性一致性（Linearizability）保证。

#### 背景

Multi-Paxos 的 Phase 2 流程是：Leader 向 Acceptor 发送 P2A(ballot, slot, command)，Acceptor 判断这个 ballot 是否不小于自己当前的 acceptorBallot，如果是就接受并回复 P2B，否则拒绝。Leader 收到多数派的 P2B 确认后，将该 slot 标记为 chosen 并提交。

#### Bug 触发场景

假设集群中发生了一次 leader 切换，旧 leader 的 ballot 是 B_old，新 leader 通过 Phase 1 确立了 B_new。**此时网络上仍然存在旧 leader 之前发出的 P2A(B_old)，因为网络延迟刚刚到达某个 Acceptor。**

我最初的实现中，reject 分支仍然会回复一个 P2B(acceptorBallot)。**本意是作为"拒绝"信号**——让旧 leader 看到更高的 ballot 后主动退位。但在特定时序下，这个本意为"拒绝"的回复，**被新 leader 误认为了"同意"。**

#### 修复前：reject 回复导致语义混淆

```
时间轴 →

旧 Leader (B_old)          Acceptor                    新 Leader (B_new)
      |                        |                              |
      |--- P2A(B_old) ------->|  (网络延迟，迟到)              |
      |                        |                              |
      |                        |  acceptorBallot 已是 B_new    |
      |                        |  B_old < B_new → reject!     |
      |                        |                              |
      |                        |--- P2B(B_new) -------------->|
      |                        |                              |
      |                        |    本意：拒绝信号              |
      |                        |    实际：B_new == leaderBallot |
      |                        |         → 被计入 accept 计数！ |
      |                        |                              |
      |                        |              slot 拿到"多数派"确认
      |                        |              → 错误 chosen → 提交
      |                        |              → ❌ 线性不一致！
```

问题的根因在于：P2B 消息承载了两种不同的语义——accept 确认和 reject 通知——但消息本身没有任何字段区分这两种语义。正常情况下可以通过 ballot 大小隐式区分（相等 = accept，更大 = preempt），但在 leader 切换 + 消息乱序的 corner case 下，reject 回复里的 acceptorBallot 恰好等于新 leader 的 ballot，隐式区分失效，导致一个 Acceptor 根本没有 accept 的 slot 被错误计入多数派，最终一个没有被多数派真正接受的值被提交，**违反线性一致性**。

#### 修复后：reject 不回复，语义清晰

```
时间轴 →

旧 Leader (B_old)          Acceptor                    新 Leader (B_new)
      |                        |                              |
      |--- P2A(B_old) ------->|  (网络延迟，迟到)              |
      |                        |                              |
      |                        |  acceptorBallot 已是 B_new    |
      |                        |  B_old < B_new → reject!     |
      |                        |                              |
      |                        |  直接 return，不发 P2B         |
      |                        |                              |
      |                        |              新 Leader 不会收到
      |                        |              虚假的 accept 回复
      |                        |              → ✅ 安全
```

修复方法是 reject 分支直接 return，不发送任何 P2B 回复。旧 leader 不会收到主动的 preempt 通知，但它会通过心跳超时或下一次 Phase 1 失败发现自己已经被抢占，正确性不受影响。

这个修复牺牲了一点 preemption 检测的速度，换来了消息语义的清晰性和协议的正确性。另一种可行的修法是在 P2B 中增加一个 accepted/rejected 标记字段来显式区分语义，但对于这个场景，不回复是更简单也更安全的方案。

#### 启发

分布式系统中，任何一条消息都可能在"错误"的时间到达"错误"的接收者。设计消息格式时，不能依赖隐式的上下文假设（比如"这个回复一定会回到发送 P2A 的那个 leader"），每条消息的语义必须是自包含且无歧义的。一个本意为"拒绝"的回复，在消息乱序的场景下被误读为"同意"，就足以打破整个系统的线性一致性保证。


## Bug 2：消息丢失导致 Slot 卡在 ACCEPTED 状态，阻塞日志执行

### 问题

Multi-Paxos 要求日志按 slot 顺序执行（apply）——slot 5 必须在 slot 4 之后执行，即使 slot 5 已经被 chosen。这意味着任何一个 slot 如果卡住，后面所有 slot 都会被阻塞。

在网络不可靠的环境下（消息可能丢失），一个 slot 完成了 Phase 2 的部分流程后，P2A 或 P2B 消息被丢弃，导致该 slot 停留在 ACCEPTED 但始终无法推进到 CHOSEN。后续所有 slot 即使已经 CHOSEN，也无法执行。

```
Slot:     1        2        3        4        5
状态:   CHOSEN   CHOSEN   ACCEPTED  CHOSEN   CHOSEN
                           ↑ P2B 丢失，卡住
                           |
执行:   ✅ 已执行  ✅ 已执行  ❌ 阻塞    ❌ 等待    ❌ 等待
                           |
                    整条流水线停滞 → 客户端超时
```

### 为什么仅靠客户端重试不够

一个自然的想法是：客户端超时后重新发送请求，leader 重新走 Phase 2，slot 就能推进了。但这只能覆盖客户端请求对应的 slot。Multi-Paxos 中还有一类特殊的 slot——**NO-OP slot**，它们是 leader 切换后在 Phase 1 中发现的、需要用空操作填补的日志空洞。NO-OP 没有对应的客户端，永远不会有人来重试。如果 NO-OP slot 的 P2A/P2B 丢了，这个 slot 就永远卡在 ACCEPTED，整条日志永久阻塞。

```
场景：Leader 切换后填补日志空洞

Slot:     1        2        3        4        5
内容:   PUT(a,1)  NO-OP   PUT(b,2)  PUT(c,3)  PUT(d,4)
状态:   CHOSEN   ACCEPTED  CHOSEN   CHOSEN    CHOSEN
                  ↑ NO-OP 的 P2B 丢失
                  |
                  没有客户端会重试这个 NO-OP
                  → 永久阻塞
```

### 修复：在心跳定时器中重试未完成的 Phase 2

我的修复方案是复用已有的 HeartbeatTimer：leader 每次发送心跳时，扫描所有处于 ACCEPTED 但未 CHOSEN 的 slot，重新发送 P2A。

```
修复前：

Leader                     Acceptor
  |--- P2A(slot=2, NO-OP) --->|
  |                            |  accept, 发送 P2B
  |       X  P2B 丢失  X       |
  |                            |
  |  (无人重试，slot 2 永久卡住)  |


修复后：

Leader                     Acceptor
  |--- P2A(slot=2, NO-OP) --->|
  |                            |  accept, 发送 P2B
  |       X  P2B 丢失  X       |
  |                            |
  | [HeartbeatTimer 触发]       |
  |  扫描: slot 2 仍是 ACCEPTED |
  |--- P2A(slot=2, NO-OP) --->|  重试！
  |                            |  accept, 发送 P2B
  |<------ P2B(slot=2) -------|  这次收到了
  |                            |
  |  slot 2 → CHOSEN           |
  |  slot 2,3,4,5 顺序执行 ✅    |
```

### 为什么复用 HeartbeatTimer 而不是单独加一个 P2ATimer

实际上两种方案都可行。选择复用 HeartbeatTimer 的考虑是：心跳本身就是周期性触发的，频率适中（不会太频繁浪费带宽，也不会太慢导致长时间阻塞），而且心跳间隔内如果 slot 仍然没有推进到 CHOSEN，大概率说明消息确实丢了，值得重试。单独加一个 P2ATimer 可以更精细地控制重试频率，但增加了额外的定时器管理复杂度，对于这个场景收益不大。

### 启发

分布式系统中消息丢失是常态，任何依赖"消息一定能送达"的假设都是隐患。对于关键路径上的操作，必须有重试机制兜底。尤其要注意那些没有外部触发源的操作（比如 NO-OP），它们不会被客户端重试，如果系统自身没有重试逻辑，就会变成永久性的阻塞点。