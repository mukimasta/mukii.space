---
aliases:
  - /professional/distributed/distributed-system-blog-01--exactly-once-rpc/
---

# Distributed System Blog 01 – Exactly-Once RPC

**在不可靠网络上实现 Exactly-Once RPC**

## 0  前言

### 0.1  分布式系统

我们每天都在用分布式系统：
- 打开微信 →  你的手机连接到腾讯的服务器
- 刷抖音     →  视频从字节的服务器传给你
- 网购         →  订单信息存在阿里的数据库里

**分布式系统 = 多个独立计算节点通过网络协作实现共同的目标**

**为什么需要分布式系统？**
- 单机装不下： Facebook 有 30 亿用户，一台机器存不下所有数据
- 单机扛不住： 双十一每秒几十万订单，一台机器处理不过来
- 单机会挂掉： 服务器会坏，硬盘会烧，需要备份

但多台机器带来了新的问题：它们之间如何通过网络通信协作？

### 0.2  Remote Procedure Call (RPC)

你平时用 app：

```
点击朋友头像 → 看到个人资料
刷新朋友圈 → 看到最新动态
发送消息 → 对方收到
```

这些操作背后就像调用了一个远程函数。

想象你在写代码：
```python
# 本地函数调用
profile = get_profile(user_id)
```

这个函数在你的程序里执行，读取本地内存的数据。

但如果数据在另一台机器上呢？

```python
# 远程函数调用（RPC）
profile = remote_get_profile(user_id)
```

这个函数：
1. 把请求通过网络发给服务器
2. 服务器执行函数
3. 把结果通过网络发回来

看起来只是加了个 “remote”，但加入了网络，一切都变了。

### 0.3  一个转账的故事

想象这个场景：
```
你打开手机 app，给朋友转账 100 元
点击"确认转账"
loading...
loading...
10 秒过去了，还在 loading
```

你会怎么做？
- 再点一次？万一第一次成功了呢？那就转了 200 元
- 放弃？万一根本没转成功呢？
- 等着？等到什么时候？

**这就是分布式系统的核心困境：网络是不可靠的**

### 0.4  网络有多不可靠？

发送"转账 100 元"后，没收到回复。发生了什么？
```
情况1：请求在路上丢了
Client ----X---> Server
(Server 根本没收到)

情况2：Server 执行了，但回复丢了
Client --------> Server ✔️
Client <---X---- Server
(钱转了，但你不知道)

情况3：网络很慢
Client ----😴---> Server 🕒
(还在路上，看起来像丢了)
```

**关键困境：你无法区分这些情况，也无法保证消息到达的顺序。**

### 0.5  我们的目标：Exactly-Once RPC

不管网络环境如何，我们想要保证：每个操作恰好执行一次（Exactly-Once）。

“Exactly-Once”怎么实现？

**Exactly-Once = At-Least-Once + At-Most-Once**

拆开来看：
- **不能是 0 次** → 至少执行 1 次（At-Least-Once）
- **不能是 2+ 次** → 至多执行 1 次（At-Most-Once）

## 1  At-Least-Once RPC

我们先来实现 At-Least-Once RPC，也就是先保证每个操作被 Server 至少执行一次，并且 Client 总会收到执行结果。

At-Least-Once 在 Client 层级上实现。

### 1.1  重试机制

我们先来解决第一种情况：请求可能丢失，也就是 Server 没有收到请求：
```
  Client    ----X--->    Server
转账 100 元  (网络丢包)  (根本没收到)

结果: 0 次执行
```

怎么办？

一个很直觉的想法是：重试

我们每间隔一段时间，就重新发送一次请求，直到成功收到回复为止。

```
  Client    ----X--->    Server
转账 100 元  (网络丢包)  (根本没收到)

  Client    -------->    Server
转账 100 元    (重试)    (成功执行)

  Client    <--------    Server
 (收到回复)              (回复结果)

结果: 1 次执行
```

看起来很合理，但是，这样会带来一个问题。

考虑这个场景：

```
时刻 T1: Client 发送 "转账 100"
时刻 T2: (超时，没回复)
时刻 T3: Client 重试，再次发送 "转账 100"
时刻 T4: Server 回复 "成功"
时刻 T5: Client 发送新命令 "查询余额"
时刻 T6: Server 回复 "成功"

问题: 这个 "成功" 是哪个命令的回复？
- 转账的回复？
- 查询余额的回复？
```

如果 Client 误以为"成功"是"查询余额"的回复，但其实是第一次"转账"的延迟回复，系统就乱了。

**问题本质：回复和请求失去了对应关系。**

### 1.2  RequestID 请求标识

怎么建立对应关系？给每个请求打标签。

标签需要满足：

- 重试时保持不变（这样才知道是同一个请求）
- 新命令时改变（这样才能区分不同请求）

**自然的选择：递增的 request_id**

```
Client 维护一个计数器:
request_id = 0

发送新命令:
  request_id += 1
  发送 (request_id, command)

重试时:
  发送相同的 (request_id, command)
  (request_id 不变！)
```

Server 的回复也必须带上 request_id，否则 Client 无法匹配。

具体场景：

```
T1: Client 发送 (request_id=1, "转账 100")
T2: (超时，准备重试) 
T3: Client 发送 (request_id=1, "转账 100")  ← ID 不变
T4: Server 回复 (request_id=1, "成功")
T5: Client 发送 (request_id=2, "查询余额") ← ID 递增
T6: Server 回复 (request_id=1, "成功")

Client 检查: request_id=1 ≠ 当前的 request_id=2
→ 这是旧回复，忽略
→ 继续等待 request_id=2 的回复
```

完整的消息格式：

```
Request:
  request_id: 第几个请求
  command:    要执行什么

Reply:
  request_id: 回复哪个请求
  result:     执行结果
```

### 1.3  At-Least-Once 的完整逻辑：

```
Client 的状态:
- current_request_id: 当前请求的 ID
- current_command:    当前请求的命令
- timer:              重试定时器

发送新命令:
  current_request_id += 1
  current_command = command
  发送 Request(current_request_id, command)
  启动 timer

收到回复 Reply(reply_request_id, result):
  if reply_request_id == current_request_id:
      停止 timer
      返回 result
  else:
      忽略 (这是旧请求的回复)

Timer 超时:
  重发 Request(current_request_id, current_command)
  重启 timer
```


**至此，我们实现了 At-Least-Once：只要 Client 不停重试，请求最终会到达并执行，Client 最终会收到回复。**


## 2  At-Most-Once RPC

Client 重试会导致 Server 收到多个相同的请求。我们即将实现的 At-Most-Once 需要保证每个请求只被执行一次。

At-Most-Once 在 Server 层级上实现。

### 2.1  去重机制

Server 怎么知道这是重复请求？

用我们已有的东西：**request_id**

```
Server 维护一个记录:
seen = {1, 2, 5, 7, ...}

收到请求 Request(request_id, command):
  if request_id in seen:
      这是重复请求
      ...
  else:
      这是新请求
      ...
```

对于多个 Client 的情况：

Server 的记录的 Key 变成 (client_id, request_id)：

在网络通信中，每个消息天然就带有发送者的地址（address）。我们直接用这个地址作为 client_id 即可。

所以一个请求的完整的唯一标识是：(client_id, request_id)，这也是在 Server 层要维护的记录。
其中：
- **client_id**：由网络框架提供（发送者的地址）
- **request_id**：由我们的应用层维护（递增序列号）

### 2.2  请求 → 结果 映射表

在接收到重复请求后，要怎么做？

```
T1: Client 发送 Request(request_id=1, command)
    Server 执行，回复丢失

T2: Client 重试，发送 Request(request_id=1, command)
    Server 发现: 之前见过 (client_id, 1)
    然后呢？
```

Server 不能：
- 重新执行 → 违反 at-most-once
- 不回复 → Client 会一直等

**Server 必须：返回之前的结果**

对于每个请求 (client_id, request_id)，保存对应的结果。

**HashMap: (client_id, request_id) -> Result**

使用一个“请求 → 结果”映射表，收到旧请求时返回即可。

Server 不能无限保存历史。

### 2.3  单请求假设下的垃圾回收机制

Client 单请求假设：Client 在未收到当前请求的回复之前不会请求新命令。

```
Client 的行为:
发送 req=1 → 等回复 → 收到
发送 req=2 → 等回复 → 收到
发送 req=3 → ...
```

在此情况下：
```
Client 发送了 request_id=N+1
→ 说明它已经收到了 request_id≤N 的回复
→ Server 可以丢弃 request_id≤N 的记录
```

所以只需保存最后一个：
```
history = {
  client_A: (last_id, last_result),
  client_B: (last_id, last_result),
}

收到新请求 N:
  history[client_id] = (N, result)
  // 自动覆盖旧的，只保留最新
```

**HashMap: client_id -> (request_id, Result)**

### 2.4  At-Most-Once 的完整逻辑

```
Server 的状态:
- history: map[client_id → (last_request_id, last_result)]

收到请求 Request(request_id, command) 来自 client_id:
  
  record = history.get(client_id)
  
  if record 不存在:
      // 第一次见到这个 Client
      result = execute(command)
      history[client_id] = (request_id, result)
      发送 Reply(request_id, result)
      return
  
  if request_id <= record.last_request_id:
      // 重复或乱序的旧请求
      发送 Reply(request_id, record.last_result)
      return
  
  // 新请求 (request_id > last_request_id)
  result = execute(command)
  history[client_id] = (request_id, result)  // 覆盖旧记录
  发送 Reply(request_id, result)
```


## 3  Exactly-Once RPC 完整架构

```
Client 节点                    Server 节点
┌──────────────┐              ┌────────────────┐
│ Retry Logic  │   Command    │ AMOApplication │
│    (ALO)     │  ─────────→  │     (AMO)      │
│              │    Result    │       ↓        │
│              │  ←─────────  │  Application   │
│              │              │   (business)   │
└──────────────┘              └────────────────┘
```

详细版本：

```
Client Node                              Server Node
┌─────────────────────────┐             ┌──────────────────────────┐
│ Retry Logic (ALO impl)  │             │ AMOApplication (AMO impl)│
│                         │             │                          │
│ • request_id: 1,2,3...  │  Command    │ • Dedup check:           │
│ • Timer: retry timeout  │  +request_id│   req_id <= last_req_id? │
│ • Match reply: ID match?│             │                          │
│                         │ ─────────→  │ • Save history:          │
│                         │             │   map[client_id→         │
│                         │             │       (req_id, result)]  │
│                         │  Result     │                          │
│                         │  +request_id│   ↓ if new request       │
│ Match → stop retry      │ ←─────────  │                          │
│                         │             │ Application (Business)   │
│                         │             │ • Get/Put/Append         │
│                         │             │ • Transfer/Query         │
│                         │             │ • ... (any business)     │
└─────────────────────────┘             └──────────────────────────┘
         ↑                                         ↑
client_id provided by network          Get client_id from message
framework (sender address)             (sender address)
```

**Server 内部分层（怎么做）**

```
Server 内部:
┌─────────────────────┐
│  AMOApplication     │ ← 去重层
│      (包装)          │   只关心 request_id
│                     │   不关心业务逻辑
│        ↓            │
│  Application        │ ← 业务层
│   (具体业务)          │   只关心业务逻辑
│  • KVStore          │   不关心去重
│  • GameServer       │
│  • ShoppingCart     │
└─────────────────────┘
```

##  4  拓展延伸


不是所有操作都怕重复

### 4.1  Side Effect 和 Idempotence


**Side Effect = 改变系统状态的操作**

```
无副作用 (读操作):
- GET(key)          - 只读，不改变状态
- QUERY_BALANCE()   - 只读，不改变状态

有副作用 (写操作):
- PUT(key, value)   - 修改状态
- TRANSFER(amount)  - 修改状态
- APPEND(key, val)  - 修改状态
```

如果操作有副作用，重复执行可能产生错误的结果。

**Idempotence（幂等性）= 执行多次和执行一次的效果相同**

```
幂等操作:
- GET(key)            - 读多次结果一样
- PUT(key, "value")   - 设置成固定值，重复设置还是那个值
- DELETE(key)         - 删除（删除已删除的 = 还是删除）

非幂等操作:
- APPEND(key, value)  - 每次追加，越来越长
- INCREMENT(counter)  - 每次加 1，越来越大
- TRANSFER(amount)    - 每次扣钱，越来越少
```

**为什么重要？**

如果操作是幂等的，系统可以简化：

```
Client: 不确定是否成功？直接重试就行
Server: 重复执行也没事
→ 不需要复杂的 AMO 机制，at-least-once 就够了
```

这就是为什么 DNS、NFS 等系统能用简单的 at-least-once。

### 4.2 我们的方案适用范围

适用于：
- 非幂等操作（需要 AMO 保护）
    - APPEND、INCREMENT、TRANSFER 等
- Client 单请求模式（垃圾回收依赖这个假设）
    - 一个 Client 一次只发一个请求
- 有状态服务（需要记住历史）
    - 需要持久化存储的服务

## 5  结语

Lab 1 看起来很简单：实现一个 RPC。

但它揭示了分布式系统的核心挑战：**如何在不确定性中构建确定性？**

我们的答案不是消除不确定性（做不到），而是：

- 承认网络不可靠
- 分解问题（exactly-once = at-least + at-most）
- 分层设计（Client 重试 + Server 去重）
- 利用假设（单请求 → 垃圾回收机制）
- 用简单机制组合成复杂保证

这不仅仅是一个 Lab 的解法，更是分布式系统设计的基本哲学。

下一步：Lab 2 会引入 Primary-Backup，在不可靠的服务器上实现可靠的服务。
[Distributed System Blog 02 – Primary-Backup](/blogs/professional/distributed/distributed-system-blog-02--primary-backup/)