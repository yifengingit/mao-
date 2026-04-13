# 当前状态 (2026-04-13)

## 已完成

### Phase 1: PDF -> Markdown (100%)
- [x] PDF 按卷拆分 (7 卷)
- [x] Markdown 转换 (markitdown)
- [x] 清洗 & 标准化 (编码修复、硬换行、格式)
- [x] 每卷 QA 报告
- [x] 全部 7 卷人工 full review 完成
- [x] Review 发现的问题已 TDD 修复并重跑

### Phase 2: 结构化抽取 (95%)
- [x] 文章切分: 421 篇，7 卷全覆盖
- [x] 人物实体抽取: 1,746 条 (DeepSeek API)
- [x] 地点实体抽取
- [x] 人物去重: 577 unique (67% 去重率)
- [x] 地点去重: ~323 unique
- [x] 关系抽取: 1,451 条
- [x] 关系去重: 1,176 unique (19% 去重率)
- [x] 实体档案生成: 585 人物 + 323 地点
- [x] 图谱构建: graph.json (1,068 节点, 1,091 边)
- [x] 社群检测 (Louvain) + 中心度计算 (betweenness)
- [x] 文章摘要生成: article_excerpts.json (421 条)
- [x] D3.js 可视化 v2 (暗色主题, 密度切换, 时间轴, 传记模式)
- [ ] **110 篇文章抽取失败** (主要是 volume-06, API 超时/格式问题)

### Phase 2.5: 可视化 v2 (进行中, ~80%)
这是最后一次 AI 编程会话正在做的工作。

**已实现的功能:**
- GitHub 暗色主题 (#0d1117 背景)
- 三级密度切换: 精要(degree>=5, 99节点) | 扩展(degree>=3, 194节点) | 全量(1068节点)
- 默认显示 99 个最核心节点（解决了"毛线团"问题）
- 加载动画 (CSS pulse dots)
- 模拟结束后自动 zoom-to-fit
- 节点大小 = betweenness centrality, 颜色 = 社群 (Louvain)
- 人物/地点/组织三色区分
- 鼠标悬停 tooltip (名称、首见年份、关联数、角色)
- 点击节点: 高亮邻居 + 右侧面板展开
- 右侧面板: 基本信息、来源段落(evidence)、关联节点列表
- 点击边: 展示关系类型 + 证据原文
- 时间轴: 底部直方图 + 拖拽滑块 (1919-1985)
- 时间过滤: 节点/边按 first_seen/first_date 过滤
- 播放按钮: 自动推进年份
- 传记模式: 选中节点 -> 只看该节点的 ego-network 随时间演化
- 搜索框: 实时过滤节点名称

**已知问题 (v2 可视化):**
- 图谱在画布上的位置偏下，zoom-to-fit 可能没有完美居中
- 需要浏览器实际测试交互功能
- 密度切换时会重建整个 simulation（有一个 loading overlay）
- `window.__excerpts` 的时序问题已修复但未验证

## 未开始

### Phase 3: 知识产品化
- [ ] 处理 110 篇失败文章 (retry_failed_articles.py 已就绪)
- [ ] 扩展实体类型: 组织、事件、概念、著作
- [ ] AI 生成实体摘要 (DeepSeek)
- [ ] Wikipedia/百度百科 交叉引用
- [ ] REST API
- [ ] 可分享的永久链接
- [ ] 移动端适配（右面板改 bottom sheet）

## 项目用户最后一句话

> "感觉一般。。没有什么吸引力和可读性。。。"

这句话触发了 v2 的完全重写。v2 已写入 `visualize/index.html`，核心改进是:
1. 默认只显示 99 个核心节点（不是 1068 个全部展示）
2. GitHub 暗色主题
3. 自动 zoom-to-fit

但 v2 在浏览器中只做了一次快速截图验证，**没有完成完整的交互测试**。
下一个 AI 助手接手时，第一件事应该是:
1. `python -m http.server 8766` 启动服务
2. 浏览器打开 `http://localhost:8766/visualize/index.html`
3. 验证所有交互功能是否正常
4. 根据用户反馈调整
