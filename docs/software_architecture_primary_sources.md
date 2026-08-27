# 软件体系结构一手资料研究：42010、架构视点、质量属性、ATAM、架构决策

## 目标

基于一手资料梳理软件体系结构实践，重点覆盖：

- `ISO/IEC/IEEE 42010`
- 架构视点（viewpoint）与视图（view）
- 质量属性与质量属性场景
- `ATAM`
- 架构决策与 `ADR`

输出重点不是“概念百科”，而是一套可直接落地的最小方法。

## 执行摘要

- `ISO/IEC/IEEE 42010:2022` 的核心不是规定某种固定图纸，而是规定“架构描述”应如何围绕干系人、关注点、视点、视图、对应关系、决策与依据来组织。
- 视点不是图本身，而是“如何构造、解释、分析某类视图”的约定。先有视点，后有视图。
- 质量属性不能只写“高性能”“高可用”，必须转成场景；SEI 明确把质量属性场景作为架构推理和评估的基础。
- 在还没有稳定架构时，先用 `QAW` 澄清关键质量属性场景；有候选架构后，再用 `ATAM` 做权衡分析。
- 架构决策需要持续记录。`42010:2022` 已明确把“记录架构决策及其 rationale”纳入架构描述内容。
- 团队最小可行做法是：`QAW -> 42010 架构描述 -> ADR -> ATAM -> 持续回写`。

## 一手资料与关键结论

### 1. ISO/IEC/IEEE 42010:2022

官方目录页与在线目录显示，该标准当前关注的章节包括：

- `6.2` 识别干系人
- `6.3` 识别干系人视角（stakeholder perspectives）
- `6.4` 识别关注点
- `6.6` 纳入架构视点
- `6.7` 纳入架构视图
- `6.9` 记录架构对应关系（correspondences）
- `6.10` 记录架构决策与依据
- `8` 规定架构视点与模型种类（model kinds）

这说明 `42010:2022` 对架构工作的基本要求，不是“画几张图”，而是建立一条可追踪链路：

`干系人 -> 关注点 -> 视点 -> 视图/视图构件 -> 对应关系 -> 决策与依据`

来源：

- ISO Online Browsing Platform: <https://www.iso.org/obp/ui/en/#!iso:std:74393:en>
- IEEE 标准页: <https://standards.ieee.org/ieee/42010/6846/>

### 2. 42010 对“架构”和“架构描述”的区分

`ISO-Architecture.org` 对标准概念模型的解释指出：

- 架构是“实体在其环境中的基本概念或性质，体现在元素、关系以及其设计和演化原则中”
- 架构描述（`Architecture Description`, `AD`）是表达架构的工件

这个区分非常重要。很多团队把“架构文档”误当成“架构本身”，导致讨论一直停留在文档格式，而不是系统关键性质。

来源：

- ISO-Architecture 概念模型页: <http://www.iso-architecture.org/42010/cm/>

### 3. 视点与视图

`Getting Started with ISO/IEC/IEEE 42010` 给出了非常直接的实践解释：

- 先识别干系人
- 再识别其关注点
- 选择一个或多个视点，使每个关注点至少被一个视点覆盖
- 为每个视点写明定义，说明适用干系人、关注点、模型种类、建模约定和来源
- 最后基于视点产出视图，并记录视图间的一致性/不一致性

该页面还明确说明：视点至少应包含以下内容：

- 一个或多个关注点
- 典型干系人
- 一个或多个模型种类
- 每种模型的语言、记法、建模技术、分析方法或其他操作约定
- 来源

这意味着：

- 逻辑视图、部署视图、运行时视图不是“固定标准答案”
- 它们只有在明确覆盖了某类关注点并规定了表达约定时，才构成一个合格视点

来源：

- ISO-Architecture Getting Started: <http://www.iso-architecture.org/ieee-1471/getting-started.html>

### 4. 质量属性

SEI 关于质量属性的资料有两个关键结论：

- 质量属性对架构有显著影响，尤其是性能、安全、可修改性、可用性、可靠性、互操作等
- 质量属性要求需要用场景来精确定义，否则无法分析、比较和评估

SEI 在 `Reasoning About Software Quality Attributes` 中明确指出：

- 要想分析或评估系统质量，首先需要刻画适用的质量属性需求
- 质量属性场景与功能需求中的用例类似，是规格化质量需求的基本方法
- “general scenarios” 可以作为生成具体质量属性场景的模板

来源：

- SEI `Quality Attributes`: <https://www.sei.cmu.edu/library/quality-attributes/>
- SEI `Reasoning About Software Quality Attributes`: <https://www.sei.cmu.edu/library/reasoning-about-software-quality-attributes/>

### 5. QAW：在架构成形前发现质量属性驱动因素

SEI 的 `Quality Attribute Workshop` 明确指出：

- `QAW` 不要求已经存在软件架构
- 它用于在架构形成前，从业务/使命目标中识别关键质量属性
- 输出是“优先级排序并细化后的场景”
- 这些场景之后可以直接作为 `ATAM` 的 seed scenarios

QAW 典型步骤包括：

- 方法介绍
- 业务/项目驱动说明
- 现有技术方案或高层技术设想说明
- 识别架构驱动因素
- 头脑风暴场景
- 场景合并
- 场景排序
- 细化前若干高优场景

来源：

- SEI `Quality Attribute Workshop Collection`: <https://www.sei.cmu.edu/library/quality-attribute-workshop-collection/>
- SEI `Quality Attribute Workshops (QAWs), Third Edition`: <https://doi.org/10.1184/R1/6582656.v1>

### 6. ATAM：在候选架构上做质量权衡分析

SEI 对 `ATAM` 的定义非常明确：

- 它是一种软件架构分析技术
- 它关注架构决策如何影响质量属性目标
- 它用于识别风险、敏感点、权衡点，并把这些结果和业务目标关联起来

SEI 的 `ATAM Collection` 给出了九步法：

1. 介绍 `ATAM`
2. 说明业务驱动
3. 说明架构
4. 识别架构方法/策略
5. 生成质量属性 utility tree
6. 分析架构方法
7. 头脑风暴并排序场景
8. 基于高优场景再次分析
9. 汇报结果

ATAM 的关键价值，不在于给架构打一个“合格/不合格”的分数，而在于把以下内容显式化：

- 风险
- 非风险
- 敏感点
- 权衡点
- 风险主题

来源：

- SEI `ATAM: Method for Architecture Evaluation`: <https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/>
- SEI `Architecture Tradeoff Analysis Method Collection`: <https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/>

### 7. 42030：把评估组织成一个正式工作产品

`ISO/IEC/IEEE 42030:2019` 把架构评估定义为一个可组织、可记录的框架，其目标包括：

- 验证架构是否回应干系人关注点
- 评估架构是否适合其目标用途
- 识别风险与机会
- 支持决策

这和 `ATAM` 并不冲突。可以把 `42030` 看成评估工作的标准化框架，把 `ATAM` 看成其中一种成熟的场景化评估方法。

来源：

- ISO 42030 页: <https://www.iso.org/standard/73436.html>
- IEEE 42030 页: <https://ieeexplore.ieee.org/document/8767001>

### 8. 架构决策与 ADR

关于架构决策，至少有两条值得直接采用的一手/准一手实践：

- `42010:2022` 已把“记录架构决策和依据”纳入架构描述内容
- Thoughtworks 明确建议用轻量 ADR 记录重要架构决策，并把记录放在源码仓库中，而不是 wiki

Thoughtworks 对 `Lightweight Architecture Decision Records` 的建议包括：

- 记录重要架构决策及其上下文和后果
- 存放在版本库中
- 保持与代码同步

Joel Parker Henderson 的 ADR 仓库对 ADR 给出的通用定义是：

- ADR 是记录一个重要架构决策，以及该决策的上下文与后果的文档

来源：

- Thoughtworks Technology Radar: <https://www.thoughtworks.com/en-us/radar/techniques/lightweight-architecture-decision-records>
- ADR 仓库: <https://github.com/joelparkerhenderson/architecture-decision-record>

## 落地方法：一套最小但完整的架构工作流

下面给出一套可在团队直接执行的最小方法，兼容 `42010 + QAW + ATAM + ADR`。

### 阶段 1：用 QAW 找到“真正驱动架构的质量属性”

适用时机：

- 项目刚启动
- 需求多但架构方向还不稳
- 业务方在说“高性能、高可用、高安全”，但定义模糊

做法：

1. 召集关键干系人
2. 先讲业务目标、约束、风险承受度
3. 收集质量属性场景
4. 投票排序
5. 细化前 `4-5` 个场景

建议输出：

- 干系人清单
- 业务目标清单
- 约束清单
- 排序后的质量属性场景列表
- 初始架构驱动因素列表

质量属性场景模板：

```text
场景名称：
质量属性：
刺激源：
刺激：
环境：
受影响构件/资产：
期望响应：
响应度量：
业务影响：
优先级：
```

最少要把“期望响应”和“响应度量”写清，否则无法进入后续评估。

### 阶段 2：按 42010 组织架构描述

适用时机：

- 已经有候选方案
- 需要形成可以评审、沟通、追踪的架构工作产品

建议用一个 `Architecture Description` 文档或目录结构来承载，最低包含：

1. 架构描述标识与范围
2. 实体/系统边界与环境
3. 干系人
4. 关注点
5. 视点目录
6. 基于视点生成的视图
7. 视图之间的对应关系
8. 架构决策与依据
9. 已知风险、约束与未决问题

建议的最小视点集：

- 上下文视点：回答系统边界、外部依赖、参与者
- 逻辑分解视点：回答职责划分、模块边界、核心关系
- 运行时视点：回答并发、时序、通信、故障路径
- 部署视点：回答节点、网络区、容量、伸缩、隔离
- 运维/安全视点：回答观测性、权限、密钥、审计、恢复

注意：

- 不要先问“要画几张图”
- 先问“哪些关注点必须被覆盖”

### 阶段 3：把关键选择写成 ADR

适用时机：

- 一旦某项选择会长期影响系统演化，就应该写 ADR

典型 ADR 触发器：

- 选型：数据库、消息系统、搜索引擎、API 风格
- 结构：单体/模块化单体/微服务
- 交互：同步调用还是事件驱动
- 数据：强一致还是最终一致
- 安全：鉴权边界、租户隔离方式
- 运维：灰度、回滚、观测、灾备策略

建议 ADR 最小模板：

```md
# ADR-0001 标题

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
当前业务背景、技术约束、质量属性目标、备选方案

## Decision
最终选择及适用边界

## Consequences
正面影响、负面影响、新增约束、后续动作

## Rationale
为什么这样选，为什么不选其他方案

## Related
相关视图、相关需求、相关工单、相关 ADR
```

实践建议：

- 一条 ADR 只记录一个关键决策
- 放到仓库，例如 `docs/adr/`
- 在架构视图、设计文档、代码 PR 中互相链接

### 阶段 4：用 ATAM 评估候选架构

适用时机：

- 方案已经比较清晰
- 需要在多个质量属性之间做取舍
- 需要正式识别架构风险

执行重点：

1. 复述业务驱动
2. 复述架构与关键策略
3. 建立 `utility tree`
4. 用高优场景检查架构策略
5. 识别风险、敏感点、权衡点
6. 汇总成风险主题和后续行动

建议产出：

- `utility tree`
- 场景分析记录
- 风险清单
- 非风险清单
- 敏感点清单
- 权衡点清单
- 整改路线图

一个实用判断标准：

- 如果评审会最后只留下“建议优化缓存/解耦/加监控”，那不是完整的 ATAM
- 如果留下的是“哪类场景会失败、为什么失败、由哪个决策导致、可接受边界是什么”，才接近 ATAM 的价值

### 阶段 5：把评估结果回写到架构基线

这是很多团队最容易漏掉的一步。

正确做法：

- 将 `ATAM` 发现回写到 `42010` 架构描述
- 把需要长期保留的结论转成 `ADR`
- 把需要执行的技术动作转成 backlog
- 把需要验证的风险转成测试、演练、容量验证或安全验证

最终形成闭环：

`场景 -> 视点/视图 -> 决策 -> 评估 -> 整改 -> 更新架构描述`

## 团队可直接采用的文档结构

```text
docs/
  architecture/
    architecture-description.md
    stakeholders.md
    concerns.md
    viewpoints/
      context-viewpoint.md
      logical-viewpoint.md
      runtime-viewpoint.md
      deployment-viewpoint.md
      operations-security-viewpoint.md
    views/
      system-context.md
      logical-decomposition.md
      runtime-scenarios.md
      deployment-topology.md
      observability-security.md
    evaluation/
      qaw-2026-08.md
      atam-2026-08.md
  adr/
    ADR-0001-choose-event-bus.md
    ADR-0002-adopt-modular-monolith.md
```

## 最小治理规则

- 每个重要关注点至少被一个视点覆盖
- 每个高优质量属性场景至少映射到一个视图和一个决策
- 每个重大架构决策必须有 `ADR`
- 每次正式评估后，必须更新架构描述和 ADR 状态
- ADR 不写长篇论文，只记录关键取舍与后果

## 常见误区

### 误区 1：把视点当成固定图种

错误做法：

- 直接套“4+1”或“C4”然后结束

更好的做法：

- 先从干系人关注点反推需要哪些视点

### 误区 2：把质量属性写成口号

错误做法：

- “系统要高性能、高可用、可扩展”

更好的做法：

- 写成可分析、可测量的场景

### 误区 3：评审只看图，不看决策

错误做法：

- 图很漂亮，但不知道为什么这样设计

更好的做法：

- 图、ADR、场景分析三者联动

### 误区 4：ATAM 只做一次

错误做法：

- 项目初期做一次架构评审，之后再也不更新

更好的做法：

- 在关键里程碑、重大需求变化、重大质量事故后复评

## 如果只允许做三件事

资源有限时，优先做这三件事：

1. 组织一次半天 `QAW`，产出前 `10` 个质量属性场景
2. 用 `42010` 的思路整理最小架构描述，至少写清干系人、关注点、视点、视图、决策
3. 对前 `5` 个高风险场景做一次轻量 `ATAM`，并把结论写成 `ADR + backlog`

## 推荐的 2 周启动方案

### 第 1 周

- 第 1 天：收集干系人、业务目标、约束
- 第 2 天：开展 `QAW`
- 第 3 天：整理质量属性场景并排序
- 第 4-5 天：完成最小架构描述与首批视图

### 第 2 周

- 第 1-2 天：补写首批 `ADR`
- 第 3 天：开展轻量 `ATAM`
- 第 4 天：整理风险、敏感点、权衡点
- 第 5 天：转化为整改计划、验证计划和文档更新

## 结论

如果把这些一手资料压缩成一句话：

> 用 `42010` 组织“怎么描述架构”，用 `QAW` 找到“什么质量属性真正驱动架构”，用 `ATAM` 检查“这些决策如何产生权衡与风险”，再用 `ADR` 把关键选择持续沉淀到仓库里。

这套组合的优点是：

- 既有标准约束，又不依赖某一种图法
- 既覆盖架构表达，也覆盖架构评估
- 既适合项目启动，也适合持续治理

## 参考来源

- ISO/IEC/IEEE 42010:2022 Online Browsing Platform: <https://www.iso.org/obp/ui/en/#!iso:std:74393:en>
- IEEE/ISO/IEC 42010-2022: <https://standards.ieee.org/ieee/42010/6846/>
- ISO-Architecture Getting Started with ISO/IEC/IEEE 42010: <http://www.iso-architecture.org/ieee-1471/getting-started.html>
- ISO-Architecture Conceptual Model: <http://www.iso-architecture.org/42010/cm/>
- ISO/IEC/IEEE 42030:2019: <https://www.iso.org/standard/73436.html>
- IEEE 42030-2019: <https://ieeexplore.ieee.org/document/8767001>
- SEI ATAM report: <https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/>
- SEI ATAM collection: <https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/>
- SEI QAW collection: <https://www.sei.cmu.edu/library/quality-attribute-workshop-collection/>
- SEI QAW Third Edition: <https://doi.org/10.1184/R1/6582656.v1>
- SEI Quality Attributes: <https://www.sei.cmu.edu/library/quality-attributes/>
- SEI Reasoning About Software Quality Attributes: <https://www.sei.cmu.edu/library/reasoning-about-software-quality-attributes/>
- Thoughtworks Lightweight ADRs: <https://www.thoughtworks.com/en-us/radar/techniques/lightweight-architecture-decision-records>
- Architecture Decision Record repository: <https://github.com/joelparkerhenderson/architecture-decision-record>
