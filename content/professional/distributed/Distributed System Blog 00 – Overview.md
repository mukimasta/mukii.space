
# 从零开始的分布式系统

在 2026 年 1 月到 3 月的春季学期里，我在 UW 上完了 Distributed System 这一门课程。我的最大感受就是这真的是一门优质的课程，教授带领我们系统性地了解分布式系统的底层思想和原理，并且还设置了4个lab，带我们从零开始一步步实现一个分布式 KV Store 系统。

四个 lab 分别是：
1. Exactly-Once RPC
2. Primary-Backup
3. Multi-Paxos
4. Sharded Multi-Paxos

除了这些内容之外，课程还要求我们阅读 3 篇 paper 并选取两个角度写 BLOG，这也是非常好的设计，让我们不止是纸上谈兵，而是看看真实工业系统中的设计是什么样的。

接下来我会用一系列的 BLOG 记录这一系列 lab 主题的思想和实现思路，从零开始实现一个 Multi-Paxos 的分布式系统。

第一篇：
[Distributed System Blog 01 – Exactly-Once RPC](/professional/distributed/distributed-system-blog-01--exactly-once-rpc/)

