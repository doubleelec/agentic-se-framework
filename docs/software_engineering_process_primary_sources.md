# 软件工程流程一手资料梳理

本文基于官方一手来源，聚焦以下问题：

- `SWEBOK` 如何界定软件工程的核心知识域与流程视角；
- `ISO/IEC/IEEE 12207` 如何定义软件生命周期过程框架；
- 从“需求”到“验证/确认”的主流程应如何理解；
- 典型核心工件应如何归类；
- 实务上可直接提炼出的流程原则有哪些。

## 一手来源

1. IEEE Computer Society, `Software Engineering Body of Knowledge (SWEBOK)`  
   官方入口：<https://www.computer.org/education/bodies-of-knowledge/software-engineering>

2. IEEE Computer Society, `SWEBOK Guide V4.0 Topics`  
   官方目录页：<https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics>

3. ISO, `ISO/IEC/IEEE 12207:2026 Systems and software engineering — Software life cycle processes`  
   官方标准页：<https://www.iso.org/standard/90219.html>  
   官方在线预览目录：<https://www.iso.org/obp/ui/en/#!iso:std:90219:en>

4. IEEE Standards Association, `IEEE/ISO/IEC 12207-2026`  
   官方标准页：<https://standards.ieee.org/ieee/12207/11416/>

5. IEEE Standards Association, `IEEE/ISO/IEC 29148-2018 Requirements engineering`  
   官方标准页：<https://standards.ieee.org/standard/29148-2018.html>

6. ISO, `ISO/IEC/IEEE 15289:2019 Content of life-cycle information items (documentation)`  
   官方标准页：<https://www.iso.org/standard/74909.html>

7. IEEE Standards Association, `IEEE/ISO/IEC 15289-2019`  
   官方标准页：<https://standards.ieee.org/ieee/15289/7196/>

8. IEEE Computer Society / ISO, `SEVOCAB`  
   官方入口：<https://pascal.computer.org/sev_display/index.action>  
   帮助页：<https://pascal.computer.org/sev_display/help.jsp>

## 总结先行

- `SWEBOK` 给的是“软件工程知识版图”，不是单一开发方法；其中与主流程最相关的知识域包括：`Software Requirements`、`Software Architecture`、`Software Design`、`Software Construction`、`Software Testing`、`Software Engineering Operations`、`Software Maintenance`、`Software Configuration Management`、`Software Engineering Management`、`Software Engineering Process`。来源：SWEBOK 官方页与 Topics 页。
- `ISO/IEC/IEEE 12207` 给的是“生命周期过程框架”，强调它不规定某一种生命周期模型或方法论，但过程可以被映射进任意模型，并且可以`并发`、`迭代`、`递归`地应用。来源：ISO 12207:2026 `Abstract`、`Scope`，IEEE 12207-2026 标准页。
- “需求到验证”的主流程，按标准精神可理解为：`需求获取/界定 -> 需求分析 -> 需求规格化 -> 架构/设计综合 -> 实现/构建 -> 集成 -> 验证 -> 确认`。其中 `12207` 给出过程框架，`29148`补足需求工程要求，`SWEBOK`补足活动分解与知识域。
- `12207` 明确说自己不细化文档名称、格式和记录媒介；工件体系应结合 `15289` 来看。`15289`把工件抽象成 `description`、`plan`、`policy`、`procedure`、`report`、`request`、`specification` 等通用信息项类型，并允许组合、拆分和按项目裁剪。来源：ISO 12207:2026 `Scope`，ISO/IEEE 15289:2019。
- `29148` 是“需求原则”的最直接官方来源：它定义了“好需求”的构造、属性与特征，并强调需求过程在整个生命周期中的`迭代`和`递归`应用。来源：IEEE/ISO/IEC 29148-2018 标准页。

## 1. SWEBOK 视角：软件工程流程不是单线，而是知识域协同

IEEE Computer Society 对 SWEBOK 的官方说明指出，SWEBOK 反映的是“软件工程领域中 generally accepted, consensus-driven knowledge”，当前版本为 `V4.0a`，共 `18` 个知识域，并新增了 `Software Architecture`、`Software Engineering Operations`、`Software Security` 等知识域。来源：<https://www.computer.org/education/bodies-of-knowledge/software-engineering>

与“软件工程主流程”最直接相关的知识域包括：

- `Chapter 1: Software Requirements Fundamentals`
- `Chapter 2: Software Architecture`
- `Chapter 3: Software Design`
- `Chapter 4: Software Construction`
- `Chapter 5: Software Testing Fundamentals`
- `Chapter 6: Software Engineering Operations`
- `Chapter 7: Software Maintenance`
- `Chapter 8: Software Configuration Management`
- `Chapter 9: Software Engineering Management`
- `Chapter 10: Software Engineering Process`

来源：<https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics>

这意味着 SWEBOK 对流程的贡献主要有两点：

1. 它把流程活动拆进多个稳定知识域，而不是把软件工程等同于某一种瀑布或敏捷方法。
2. 它隐含了一个“主线 + 横切支撑”的结构：
   - 主线：需求、架构、设计、构建、测试、运行、维护
   - 横切：配置管理、项目管理、过程管理、质量、安全、经济性、职业实践

## 2. 12207 视角：生命周期过程框架

`ISO/IEC/IEEE 12207:2026` 的官方摘要指出，该标准“establishes a common framework for software life cycle processes”，覆盖软件系统/产品/服务的获取、供给、开发、运行、维护和处置，并以利益相关方参与和客户满意为目标。来源：<https://www.iso.org/standard/90219.html>

IEEE 官方标准页进一步强调：

- 它描述的是从 `conception through retirement` 的完整生命周期；
- 它支持对这些过程进行 `definition`、`control`、`assessment`、`improvement`；
- 这些过程可以被 `concurrently`、`iteratively`、`recursively` 应用于系统及其组成部分；
- 用户应把这些过程映射为适合自己的生命周期阶段与模型。  
  来源：<https://standards.ieee.org/ieee/12207/11416/>

ISO 在线预览目录显示 `12207:2026` 把过程组织为四大类：

- `Agreement processes`
- `Organizational project-enabling processes`
- `Technical management processes`
- `Technical processes`

来源：<https://www.iso.org/obp/ui/en/#!iso:std:90219:en>

对“软件工程主流程”最关键的是后两类：

- `Technical management processes` 负责计划、风险、配置、信息、决策、评审与控制；
- `Technical processes` 负责把需求与约束逐步转化为可运行、可验证、可确认的软件系统。

## 3. 从需求到验证的主流程

### 3.1 12207 给出的主线逻辑

`12207:2026` 的引言说明，该标准覆盖：

- 早期界定利益相关方需求、关注点、优先级与约束；
- 建立需求；
- 在考虑完整问题背景下并行进行设计综合与系统确认；
- 从概念出发，经过运行、维护/持续支持，直至处置。

来源：ISO 在线预览目录中的 `Introduction`：<https://www.iso.org/obp/ui/en/#!iso:std:90219:en>

据此，面向软件团队可以把“需求到验证”的主流程抽象为：

1. `需求获取与澄清`
   - 识别利益相关方、业务目标、约束、优先级
   - 输出：需求来源、问题定义、边界、约束清单

2. `需求分析`
   - 消解冲突、分解需求、明确功能与非功能要求
   - 输出：结构化需求、优先级、依赖、假设、验收关注点

3. `需求规格化`
   - 把需求写成可沟通、可评审、可跟踪、可验证的规格
   - 输出：需求规格说明、验收准则、模型/原型

4. `架构与设计综合`
   - 形成系统/软件结构、关键决策、接口与详细设计
   - 输出：架构描述、设计描述、接口说明、设计决策记录

5. `实现与构建`
   - 将设计落实为代码、配置、脚本、构建产物
   - 输出：源码、构建脚本、可执行产物、单元级测试资产

6. `集成`
   - 将部件组装为更高层级的软件系统
   - 输出：集成基线、集成记录、集成测试结果

7. `验证`
   - 检查产物是否满足规定需求与设计约束
   - 输出：验证计划、测试用例、测试报告、缺陷记录、评审记录

8. `确认`
   - 检查系统是否满足真实使用场景中的利益相关方需求
   - 输出：验收结果、试运行反馈、确认报告、发布/移交决定

### 3.2 SWEBOK 对这条主线的细化

SWEBOK Topics 页对主线各段给出了可直接落地的活动分解：

- `Requirements`
  - `Requirements Elicitation`
  - `Requirements Analysis`
  - `Requirements Specification`
  - `Requirements Validation`
  - `Requirements Management Activities`
  - `Requirements Tracing`
- `Architecture`
  - `Architectural Design`
  - `Architecture Analysis`
  - `Architecture Synthesis`
  - `Architecture Evaluation`
- `Design`
  - `High-Level Design`
  - `Detailed Design`
  - `Design Reviews and Audits`
  - `Verification, Validation, and Certification`
- `Construction`
  - `Coding`
  - `Construction Testing`
  - `Integration`
  - `Test-First Programming`
- `Testing`
  - `Unit Testing`
  - `Integration Testing`
  - `System Testing`
  - `Acceptance Testing`
  - `Test Planning Process`
  - `Test Design and Implementation`
  - `Test Documentation`

来源：<https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics>

这说明在 SWEBOK 视角下，“验证”并不是孤立终点，而是：

- 需求阶段就要开始做 `Requirements Validation`
- 设计阶段就要考虑 `Verification, Validation, and Certification`
- 构建阶段要为验证而构建
- 测试阶段再系统化展开不同层级的验证活动

## 4. 核心工件：按 15289 分类最稳妥

`12207:2026` 明确声明：它`不细化`信息项的名称、格式、显式内容和记录媒介，并把这部分交给 `ISO/IEC/IEEE 15289`。来源：<https://www.iso.org/standard/90219.html>

`15289:2019` 官方摘要说明：

- 它规定生命周期信息项的`purpose and content`；
- 它把信息项按通用文档类型组织；
- 它把 `12207` / `15288` 的过程映射到一组信息项；
- 它允许信息项按项目需要进行组合和拆分。

来源：<https://www.iso.org/standard/74909.html>、<https://standards.ieee.org/ieee/15289/7196/>

因此，面向“需求到验证”主流程，最实用的核心工件可以这样整理：

### 需求阶段工件

- `specification`
  - 需求规格说明
  - 用户/系统/软件需求条目
  - 验收准则
- `description`
  - 业务背景说明
  - 领域模型
  - 用例、场景、原型、模型
- `request`
  - 需求变更请求
- `record`
  - 需求来源、评审意见、追踪关系、优先级记录

### 架构与设计阶段工件

- `description`
  - 架构描述
  - 设计描述
  - 接口描述
  - 决策记录
- `specification`
  - 外部接口规范
  - 关键技术约束和质量属性规格
- `record`
  - 设计评审记录

### 实现与集成阶段工件

- `description`
  - 源码说明、模块说明、构建说明
- `procedure`
  - 构建、集成、部署、回滚步骤
- `record`
  - 构建记录、集成记录、配置基线、变更记录

### 验证与确认阶段工件

- `plan`
  - 验证计划、测试计划、确认/验收计划
- `specification`
  - 测试规格、测试用例、测试环境要求
- `report`
  - 测试报告、缺陷报告、验证报告、确认报告
- `record`
  - 缺陷单、执行记录、覆盖记录、验收结果

### 横切工件

- `plan`
  - 项目计划、质量计划、配置管理计划、风险管理计划
- `policy`
  - 质量策略、变更控制策略、配置策略
- `procedure`
  - 评审、发布、故障处理、变更控制流程

## 5. 原则：从标准直接能提炼出的最重要几条

### 5.1 过程原则

- `过程先于方法`
  - `12207` 明确不规定某一种生命周期模型或开发方法，过程框架可映射到瀑布、增量、迭代、敏捷等不同实践。来源：ISO 12207:2026 `Scope`

- `并发、迭代、递归`
  - `12207` 与 `29148` 都强调过程不是一次性串行穿过，而是可并发、迭代、递归应用。来源：ISO 12207:2026 `Abstract/Scope`，IEEE 29148-2018 标准页。

- `全过程利益相关方参与`
  - `12207` 多次强调 stakeholder involvement 和 customer satisfaction。来源：ISO/IEEE 12207 官方页。

- `过程可裁剪`
  - `12207` 有 `Conformance` 与 `Tailoring process`，说明组织必须按项目背景选择适用过程与深度。来源：ISO 12207 在线目录。

### 5.2 需求原则

- `需求必须是工程对象，而非口头愿望`
  - `29148` 把 requirements engineering 定义为贯穿生命周期的过程与产品集合。来源：IEEE 29148-2018 标准页。

- `好需求要有明确构造和属性`
  - `29148` 明确“defines the construct of a good requirement, provides attributes and characteristics of requirements”。来源：IEEE 29148-2018 标准页。

- `需求要可追踪、可变更管理、可验证`
  - SWEBOK 明确包含 `Requirements Tracing`、`Requirements Change Control`、`Requirements Validation`。来源：SWEBOK Topics 页。

### 5.3 文档/工件原则

- `工件服务于过程，不必拘泥固定模板`
  - `15289` 允许工件组合、拆分，并按生命周期模型裁剪。来源：ISO/IEEE 15289:2019。

- `先定义工件类型，再确定项目模板`
  - `15289` 给出的通用信息项类型比“直接套一份 SRS/SDD 模板”更稳，因为它能跨方法、跨组织复用。来源：ISO/IEEE 15289:2019。

### 5.4 验证/确认原则

- `验证左移`
  - SWEBOK 在需求、设计、构建、测试多个知识域都放入了验证相关活动，意味着验证应前移，而不是只在测试阶段集中发生。来源：SWEBOK Topics 页。

- `验证与确认分离`
  - 实务上应区分“是否满足规定需求/规格”和“是否满足真实场景/用户需要”；`12207` 的引言已经把建立需求、设计综合、系统确认放在同一主线中。来源：ISO 12207 在线预览。

## 6. 一张可直接复用的流程表

| 核心阶段 | 主要目标 | 核心工件 | 关键原则 | 主要标准锚点 |
|---|---|---|---|---|
| 需求获取 | 弄清业务目标、利益相关方、约束 | 需求来源、场景、约束清单 | 利益相关方参与、问题先定义 | 12207, 29148, SWEBOK |
| 需求分析 | 消解冲突并形成结构化需求 | 需求分析记录、优先级、依赖关系 | 迭代、冲突消解、可追踪 | 29148, SWEBOK |
| 需求规格化 | 形成可评审、可验证规格 | SRS/需求规格、验收准则、原型/模型 | 好需求、清晰性、可验证性 | 29148, SWEBOK |
| 架构/设计 | 形成解决方案结构 | 架构描述、设计描述、接口说明 | 逐层综合、评审驱动 | 12207, SWEBOK |
| 实现/构建 | 把设计落实为可运行软件 | 源码、构建脚本、构建记录 | 为验证而构建、持续集成 | SWEBOK, 12207 |
| 集成 | 形成更高层级系统 | 集成基线、集成记录 | 分层集成、配置控制 | 12207, SWEBOK |
| 验证 | 证明满足规定需求 | 测试计划、测试用例、测试报告、缺陷单 | 分层验证、左移验证 | 12207, SWEBOK |
| 确认/验收 | 证明满足真实使用需求 | 验收记录、确认报告、发布决定 | 面向场景、面向价值 | 12207 |

## 7. 对落地实践的建议

如果要把这些标准压缩成一个团队可执行的最小流程，可以采用下面的最小工件集合：

- `需求规格`：把功能、非功能、约束、验收准则写清楚
- `追踪矩阵`：把需求映射到设计、代码、测试
- `架构/设计描述`：至少覆盖结构、接口、关键决策
- `变更记录`：任何需求或设计变化都留痕
- `测试计划与测试报告`：覆盖验证策略与结果
- `配置基线`：确保“拿到的版本”与“被验证的版本”一致

这组最小集合与 `12207 + 29148 + 15289 + SWEBOK` 的共同精神是一致的。

## 备注

- 当前 `12207` 最新正式版是 `2026`；`2017` 已被撤销并由 `2026` 取代。来源：ISO 与 IEEE 官方标准页。
- 当前 `15289:2019` 仍是现行版，但 IEEE 已有面向 `12207:2026` 的 `P15289` 修订项目。来源：IEEE 15289-2019 与 P15289 官方页。
- 本文避免使用二手博客作为事实依据；若后续需要，我可以继续补一版“标准条文对照表”或“适合中小团队的裁剪版流程模板”。
