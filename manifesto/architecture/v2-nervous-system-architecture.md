# 一人制公司 Agent OS — v2 架构设计
## 从"部门流水线"到"经营神经系统"

**版本：** v2.0-draft
**状态：** 设计阶段
**上一版本问题：** v1 用公司部门组织图思维解决了神经系统问题——它处理任务，但不感知、不学习、不保护、不适应。

---

## 核心判断：两种根本不同的设计哲学

| | v1：部门流水线 | v2：经营神经系统 |
|---|---|---|
| **工作模式** | 任务进入 → 顺序处理 → 结果输出 | 持续感知 + 按需深度处理 |
| **状态** | 无状态，每次从零开始 | 有状态，每次在历史上生长 |
| **执行结构** | 线性串行（A→B→C→D→E→F→G） | DAG 并行（可并发，按依赖合并）|
| **工具能力** | 纯语言模型（训练数据）| 工具原生（搜索、执行、存储）|
| **学习机制** | 记忆 Agent 记录但不反馈 | 决策考古 + 模式库自动更新 |
| **对主理人** | 被动响应 | 主动感知 + 节律驱动 |
| **挑战能力** | 无（只有执行） | 红队 Agent 专职挑战 |
| **社区维度** | 无 | 匿名模式共鸣网络 |

---

## v2 四层架构

```
┌─────────────────────────────────────────────────────────┐
│  Layer 0：经营底座（Business Foundation）                  │
│  主理人画像 · 当前经营状态 · 历史决策库 · 价值边界           │
└────────────────────────┬────────────────────────────────┘
                         │ 持续读写
┌────────────────────────▼────────────────────────────────┐
│  Layer 1：感知层（Perception Layer）                       │
│  节律触发器 · 事件监听器 · 任务入口 · 信号聚合器            │
└────────────────────────┬────────────────────────────────┘
                         │ 结构化信号
┌────────────────────────▼────────────────────────────────┐
│  Layer 2：处理层（Processing Layer）— 升级版七核 DAG        │
│                                                          │
│    ┌──────────┐   ┌──────────┐                          │
│    │ 判断核   │   │ 初步研究 │  ← 并行执行               │
│    └────┬─────┘   └────┬─────┘                          │
│         └──────┬────────┘                               │
│                ▼                                        │
│         ┌──────────┐   ┌──────────┐                    │
│         │  编排核  │   │  红队核  │  ← 新增，独立挑战    │
│         └────┬─────┘   └────┬─────┘                    │
│              └──────┬───────┘                           │
│                     ▼                                   │
│    ┌──────────┐   ┌──────────┐                          │
│    │ 深度研究 │   │  表达核  │  ← 部分并行              │
│    └────┬─────┘   └────┬─────┘                          │
│         └──────┬────────┘                               │
│                ▼                                        │
│         ┌──────────┐                                    │
│         │  执行核  │                                    │
│         └────┬─────┘                                    │
│              ▼                                          │
│    ┌──────────┐   ┌──────────┐                          │
│    │ 审计核   │   │ 能量感知 │  ← 并行评估              │
│    └────┬─────┘   └──────────┘                          │
│         ▼                                               │
│    ┌──────────┐                                         │
│    │  记忆核  │  → 写入 Layer 0 经营底座                 │
│    └──────────┘                                         │
└─────────────────────────────────────────────────────────┘
                         │ 沉淀
┌────────────────────────▼────────────────────────────────┐
│  Layer 3：沉淀层（Sedimentation Layer）                   │
│  决策考古档案 · 模式库（自更新）· 资产仓库 · 社区共鸣网络  │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 0：经营底座（永久状态层）

这是整个系统最重要的创新之一。**每次任务不再从零开始，而是从主理人的经营状态出发。**

### 底座四要素

**1. 主理人画像（Principal Profile）**
```yaml
principal_profile:
  decision_style: "slow-deliberate"      # 或 fast-adjust
  risk_appetite:
    market: high
    execution: medium
    finance: low
  cognitive_peaks: ["09:00-11:00", "15:00-17:00"]
  communication_preference: "bullet-first"  # 先结论后展开
  known_blind_spots:
    - "高估执行速度"
    - "低估竞争对手反应时间"
  strengths:
    - "市场判断准确率高"
    - "内容策略直觉强"
```

**2. 当前经营状态（Business State）**
```yaml
business_state:
  active_projects: [...]
  open_commitments: [...]
  current_focus_theme: "产品验证阶段"
  resource_status:
    time_available_this_week: 24h
    financial_runway: "8 months"
  open_questions: [...]  # 主理人正在思考但未决的问题
```

**3. 决策历史库（Decision Archive）**
- 每个重要决策的时间切片（见"决策考古"章节）
- 决策质量追踪（预测 vs 实际结果）
- 个人判断准确率分域统计

**4. 价值边界（Value Constraints）**
```yaml
non_negotiables:
  - "不做需要大团队的模式"
  - "不接受让用户数据作为产品的商业模式"
  - "主理人每周有至少两天深度工作时间"
```

---

## Layer 1：感知层

**节律触发器（Rhythm Engine）**

```
日节律：每日 08:30
  → 扫描今日承诺
  → 检查待处理信号
  → 生成当日聚焦建议（3条以内）
  → 能量状态询问（主理人输入）

周节律：每周一 09:00
  → 上周回顾（完成率、质量评级）
  → 本周优先级确认
  → 模式库更新推送

月节律：每月 1 日
  → 决策考古提醒（30/90/180 天回顾）
  → 经营趋势分析
  → 系统校准建议
```

**事件监听器**（可选工具接入）
- 邮件信号 → 判断是否需要系统介入
- 日历提醒 → 提前准备相关研究
- 关键词监控 → 市场信号捕获

---

## Layer 2：处理层 — 升级版七核 + 红队

### 新增：红队核（Red Team Agent）

**这是当前系统最严重的缺失。**

一人制公司最大的认知危险是：没有人会真诚地挑战你。红队核的职责就是专职担任"建设性反对者"。

**红队核的工作方式：**
```
输入：判断核的结论 + 编排核的方案
输出：
  最弱假设：[当前方案中最危险的未验证假设]
  反向情景：[如果最坏情况发生，这个方案如何崩塌]
  被遗漏的视角：[没有考虑到的利益相关者/竞争者/外部变量]
  挑战性问题：[3个主理人应该回答但可能没想过的问题]
  评级：[是否建议在推进前先回答这些问题]
```

**红队核的系统提示词设计原则：**
- 明确被告知"你的职责是找问题，不是支持方案"
- 被要求给出"如果这个计划失败，最可能的原因"
- 被要求寻找"反向证据"（与主流结论相悖的信号）

### DAG 执行逻辑

```python
# v2 并行执行示意

async def run_v2_pipeline(task, principal_state):
    # 阶段一：并行启动
    judgment, initial_research = await asyncio.gather(
        run_judgment(task, principal_state),
        run_initial_research(task)  # 快速搜索，非深度
    )

    # 阶段二：编排 + 红队并行
    orchestration, red_team = await asyncio.gather(
        run_orchestration(task, judgment, initial_research),
        run_red_team(task, judgment)  # 独立挑战，不被编排影响
    )

    # 仲裁点：主理人查看红队报告，决定是否继续
    if red_team.requires_arbitration:
        await request_principal_arbitration(red_team)

    # 阶段三：深度研究（带工具）
    deep_research = await run_deep_research(
        task, orchestration,
        tools=["web_search", "knowledge_base"]
    )

    # 阶段四：表达
    expression = await run_expression(deep_research, orchestration)

    # 阶段五：执行规划
    execution = await run_execution(expression, principal_state)

    # 阶段六：审计 + 能量感知并行
    audit, energy_check = await asyncio.gather(
        run_audit(judgment, deep_research, expression, execution),
        run_energy_assessment(principal_state)
    )

    # 阶段七：记忆沉淀 → 写回 Layer 0
    memory_output = await run_memory(
        task, expression, audit,
        target=principal_state.decision_archive  # 写回底座
    )

    return PipelineResult(
        expression=expression,
        execution=execution,
        red_team_flags=red_team,
        audit=audit,
        assets_created=memory_output.assets
    )
```

---

## Layer 3：沉淀层

### 决策考古系统（Decision Archaeology）

**最被低估的功能。**

每个重要决策在执行时创建一个"时间切片"：

```json
{
  "decision_id": "dec_20260320_001",
  "timestamp": "2026-03-20",
  "task": "是否进入B端市场",
  "decision": "暂缓，先验证C端",
  "context_at_time": {
    "assumptions": ["C端有10万潜在用户", "B端获客成本高"],
    "information_held": ["竞品A已在B端，但增速放缓"],
    "alternatives_considered": ["直接进B端", "双线并行"],
    "why_rejected": ["资源不足支持双线"]
  },
  "review_schedule": ["2026-06-20", "2026-09-20", "2027-03-20"],
  "actual_outcome": null  // 未来填入
}
```

**30/90/180天自动回顾：**
- 系统在预定时间提醒：「你在X天前做了这个决策，当时的假设是…现在的实际情况是什么？」
- 主理人输入实际结果
- 系统计算预测准确率，更新"判断准确率"分域档案

### 模式库（Pattern Library）

**自动从历史任务中提炼可复用模式：**

```
模式：竞品分析-快速研究模板
来源：7次成功使用
成功率：86%
适用条件：新市场进入判断 / 功能优先级决策
核心框架：[功能矩阵 × 用户评价 × 价格定位]
主理人偏好：此人倾向于"用户反馈优先于功能参数"
```

---

## 三种任务快速通道

```
Fast Lane（< 5 min, $0.05）：
  单核路由 → 判断+研究+表达 合并为单一调用
  适用：日常判断、快速信息查询

Standard Lane（~ 15 min, $0.50）：
  DAG 并行七核
  适用：重要研究、策略决策

Deep Lane（~ 45 min, $2+）：
  完整系统 + 多轮红队 + 主理人仲裁
  适用：高风险决策、方向性选择
```

**系统自动判断走哪条通道，主理人可覆盖。**

---

## 最小可行版本（MVP v2）

按价值/复杂度比排序，建议以下顺序实现：

1. **持久化记忆**（JSON → 向量数据库）—— 让每次对话读取历史
2. **研究核接入工具**（web_search_20260209）—— 最大单点价值提升
3. **红队核**（新增系统提示词）—— 认知质量飞跃
4. **判断+研究并行**（asyncio）—— 40% 速度提升
5. **快速通道（Fast Lane）**—— 降低日常使用摩擦
6. **决策考古**（时间切片 + 回顾调度）—— 长期复利引擎
7. **节律引擎**（每日/每周扫描）—— 从响应式到主动式
