# 新软件项目技能全景图

## 1. 目的与理论定位

本文不是一份“技能目录”，而是一套面向新软件项目的工程方法论说明书。它回答的核心问题是：

- 当需求仍然模糊时，项目应如何启动而不仓促落入编码；
- 如何让流程与主流、基础的软件工程理论兼容，便于理解、推广与裁剪；
- 如何把软件体系结构设计从“凭经验画图”提升为“有干系人、有关注点、有质量属性、有评估闭环”的严谨活动；
- 当前 `agentic-se-framework` 工作区中的技能，应该如何映射到这套方法论中。

### 1.1 理论定位与核心原则

这套方法论在软件工程主线上与 `SWEBOK`、`ISO/IEC/IEEE 12207`、`29148`、`15289` 的精神保持一致；在软件体系结构上，以 `ISO/IEC/IEEE 42010`、质量属性场景、`QAW`、`ATAM`、`ADR` 为核心，建立完整、细致、审慎的架构工作流：

- **生命周期并发、迭代、递归**：生命周期过程并非僵硬单线，需求、架构、设计、实现、验证、确认、运维和维护是同一条工程主线上的连续活动；
- **架构以描述与决策为中心**：架构不是几张孤立的草图，而是“干系人、关注点、视点、视图、对应关系、决策（ADR）及其依据”的组织化描述；
- **质量属性场景化**：质量属性不能只写口号（如“高性能”），必须转化为具体可测量的场景；
- **验证左移与真实场景确认**：验证贯穿需求、设计、原型、代码评审与测试全过程；
- **流程可裁剪，但关键问题不可省略**：小项目可压缩工件形式，但仍需回答“解决什么问题、哪些质量属性驱动结构、为何这样设计、如何证明有效”。

### 1.2 适用范围与技能源

本文基于当前已发布的技能集合：
- `vendor/mattpocock/local/*`：本地维护与增强的软件工程衍生技能；
- `core/*`：本仓库自研的架构治理、工单追踪与交付演进技能。

本文希望建立的是一条“可推广的主线 + 可裁剪的分支 + 可审计的工件体系”，而不是一条僵硬流水线。

## 2. 全局方法论总览

从经典软件工程视角看，一个新项目的稳妥主线不是“先写代码”，而是：

1. 建立协作和治理底座；
2. 澄清问题、干系人、目标与约束；
3. 建立领域语言、边界和架构驱动因素，并合成为完整的架构描述与实现流程计划；
4. 形成可评审、可验证、可追踪的规格；
5. 拆解为可执行工作包并建立状态流；
6. 提前验证未知项、风险项和关键假设；
7. 进入实现、集成与分层验证；
8. 对高风险变更设置审慎闸门；
9. 在交付前做规范一致性、规格一致性和架构一致性检查；
10. 发布、交接、运维观察，并把后续输入重新送回维护闭环。

如果映射到当前技能，主干路径通常是：

| 时机 | 优先技能 |
| :--- | :--- |
| 阶段 0：项目启动 | [`setup-matt-pocock-skills`](#setup-matt-pocock-skills) |
| 阶段 1：需求获取（二选一） | [`wayfinder`](#wayfinder) / [`grill-with-docs`](#grill-with-docs) |
| 阶段 2：概念统一、架构合成与约束落地 | [`domain-modeling`](#domain-modeling) → [`codebase-design`](#codebase-design) → [`to-arch`](#to-arch) → [`governed-arch`](#governed-arch) |
| 阶段 3：规格化与工单拆解 | [`to-spec`](#to-spec) → [`to-tickets`](#to-tickets) |
| 阶段 4：单切片编码与测试闭环 | [`implement`](#implement)（内含 [`tdd`](#tdd) + [`code-review`](#code-review)） |
| 阶段 5：运维、诊断与资产演进 | [`to-issues`](#to-issues) → [`triage`](#triage) / [`diagnosing-bugs`](#diagnosing-bugs) → [`governed-arch`](#governed-arch) |
| 辅助/横切：高不确定性探路 | [`research`](#research) / [`prototype`](#prototype) |
| 辅助/横切：高风险改动守门 | [`failsafe-loop`](#failsafe-loop) |
| 辅助/横切：会话交接 | [`handoff`](#handoff) |

要点不在于“顺序必须一刀切”，而在于每个阶段都必须回答一个明确的工程问题，并留下相应工件。

<div style="margin: 20px 0 28px;">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 620" width="100%" height="auto" role="img" aria-label="软件工程生命周期与技能映射图">
    <defs>
      <marker id="arrow-main" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
        <path d="M1 1 L7 4 L1 7 Z" fill="#6f42ff"></path>
      </marker>
      <marker id="arrow-dashed" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
        <path d="M1 1 L7 4 L1 7 Z" fill="#cbd5e1"></path>
      </marker>
    </defs>
    <!-- 背景底色 -->
    <rect x="0" y="0" width="1120" height="620" rx="12" fill="#ffffff"></rect>

    <!-- 行 1: 核心工程目标 (与主阶段对齐) -->
    <rect x="8" y="14" width="168" height="32" rx="16" fill="#475569"></rect>
    <text x="92" y="35" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">核心工程目标</text>
    
    <rect x="260" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="320" y="40" text-anchor="middle" font-size="14" fill="#334155">澄清问题</text>
    <text x="320" y="58" text-anchor="middle" font-size="14" fill="#334155">与关注点</text>
    
    <rect x="440" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="500" y="40" text-anchor="middle" font-size="14" fill="#334155">统一概念</text>
    <text x="500" y="58" text-anchor="middle" font-size="14" fill="#334155">与架构约束</text>
    
    <rect x="620" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="680" y="40" text-anchor="middle" font-size="14" fill="#334155">形成契约</text>
    <text x="680" y="58" text-anchor="middle" font-size="14" fill="#334155">与执行工单</text>
    
    <rect x="780" y="20" width="120" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="4 2"></rect>
    <text x="840" y="40" text-anchor="middle" font-size="14" fill="#334155">满足基线</text>
    <text x="840" y="58" text-anchor="middle" font-size="14" fill="#334155">与真实场景</text>

    <!-- 垂直连接线 (对齐核心) -->
    <line x1="320" y1="68" x2="320" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="500" y1="68" x2="500" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="680" y1="68" x2="680" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="840" y1="68" x2="840" y2="150" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>

    <!-- 行 2: 工程主阶段 -->
    <rect x="8" y="96" width="168" height="32" rx="16" fill="#6f42ff"></rect>
    <text x="92" y="117" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">工程主阶段</text>
    
    <line x1="158" y1="180" x2="1050" y2="180" stroke="#6f42ff" stroke-width="3" marker-end="url(#arrow-main)"></line>
    
    <rect x="95" y="150" width="125" height="60" rx="14" fill="#f5f3ff" stroke="#c4b5fd"></rect>
    <text x="158" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">启动</text>
    
    <rect x="250" y="150" width="140" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="320" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">需求获取</text>
    
    <rect x="420" y="150" width="160" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="500" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">架构与边界设计</text>
    
    <rect x="610" y="150" width="140" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="680" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">规格与拆解</text>
    
    <rect x="780" y="150" width="130" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="845" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">迭代闭环</text>
    
    <rect x="940" y="150" width="140" height="60" rx="14" fill="#ede9fe" stroke="#8b5cf6"></rect>
    <text x="1010" y="186" text-anchor="middle" font-size="15" font-weight="600" fill="#111827">运行与演进</text>

    <!-- 阶段 -> 技能 连接线 -->
    <line x1="158" y1="210" x2="158" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="320" y1="210" x2="320" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="500" y1="210" x2="500" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="680" y1="210" x2="680" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="845" y1="210" x2="845" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="1010" y1="210" x2="1010" y2="260" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>

    <!-- 行 3: 执行技能线 -->
    <rect x="8" y="220" width="168" height="32" rx="16" fill="#0f766e"></rect>
    <text x="92" y="241" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">执行技能线</text>
    
    <rect x="95" y="260" width="125" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="158" y="325" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">setup</text>
    
    <rect x="250" y="260" width="140" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="320" y="305" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">wayfinder</text>
    <text x="320" y="325" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">grill-with-docs</text>
    <text x="320" y="345" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-questionnaire</text>
    
    <rect x="420" y="260" width="160" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="500" y="290" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">domain-modeling</text>
    <text x="500" y="309" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">codebase-design</text>
    <text x="500" y="328" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-arch</text>
    <text x="500" y="347" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">governed-arch</text>
    
    <!-- impl-loop 编排虚线框 -->
    <rect x="598" y="246" width="324" height="142" rx="10" fill="#f0fdfa" fill-opacity="0.4" stroke="#0d9488" stroke-width="1.8" stroke-dasharray="5 3"></rect>
    <rect x="715" y="236" width="90" height="20" rx="6" fill="#0f766e"></rect>
    <text x="760" y="250" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffffff">impl-loop</text>

    <rect x="610" y="260" width="140" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="680" y="315" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-spec</text>
    <text x="680" y="335" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-tickets</text>
    
    <rect x="780" y="260" width="130" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="845" y="310" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">implement</text>
    <text x="845" y="330" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">（含 tdd /</text>
    <text x="845" y="350" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">code-review）</text>
    
    <rect x="940" y="260" width="140" height="120" rx="8" fill="#ecfeff" stroke="#2dd4bf"></rect>
    <text x="1010" y="295" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">to-issues</text>
    <text x="1010" y="315" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">triage</text>
    <text x="1010" y="335" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">diagnosing-bugs</text>
    <text x="1010" y="355" text-anchor="middle" font-size="12" font-weight="600" fill="#0f766e">governed-arch</text>

    <!-- 技能 -> 产物 连接线 -->
    <line x1="158" y1="380" x2="158" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="320" y1="380" x2="320" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="500" y1="380" x2="500" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="680" y1="380" x2="680" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="845" y1="380" x2="845" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>
    <line x1="1010" y1="380" x2="1010" y2="430" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="3 3" marker-end="url(#arrow-dashed)"></line>

    <!-- 行 4: 产物线 (简明名称) -->
    <rect x="8" y="390" width="168" height="32" rx="16" fill="#1d4ed8"></rect>
    <text x="92" y="411" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">产物线</text>
    
    <rect x="95" y="430" width="125" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="158" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">AGENTS.md</text>
    <text x="158" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">issue-tracker.md</text>
    <text x="158" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">triage-labels.md</text>
    
    <rect x="250" y="430" width="140" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="320" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">map.md</text>
    <text x="320" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">CONTEXT.md</text>
    <text x="320" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">to-questionnaire-*.md</text>
    
    <rect x="400" y="430" width="200" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="500" y="452" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">CONTEXT.md / ADR</text>
    <text x="500" y="472" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">docs/architecture.md</text>
    <text x="500" y="492" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">docs/action-plan.md</text>
    <text x="500" y="510" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">architecture.toml / module.toml</text>
    
    <rect x="610" y="430" width="140" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="680" y="450" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">.scratch/&lt;slug&gt;/</text>
    <text x="680" y="468" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">spec.md</text>
    <text x="680" y="488" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">.scratch/&lt;slug&gt;/</text>
    <text x="680" y="506" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">tickets/NN-*.md</text>
    
    <rect x="780" y="430" width="130" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="845" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">src/ + tests/</text>
    <text x="845" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">review 报告</text>
    <text x="845" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">failsafe 快照</text>
    
    <rect x="940" y="430" width="140" height="88" rx="8" fill="#eff6ff" stroke="#60a5fa"></rect>
    <text x="1010" y="458" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">docs/issues/*.md</text>
    <text x="1010" y="478" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">docs/issues/_summary.md</text>
    <text x="1010" y="498" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1e40af">诊断记录</text>

    <!-- 底部辅助横条 -->
    <line x1="20" y1="546" x2="1100" y2="546" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="6 4"></line>
    <rect x="10" y="558" width="1100" height="48" rx="10" fill="#fffbeb" stroke="#f59e0b" stroke-dasharray="5 3"></rect>
    <text x="28" y="587" font-size="15" font-weight="700" fill="#b45309">辅助/横切技能</text>
    <text x="225" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">research</text>
    <text x="355" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">prototype</text>
    <text x="500" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">failsafe-loop</text>
    <text x="640" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">to-issues</text>
    <text x="775" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">improve-arch</text>
    <text x="905" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">teach</text>
    <text x="1025" y="587" text-anchor="middle" font-size="14" font-weight="600" fill="#d97706">handoff</text>
  </svg>
</div>

## 3. 操作手册：按阶段详细指导

以下是软件工程生命周期各个阶段的详细操作指南，包括每个阶段应该使用什么技能、如何使用以及预期产出的工件。

### 3.1 阶段 0：启动（协作底座）

**目标**：建立团队（Agent 与人类）的协作底座。

**使用技能与逻辑关系**：【必选单技能】

- **[`setup-matt-pocock-skills`](#setup-matt-pocock-skills)**
    - **怎么用**：项目伊始，人类直接调用该技能。
    - **发生什么**：它会在项目根目录生成 `AGENTS.md`，并在 `docs/agents/` 下建立工单跟踪器（Issue tracker）、分诊标签（Triage labels）和领域文档（Domain docs）的约定。

**阶段产出清单**：
- `AGENTS.md`：项目根目录协作底座与 Agent 行为指引
- `docs/agents/issue-tracker.md`：双流工单（Tickets / Issues）跟踪器约定
- `docs/agents/triage-labels.md`：分诊角色与状态标签定义
- `docs/agents/domain.md`：单上下文领域文档约定

### 3.2 阶段 1：需求获取

**目标**：从模糊的口号中提炼出确定的干系人关注点、目标和边界。

**使用技能与逻辑关系**：【互斥选择 1 + 按需辅助】

- **[`grill-with-docs`](#grill-with-docs)**（与 wayfinder 二选一，适用于小型、边界清晰的需求）
    - **怎么用**：抛出一个初始想法，调用该技能让它深度盘问你。
    - **发生什么**：通过多轮对话逼出隐藏假设；内嵌复用的 `domain-modeling` 会在术语敲定的当下即时写入 `CONTEXT.md`，并克制地沉淀 ADR。
- **[`wayfinder`](#wayfinder)**（与 grill 二选一，适用于大型、模糊的需求）
    - **怎么用**：当需求大到需要跨多天讨论、或者前路迷雾重重时调用。
    - **发生什么**：它不直接盘问，而是建立一个导航地图（`.scratch/<effort>/map.md`），把问题拆成子工单（`.scratch/<effort>/tickets/NN-<slug>.md`）逐个解决。具体解决某个 ticket 时，再使用 `grill-with-docs` 或 `research`。
- **[`to-questionnaire`](#to-questionnaire)**（按需辅助）
    - **怎么用**：当关键信息不在手里时调用。
    - **发生什么**：生成结构化问卷，以便发给外部干系人采集需求。

**阶段产出清单**：
- `.scratch/<effort>/map.md`：（若使用 `wayfinder`）迷雾导航地图与决议索引
- `.scratch/<effort>/tickets/NN-<slug>.md`：（若使用 `wayfinder`）探索子工单
- `CONTEXT.md`：初版领域词汇与核心实体定义（术语敲定即落盘，阶段 2 持续收敛）
- `docs/adr/NNNN-*.md`：初版架构决策记录（若在盘问中敲定关键决策）
- `to-questionnaire-*.md`：（若使用）外发干系人问卷（临时外发，不入库）

### 3.3 阶段 2：架构与边界设计

**目标**：识别质量属性，统一领域语言，设计逻辑边界，把它们合成为一份完整的架构描述，再转化为强制约束。这是一条从认知到代码的深水工作链。

**使用技能与逻辑关系**：【顺序协作，需依次执行】

1. **[`domain-modeling`](#domain-modeling)**（第一步：认知层）
    - **怎么用**：在理清需求后立即调用。
    - **发生什么**：统一团队词汇，识别核心实体，沉淀架构决策记录（ADR）。这是后续所有工作的前提。若阶段 1 已随 `grill-with-docs` 建立了初版 `CONTEXT.md` / ADR，本步在其上做增量挑战与收敛，而非从零新建。
2. **[`codebase-design`](#codebase-design)**（第二步：设计层）
    - **怎么用**：在概念统一后，用它来规划代码结构。
    - **发生什么**：它会帮你切分模块接缝（seams），在逻辑上保证高内聚和可测试性。
3. **[`to-arch`](#to-arch)**（第三步：合成层）
    - **怎么用**：当统一语言、关键决策与接缝方案基本就绪后调用。
    - **发生什么**：把散落在 `CONTEXT.md`、ADR、质量属性场景与地图决议中的认知，合成为一份完整的架构描述——讲清设计思想、干系人关注点、模块划分与必要视图。它向上游是决策的“汇”，向下游是执法层与规格层的“源”：`governed-arch` 依据其中的边界定义做 TOML 翻译，`to-spec` 从中获得全局框架。
    - **产物**：两份——架构描述 `docs/architecture.md`（结构遵循 `docs/templates/ARCHITECTURE-DESCRIPTION-FORMAT.md`，视图内嵌或相对链接），以及实现流程计划 `docs/action-plan.md`——规定治理脚手架先行、各模块实现、集成测试收尾的先后顺序，并标注哪些部分可并行、哪些必须串行及依据。
    - **边界**：`architecture.toml` 的 `depends_on` 拓扑只约束运行时"谁能 import 谁"，不规定施工顺序——依托接缝以测试替身先行，上层模块也能先实现、先单测；拓扑真正决定的是集成次序。模块/特性内部的步骤顺序归 `to-spec` 与 `to-tickets`，`action-plan.md` 只管跨模块编排。
4. **[`governed-arch`](#governed-arch)**（第四步：约束层）
    - **怎么用**：把架构描述中的边界定义翻译为强制执行的物理约束。
    - **发生什么**：生成 `architecture.toml` 和 `module.toml`，并配以自动化测试（如 `test_module_boundaries.py`），充当架构不被破坏的“执法者”。

**阶段产出清单**：
- `CONTEXT.md`：收敛定稿的统一领域语言
- `docs/adr/NNNN-*.md`：定稿的架构决策记录
- `docs/architecture.md`：全局架构描述（由 `to-arch` 合成，含干系人、视点/视图、质量属性）
- `docs/action-plan.md`：全系统波次施工计划与项目恢复点（由 `to-arch` 维护）
- `architecture.toml`：项目级架构边界与依赖规则
- `<module>/module.toml`：各模块私有/公开边界定义与测试约束

### 3.4 阶段 3：规格化与工单拆解

**目标**：将抽象的设计和需求转化为可执行的规格说明书和具体开发任务。

**范围边界**：跨模块的系统级施工顺序已由阶段 2 的 `docs/action-plan.md` 规定（含治理脚手架与集成测试的位次）；本阶段的 `to-spec` 与 `to-tickets` 只负责单个特性内部的步骤顺序，二者互不越界。本阶段既可在 `impl-loop` 的编排下自动化执行，亦可独立调用。

**使用技能与逻辑关系**：【顺序协作，需依次执行】

1. **[`to-spec`](#to-spec)**
    - **怎么用**：架构和需求稳定后调用（亦由 `impl-loop` 自动调用）。
    - **发生什么**：它会生成结构化的 `spec.md`，明确功能需求、非功能需求和验收标准。
2. **[`to-tickets`](#to-tickets)**
    - **怎么用**：基于 `spec.md` 调用（亦由 `impl-loop` 自动调用）。
    - **发生什么**：它会按照 `docs/agents/issue-tracker.md` 的约定，将规格拆解为 `.scratch/<feature-slug>/tickets/` 下的一张张开发工单，逐张声明阻塞关系。

**阶段产出清单**：
- `.scratch/<feature-slug>/spec.md`：单特性规格说明书
- `.scratch/<feature-slug>/tickets/NN-<slug>.md`：垂直切片开发工单（带 Blocked by 依赖 DAG，编号从 01 开始）

### 3.5 阶段 4：实现与迭代闭环

**目标**：编写代码，满足规格要求，并在紧致的小循环中完成审查、测试闸门验证与计划状态回写。

**使用技能与逻辑关系**：【高频循环：领工单 -> 实现（TDD + 审查） -> 闸门验证 -> 完工回写】

- **[`implement`](#implement)**（单切片执行主干，内含 [`tdd`](#tdd) 与 [`code-review`](#code-review)）
    - **怎么用**：由 `impl-loop` 逐张认领工单时自动调用，亦可由人类在单切片场景独立调用。
    - **发生什么**：
      1. **TDD 红绿循环**：在预定接缝处先写失败测试，再以最小实现变绿，保证回归测试覆盖；
      2. **类型与单测检查**：持续运行 typecheck 和单元测试；
      3. **合入前审查**：在提交前调用 `code-review` 进行双轴审查（仓库标准轴与规格契约轴）；
      4. **提交代码**：将已验证的切片代码与测试一同提交至当前分支。
      *(注：若实现中发现架构设计不合理、找不到接缝或依赖渗漏，应暂停实现，回退调用 `codebase-design` 重新切分接缝)*
- **[`governed-arch`](#governed-arch)**（按需辅助：持续校验）
    - **怎么用**：在编写跨模块代码或重构时随时调用，或通过它的测试脚本跑 CI。
    - **发生什么**：运行边界校验，立即告诉你新加的 `import` 是否违反了架构规则。

**阶段产出清单**：
- `src/` 与 `tests/`：通过分层验证的代码与单元/集成测试用例
- `docs/action-plan.md`：更新后的施工波次进度与新恢复点（由 `impl-loop` 自动回写）
- （代码合入与特性上线后，清理 `.scratch/<feature-slug>/` 临时工单目录）

### 3.6 跨阶段交付编排引擎：[`impl-loop`](#impl-loop)

在 SVG 全景图中，**阶段 3（规格与拆解）** 与 **阶段 4（迭代闭环）** 被外层的绿色大虚线框整体包裹，其核心载体正是自研编排技能 **`impl-loop`**。

#### 3.6.1 产生背景与核心价值

在传统或单点 Agent 协作中，开发者往往需要频繁手动执行多条独立命令：先调用 `/to-spec` 起草规格，再手动运行 `/to-tickets` 拆工单，接着逐张票敲 `/implement`，并在每张票完成后手动跑测试命令，最后还要手动打开 `docs/action-plan.md` 标记完成。这种割裂的交互模式极易出现**状态悬挂（State Drift）**或步骤遗漏。

`impl-loop` 的定位是**端到端跨切片交付引擎（End-to-End Delivery Engine）**。它将阶段 3 的规格与拆解产物和阶段 4 的编码、测试与合入审查串联成一个高度自动化、强闸门约束的工业级交付流水线：

```text
               ┌───────────────────── impl-loop 交付闭环 ─────────────────────┐
               │                                                              │
/to-arch ────> │  /to-spec ──> /to-tickets ──> [ 逐票: /implement ──> 闸门 ]    │ ──> 回写 action-plan.md (done)
(提供施工计划) │  (阶段 3)       (阶段 3)               (阶段 4)      (分层验证)  │     推进波次恢复点
               └──────────────────────────────────────────────────────────────┘
```

#### 3.6.2 分工边界与职责矩阵

| 技能 | 角色定位 | 核心职责 |
| :--- | :--- | :--- |
| **`impl-loop`** | **交付编排引擎** | 跨阶段全链路驱动、前置工件自主检测与补齐、测试闸门调度与验证、单 Spec 完工原子回写 `docs/action-plan.md`、断点续跑管理 |
| **`to-spec`** | **规格起草器** | 探索代码库，基于领域词汇（`CONTEXT.md`）起草结构化规格说明书 `spec.md` |
| **`to-tickets`** | **工单拆解器** | 将 `spec.md` 拆解为垂直切片临时工单 `tickets/NN-*.md`，声明 Blocked by 依赖 DAG |
| **`implement`** | **单切片执行器** | 单张工单的具体代码实现：以 `tdd` 红绿循环实现、持续跑单测、合入前调用 `code-review`、Git commit |
| **`to-arch`** | **顶层规划者** | 提供全系统波次施工计划 `docs/action-plan.md` 与分层测试策略（`docs/architecture.md`） |

#### 3.6.3 完工原子回写与断点恢复

- **单 Spec 完工原子回写**：当前 Spec 的所有工单解决且集成测试通过后，`impl-loop` 自动在 `docs/action-plan.md` 中将该 Slice 标记为 `done (<final_commit_sha>)`、记录测试通过命令，并将头部恢复点推进到下一波次，确保施工进度 100% 真实。
- **断点恢复（Resume Semantics）**：`impl-loop` 天生支持长链路与跨会话接续，任何新会话输入 `/impl-loop` 即可直接读取 `action-plan.md` 恢复点继续执行。

### 3.7 阶段 5：运行、诊断与演进

**目标**：系统上线或形成里程碑后，应对外部反馈、排查线上故障，并更新全局治理资产。

**使用技能与逻辑关系**：【按外部事件触发】

- **[`to-issues`](#to-issues)**（外部反馈触发，捕获入口）
    - **怎么用**：收到 Bug 报告、小功能请求或独立任务时首先调用。
    - **发生什么**：将其写入 `docs/issues/` 永久问题流（全局编号，Type / Status / Created 行），并同步刷新 `_summary.md` 索引；修复关闭后文件永久保留。
- **[`triage`](#triage)**（问题入流后触发）
    - **怎么用**：对两股流中的条目做分类流转——`docs/issues/` 的长期问题与 `.scratch/` 的临时工单都适用。
    - **发生什么**：把条目在五个 triage 角色间移动（如 `needs-triage` → `ready-for-agent`），排定处理顺序。
- **[`diagnosing-bugs`](#diagnosing-bugs)**（线上故障或性能瓶颈触发）
    - **怎么用**：出现复杂 Bug 或性能退化，不知从何下手时调用。
    - **发生什么**：启动专门的诊断循环，深入排查代码或日志，寻找根本原因。
- **[`governed-arch`](#governed-arch)**（里程碑触发）
    - **怎么用**：大版本发布或交接给运维团队前调用。
    - **发生什么**：一键生成/更新最新的模块架构 HTML 文档和依赖图，作为对外交付的资产。

**阶段产出清单**：
- `docs/issues/NNN-<slug>.md`：全局永久问题工单（三位数字编号如 001-fix-login.md）
- `docs/issues/_summary.md`：全局问题索引表（按状态与优先级分类并实时同步）
- 故障诊断分析报告与根因分析记录
- 重新导出的最新模块架构视图与演进知识库

## 4. 各阶段工件明细与模板规范

为了确保工程质量的可追踪性和一致性，下表明确了每个阶段应产生的核心工件及其对应的参考模板。

| 工程阶段 | 核心工件（标准相对路径） | 推荐技能 | 模板/规范参考 |
| :--- | :--- | :--- | :--- |
| **0. 启动** | `AGENTS.md`<br>`docs/agents/issue-tracker.md`<br>`docs/agents/triage-labels.md` | `setup-skills` | issue-tracker.md |
| **1. 需求获取** | `.scratch/<effort>/map.md`<br>`CONTEXT.md` (初版)<br>`docs/adr/NNNN-*.md` (初版) | `grill-with-docs`<br>`wayfinder` | QAS-FORMAT.md<br>CONTEXT-FORMAT.md<br>ADR-FORMAT.md |
| **2. 架构设计** | `CONTEXT.md` (定稿)<br>`docs/adr/NNNN-*.md`<br>`docs/architecture.md`<br>`docs/action-plan.md`<br>`architecture.toml` / `module.toml` | `domain-modeling`<br>`codebase-design`<br>`to-arch`<br>`governed-arch` | ARCHITECTURE-DESCRIPTION-FORMAT.md<br>VIEWPOINT-CATALOG.md<br>ADR-FORMAT.md |
| **3. 规格拆解** | `.scratch/<feature-slug>/spec.md`<br>`.scratch/<feature-slug>/tickets/NN-*.md` | `to-spec`<br>`to-tickets`<br>（由 `impl-loop` 驱动） | SPEC-FORMAT.md |
| **4. 迭代实现** | `src/` + `tests/`<br>`docs/action-plan.md` (进度回写) | `impl-loop`<br>`implement` (含 `tdd`/`review`)<br>`governed-arch` | 视项目规范而定 |
| **5. 运行演进** | `docs/issues/NNN-*.md`<br>`docs/issues/_summary.md`<br>诊断记录 / 更新后的架构图 | `to-issues`<br>`triage`<br>`diagnosing-bugs`<br>`governed-arch` | HANDOFF-FORMAT.md |

> 活文档标注：`CONTEXT.md` 与 ADR 是跨阶段演进的活文档，不专属于单一阶段——在阶段 1 由 `grill-with-docs` 内嵌的 `domain-modeling` 即时创建（惰性建文件、术语敲定即落盘），在阶段 2 由显式调用 `domain-modeling` 做统一挑战与收敛定稿。

## 5. 辅助技能与实用判断表

在主干路径之外，存在一组“辅助/横切技能”（对应 SVG 底部横条）。它们不直接推进流水线的状态流转，而是像“外挂工具箱”一样，在主干受阻、存在知识盲区、需要重构上下文或遇到高风险时按需触发（调用应当是非阻塞式和高度目的性的，解决完具体问题后迅速回到主干）。

### 5.1 辅助技能速览

| 技能 | 触发时机与用途 |
| :--- | :--- |
| [`research`](#research) | 关键事实不在手里（API 设计、库能力、竞品做法） |
| [`prototype`](#prototype) | 存在高不确定性风险，正式实现前先探路验证 |
| [`failsafe-loop`](#failsafe-loop) | 遇到极易出错或破坏性极大的修改，强行引入分阶段验证与快照比对 |
| [`to-issues`](#to-issues) | 捕获 bug 报告、小型功能请求或独立任务，写入永久问题流 |
| [`improve-codebase-architecture`](#improve-codebase-architecture) | 设计无法落地，或维护期结构阻碍新特性 |
| [`teach`](#teach) | 有复杂领域经验或脚手架要沉淀，或准备引入新成员 |
| [`handoff`](#handoff) | 会话结束或交接时压缩上下文，留存清晰起点 |
| [`to-questionnaire`](#to-questionnaire) | 关键信息掌握在外部干系人手里 |

### 5.2 实用判断表

| 当前卡点 / 场景 | 优先技能 | 应对动作 |
| --- | --- | --- |
| 需求极大且极模糊，一次说不完 | [`wayfinder`](#wayfinder) | 建立导航地图并拆出探索子工单 |
| 需求单一但逻辑不严密、隐藏假设多 | [`grill-with-docs`](#grill-with-docs) | 深度盘问逼出隐藏假设，即时沉淀术语与 ADR |
| 关键信息不在手里 | [`research`](#research) / [`to-questionnaire`](#to-questionnaire) | 调研一手事实或外发干系人问卷 |
| 术语漂移、概念混乱、实体定义不清 | [`domain-modeling`](#domain-modeling) | 统一团队词汇，维护 `CONTEXT.md` 与 ADR |
| 逻辑边界和接缝（seams）切分不清 | [`codebase-design`](#codebase-design) | 规划深模块与可测试接缝 |
| 需要一份讲清设计思想与模块划分的架构描述 | [`to-arch`](#to-arch) | 合成 `docs/architecture.md` 与施工波次 `docs/action-plan.md` |
| 需要强制执行架构和目录边界 | [`governed-arch`](#governed-arch) | 生成 TOML 边界规则与自动化架构测试 |
| 逻辑已收敛，需要形成执行与验收契约 | [`to-spec`](#to-spec) | 起草结构化规格说明书 `spec.md` |
| 需求和架构都定了，需要拆成开发切片 | [`to-tickets`](#to-tickets) | 拆解为垂直切片临时工单并声明阻塞 DAG |
| 规格与工单已就绪，需全流程驱动实现并推进项目计划 | [`impl-loop`](#impl-loop) | 串联逐票实现、测试闸门与 action-plan 进度回写 |
| Bug 报告、小功能或独立任务要长期追踪 | [`to-issues`](#to-issues) | 录入全局编号永久问题流并同步索引 |
| 可以开始写代码了 | [`implement`](#implement) / [`tdd`](#tdd) | 红-绿-重构节奏实现功能与单测 |
| 实现期发现设计无法落地、边界渗漏 | [`improve-codebase-architecture`](#improve-codebase-architecture) | 重划接缝并更新 ADR / 架构描述 |
| 这次改动破坏性极大，需要步步审查 | [`failsafe-loop`](#failsafe-loop) | 引入分阶段快照比对与严格风险闸门 |
| 要检验代码是否符合规范和规格 | [`code-review`](#code-review) | 启动双轴子代理审查标准与规格 |
| 任务交接或会话结束 | [`handoff`](#handoff) | 压缩会话上下文留存清晰交接点 |
| 线上故障排查或性能瓶颈定位 | [`diagnosing-bugs`](#diagnosing-bugs) | 建立红绿复现循环与可证伪假设排查根因 |

## 附录：技能速查 {#skill-appendix}

全景图中出现的全部技能在此逐一速查。按主线流程顺序排列；每条给出"何时使用、做了什么、怎么做的"的概括。`to-issues` 为本仓库自研技能（mine），与上游 `to-tickets` 分工互补而非重名关系。

### setup-matt-pocock-skills
- **何时使用**：项目伊始（阶段 0），建立 Agent 与人类协作底座。
- **做了什么**：生成 `AGENTS.md`，并在 `docs/agents/` 下建立工单跟踪器、分诊标签和领域文档约定。
- **怎么做的**：先探索仓库现状（远程与已有 `AGENTS.md`），再逐节提问确认三类配置，草稿确认后写入文档与 `AGENTS.md`。

### wayfinder
- **何时使用**：需求极大且模糊、需要跨多天讨论时（阶段 1，与 `grill-with-docs` 二选一）。
- **做了什么**：建立导航地图 `map.md`，把问题拆成工单逐个解决；具体解决某张工单时，再交给 `grill-with-docs` 或 `research`。
- **怎么做的**：先以 grilling 方式定目的地与范围，再广度优先梳理迷雾区、建立地图与决策票；认领前沿票后解析并记录决议闭合，每会话只解析一张票。

### grill-with-docs
- **何时使用**：小型、边界清晰的需求（阶段 1，与 `wayfinder` 二选一）。
- **做了什么**：多轮深度盘问逼出隐藏假设，顺手记录术语与决策。
- **怎么做的**：运行 grilling 会话逐问逼问隐藏假设，同时用 `domain-modeling` 维护词汇与 ADR，产出一份结合问答结果的文档。

### domain-modeling
- **何时使用**：既作为独立技能在阶段 2 第一步调用，也在阶段 1 被 `grill-with-docs` 内嵌复用（术语敲定即写入 `CONTEXT.md`）。
- **做了什么**：统一团队词汇、识别核心实体、沉淀 ADR，是后续所有工作的前提。
- **怎么做的**：对照词汇表即时指出术语冲突并给出规范术语，通过构造场景检验边界，边讨论边更新 `CONTEXT.md`，必要时写成 ADR。

### codebase-design
- **何时使用**：概念统一后规划代码结构（阶段 2 第二步）。
- **做了什么**：切分模块接缝（seams），保证高内聚、可测试。
- **怎么做的**：用统一词汇描述模块与接口，用"删除测试"判断模块深浅；通过依赖注入、返回结果、缩小接口面来优化，并牢记"一个适配器是假接缝，两个才是真"。

### to-arch
- **何时使用**：领域语言、关键决策与接缝方案基本就绪后（阶段 2 第三步）合成首版架构描述与实现计划（init 模式）；实现期任一切片开工/完工/受阻时回写进度（update-progress 模式）；里程碑或重大决策后对账再收敛（reconcile 模式）。本仓库自研技能（mine），模板副本内置，项目内 `docs/templates/` 同名文件优先。
- **做了什么**：把 `CONTEXT.md`、ADR、质量属性场景与地图决议合成为一份完整的架构描述 `docs/architecture.md`——讲清设计思想、干系人关注点、模块划分与必要视图；同时产出实现流程计划 `docs/action-plan.md`，规定治理脚手架先行、各模块实现、集成测试收尾的先后与并行分组（注意 `depends_on` 不决定施工顺序）。向上游汇齐分散决策，向下游为 `governed-arch` 的 TOML 翻译和 `to-spec` 的全局框架提供事实源。
- **怎么做的**：先盘点既有工件，列决策清单与视点选择；缺口按类型分流给 `grill-with-docs`/`wayfinder`/`research`/`domain-modeling`，坚持零虚构。随后逐节起草架构描述与波次式 action-plan（含并行分组与串行依据），经用户逐节确认后落盘。action-plan 是半成品工程的自述文件——头部"当前位置"行与每切片状态随做随更，任何新会话只读它即可知道做到哪、从哪继续；里程碑以 reconcile 模式对 TOML 投影与真实实现对账。

### governed-arch
- **何时使用**：设计落地为物理约束时，以及实现期、发布期的持续校验（阶段 2/4/5）。
- **做了什么**：生成 `architecture.toml`、`module.toml` 及自动化边界测试，充当架构不被破坏的"执法者"；发布时生成架构 HTML 文档与依赖图。
- **怎么做的**：用 TOML 声明结构与模块边界，公共 API 暴露即锁接口签名，跨模块只走 facade 网关导入；通过治理测试把关，并生成 HTML 文档呈现结果。

### to-spec
- **何时使用**：架构和需求稳定后（阶段 3 第一步）。
- **做了什么**：生成结构化的 `spec.md`，明确功能需求、非功能需求和验收标准。
- **怎么做的**：先探索代码库并用领域词汇起草 spec，确定最高价值的接缝并与用户确认，再按模板写 `spec.md` 发布并标记 ready-for-agent。

### to-tickets
- **何时使用**：规格就绪后拆解为可执行开发切片（阶段 3 第二步）。上游原版技能，按锁定基线逐字节还原。
- **做了什么**：按 `docs/agents/issue-tracker.md` 约定，将规格按垂直切片起草为 `.scratch/<feature-slug>/tickets/` 下的一张张临时开发票（`NN-<slug>.md`），逐张标注阻塞关系，宽重构改用 expand-contract 序列。
- **怎么做的**：与用户确认粒度与依赖后写入 `.scratch/<feature-slug>/tickets/`；工单是短期规划脚手架，随特性结束即弃——不建索引、编号按依赖顺序从 `01` 起、不跨特性复用。

### impl-loop
- **何时使用**：规格与工单拆解就绪后，需要推进端到端交付循环，或接续在途中特性时（阶段 3/4 编排器）。本仓库自研技能（mine）。
- **做了什么**：串联 `/to-spec` -> `/to-tickets` -> `/implement` -> 测试闸门，逐票闭环并实时更新恢复点；单 Spec 完工且集成闸门通过后，自动回写 `docs/action-plan.md` 标记 Slice 完成并推进波次。
- **怎么做的**：按 DAG 认领工单并派发给 `implement`，单票以 unit test 验收并打点，最后过 spec 级 integration test；完工时执行原子回写：更新 Slice 状态行、更新 Notes 闸门记录、推进 Resume Point 头部、归档临时脚手架。

### to-issues
- **何时使用**：捕获 bug 报告、小型功能请求或独立任务，写入仓库级永久问题流；不用于把规格拆解成切片（那是 `/to-tickets` 的职责）。本仓库自研技能（mine）。
- **做了什么**：在 `docs/issues/` 下以三位全局递增编号（永不复用）创建 `NNN-<slug>.md`，带 Type / Status / Created 元数据与 Evidence 证据节，并同步刷新 `_summary.md` 全局索引。
- **怎么做的**：先收集上下文，bug 尝试低成本复现但不阻塞记录；生命周期 needs-triage ⇄ needs-info → ready-for-agent | ready-for-human → fixed，wontfix 任意状态可达，重复问题记 wontfix 并留指针。约定见 `docs/agents/issue-tracker.md`。

### implement
- **何时使用**：领取工单开始写代码时（阶段 4 主干，与 `tdd` 搭配）。
- **做了什么**：按 TDD 节奏实现功能；若发现架构不落地（找不到缝隙、测试报错），暂停并回退到 `codebase-design`。
- **怎么做的**：用 `tdd` 在预定接缝处实现，期间定期类型检查、跑单元测试，最后全量测试；完成后交 `code-review` 并提交。

### tdd
- **何时使用**：伴随 `implement` 的必选节奏（阶段 4）。
- **做了什么**：以红-绿-重构循环保证测试覆盖，让每个功能都可回归验证。
- **怎么做的**：先写失败测试再最小实现变绿，一次只做一个切片；测试只测公开行为，避免实现耦合与同义反复测试。

### code-review
- **何时使用**：功能开发完毕、准备合并到主分支前（阶段 4 合入前触发）。
- **做了什么**：对照 `spec.md` 检查是否遵循仓库标准与规格要求，输出评审结论。
- **怎么做的**：先固定 diff 基点并确认非空，找到 spec 来源与编码标准文档；派并行子代理分"标准"与"规格"两轴审查，最后聚合报告、两轴分开呈现。

### handoff
- **何时使用**：会话结束、或要把工作交接给另一个 Agent / 人类时（阶段 4）。
- **做了什么**：压缩当前上下文，留给下一位接手者一个清晰的起点。
- **怎么做的**：把会话压缩成交接文档存入 `.scratch`，引用已有产物而不重复内容，脱敏后附上建议的技能清单。

### failsafe-loop
- **何时使用**：遇到极易出错或破坏性极大的修改时（阶段 4 按需干预）。
- **做了什么**：强行引入分阶段执行、每步验证与快照比对，失败即停，守住高风险闸门。
- **怎么做的**：每步先定义边界、不变量与基线，再依次过测试、工作流、审计、对比四道门；发现意外漂移立即停止上报，通过后按格式提交并汇报。

### triage
- **何时使用**：问题入流后需要分类流转时（阶段 5 触发）；对 `docs/issues/` 的长期问题与 `.scratch/` 的临时工单都适用。
- **做了什么**：把条目在五个 triage 角色间移动（如 `needs-triage` → `ready-for-agent`），排定处理顺序。
- **怎么做的**：先按 Type 分类（bug/enhancement 等），收集上下文并查重、排除 out-of-scope；复现验证 claim，必要时用 grilling 补充信息，最后应用状态流转并写 agent brief 或转 needs-info。

### diagnosing-bugs
- **何时使用**：出现复杂 Bug 或性能退化、不知从何下手时（阶段 5 故障触发）。
- **做了什么**：启动专门的诊断循环，深入排查代码与日志，定位根本原因并形成闭环。
- **怎么做的**：先构建紧致的红绿灯复现循环，复现并最小化到承重要素；生成 3-5 个可证伪假设逐一测试，修复前写回归测试，最后清理现场并预防复发。

### research
- **何时使用**：关键事实不在手里——API 怎么设计、库是否支持某特性、竞品怎么做（按需辅助）。
- **做了什么**：基于高可信来源输出一份 Markdown 调研报告，结论回流到主干继续推进。
- **怎么做的**：派后台代理并行调研，只追踪一手权威资料并引用；结果写成 Markdown 存入仓库约定位置。

### prototype
- **何时使用**：存在高不确定性风险——交互流、技术栈、状态机设计是否可行（进入正式实现之前）。
- **做了什么**：写并运行抛弃型代码验证假设，结论回填 ADR 或架构设计，验证后废弃代码。
- **怎么做的**：先判定是逻辑还是 UI 问题，用临时代码、单命令运行、无持久化；每次操作后展示完整状态，吸收决策后提交临时分支留痕。

### improve-codebase-architecture
- **何时使用**：实现期发现设计无法落地（找不到 seam、模块耦合），或维护期结构阻碍新特性加入。
- **做了什么**：对接缝切分或职责重构，并联动 `governed-arch` 更新 TOML 约束，锁定重构成果。
- **怎么做的**：先定扫描范围找出热点模块，生成 HTML 审查报告；选定候选后以 grilling 深挖设计，边决策边更新领域模型，重构后回写 TOML 约束。

### teach
- **何时使用**：解决了复杂的特定领域问题、沉淀了独特脚手架，或准备引入新成员时。
- **做了什么**：提取最佳实践、隐式规则和领域专有词汇，生成 Tutorials、Glossary 等培训材料，转化为组织长期资产。
- **怎么做的**：先明确 mission 并采集高可信资源，每课一个 HTML、小而可快速完成；用测验练习建立紧反馈环，产出 reference 与 learning-records。

### to-questionnaire
- **何时使用**：决策取决于干系人、专家或第三方掌握、而你无法独自补充的信息时。
- **做了什么**：把知识差距写成 Markdown 问卷（`to-questionnaire-<slug>.md`）交给对方填写，返回后回到主干继续澄清。
- **怎么做的**：只盘问发送方（问卷发给谁、需要他回什么），瞄准用户与收件人的知识差距；按模板写问答卷、重要问题在前。