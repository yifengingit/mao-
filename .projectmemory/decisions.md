# 关键设计决策

## D1: markitdown 而非 marker 做 PDF 转换
- **决策时间**: Phase 1
- **原因**: marker 是首选但在 Windows 环境下因网络问题无法下载远端模型
- **影响**: markitdown 输出质量略低 (偶尔编码问题)，但 clean_markdown.py 已补偿
- **后续**: 如果换到 Linux/Mac 环境，可以考虑用 marker 重跑获得更好质量

## D2: DeepSeek 而非 GPT-4 / Claude 做实体抽取
- **原因**: 性价比。421 篇文章 x 长上下文 = 大量 token。DeepSeek 价格低一个数量级
- **代价**: JSON 格式偶尔不一致，需要重试逻辑 (3 次重试 + 指数退避)
- **结果**: 110 篇 (26%) 失败，主要是大文章 token 超限

## D3: JSONL 而非 SQLite 做数据存储
- **原因**: 简单、可 git 跟踪、可 diff
- **代价**: 读取需要全量加载，没有查询能力
- **权衡**: 数据量 < 10MB，全量加载可接受

## D4: 单文件 HTML 而非 React/Vue
- **原因**: Portfolio 项目，不需要构建工具。一个文件 = 最简部署
- **代价**: 代码全在 <script> 标签里，重构难度高
- **权衡**: D3.js 本身就适合单文件操作

## D5: 默认 99 节点而非全部显示
- **决策时间**: Phase 2.5 (v2 重写)
- **原因**: 1068 节点 = 毛线团。degree >= 5 的 99 个节点形成可读的核心网络
- **数据依据**: 度分布分析: degree>=5=99, degree>=3=194, all=1068
- **三级切换**: 让用户自行选择密度，不强制

## D6: 时间轴做过滤而非重排
- **决策时间**: Phase 2.5 设计会议
- **原因**: KronoGraph 式的时间轴排列会破坏力导向图的社群空间结构
- **灵感**: "Everyone moves nodes to the timeline. We move the timeline to the nodes."
- **实现**: currentYear 过滤 node.first_seen 和 link.first_date 的可见性

## D7: 保留 Louvain 社群但仅用于着色
- **原因**: 479 个社群太多，做不了有意义的社群标签
- **现状**: 社群 ID 用于 person 节点的颜色分配 (community_id % 19 色)
- **潜力**: 只有前 10 个社群有 > 8 个成员，可以只给这些打标签

## D8: evidence_items 直接嵌入 graph.json
- **原因**: 前端点击边时需要立即显示原文，不想做二次请求
- **代价**: graph.json 从 ~500KB 膨胀到 1.4MB
- **权衡**: 1.4MB 对于浏览器加载完全可接受
