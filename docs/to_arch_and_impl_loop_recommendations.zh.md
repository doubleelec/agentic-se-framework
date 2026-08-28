# to-arch 与 impl-loop 技能深化建议与演进指南

本文档记录了针对 `to-arch`（架构合成与施工计划制定）与 `impl-loop`（端到端规格-工单-实现交付循环）两个核心自研/编排技能的完整分析、优化建议与演进策略。

---

## 1. 当前机制与核心优势评估

在当前的软件工程技能全景图中，`to-arch` 与 `impl-loop` 形成了清晰的**“战略制图”与“战术巡航”**分工：

- **`to-arch`（战略制图）**：
  - 严格遵循 ISO/IEC/IEEE 42010 架构描述标准；
  - 坚持“零发明”原则（Zero-invention），对决策缺口、事实缺口、术语缺口精准分流；
  - 产出全局架构描述 `docs/architecture.md` 与施工波次计划 `docs/action-plan.md`；
  - 固化粒度绑定的测试分层体系（Unit $\leftrightarrow$ Ticket，Integration $\leftrightarrow$ Spec，System $\leftrightarrow$ Multi-spec / Whole effort）；
  - 彻底解耦运行时拓扑依赖（`architecture.toml` 的 `depends_on`）与施工构建波次（`action-plan.md` 的 Waves）。

- **`impl-loop`（战术巡航）**：
  - 纯编排器设计，不重复造轮子，内嵌调用 `/implement`、`/tdd` 与 `/code-review`；
  - 测试闸门严格从上游（`action-plan.md` 与 `docs/architecture.md`）继承，禁止执行层私自升降测试强度；
  - 状态以 `docs/action-plan.md` 头部恢复点（Resume point）为准，天生支持断点续传与跨会话接续；
  - 单票推进机制（One ticket in flight at a time），保障每个垂直切片的高质量交付。

---

## 2. 关于 `to-arch` 的深化建议

### 2.1 建立质量属性场景（QAS）到测试闸门（Test Gate）的显式追踪链
- **背景**：`to-arch` 在 Step 1 收集 QAS，在 Section 7 规定 Test Architecture。
- **优化点**：对于性能、并发、吞吐量、幂等性等非功能性 QAS，在 `docs/architecture.md` 中不仅记录文字描述，更应显式绑定到对应的测试命令与波次。
- **示例**：
  > `QAS-02 (订单查询时延 < 200ms)` $\rightarrow$ 绑定到 Wave 2 的 S3 集成测试闸门 `pytest tests/e2e/test_latency.py`。

### 2.2 强化 Reconcile 模式中的“架构漂移快速自检清单”
- **背景**：`to-arch` 在里程碑或发现漂移时通过 `reconcile` 模式对账。
- **优化点**：在 Step 1 盘点中，固化 3 条零漂移规则：
  1. **ADR 漂移检查**：是否存在新落盘的 `docs/adr/*.md` 尚未在 `docs/architecture.md` 第 5 节中索引？
  2. **模块边界漂移检查**：是否存在 `architecture.toml` 或 `module.toml` 中新增的模块/子模块尚未在逻辑分解视图中呈现？
  3. **接缝漂移检查**：是否存在 `[public_api].exposed` 新增了突破原定 Seam 的接口？若有，需确认是否补充 ADR 或更新架构描述。

### 2.3 波次并行组（Parallel Groups）的显式标注
- **优化点**：在 `action-plan.md` 的 Waves 章节中，针对同波次内可并行的切片明确标注 `Parallel group: [S1, S2]`，便于未来多 Subagent 或多人并发认领与推进。

---

## 3. 关于 `impl-loop` 的深化与鲁棒性建议

### 3.1 结尾处显式闭合 `action-plan.md` 进度（核心必选动作）
- **优化点**：在单 Spec 下所有 Tickets 交付完毕且 Spec 级 Integration Gate 通过后，`impl-loop` **必须在退出前执行完工回写**：
  1. **更新 Slice 状态**：将该 Slice 的 `Status` 置为 `done (<commit_sha>)`；
  2. **更新 Notes 记录**：记录 `all N tickets resolved, integration gate passed (<gate_cmd>)`；
  3. **推进 Resume Point 头部**：
     - 若当前 Wave 还有在途/待办 Slice $\rightarrow$ 更新 in-flight / pending 状态；
     - 若当前 Wave 全部 Slice 已 Done $\rightarrow$ 将 Resume Point 推进至 `Wave <k+1>`；
     - 若已通过最终波次的 System Test $\rightarrow$ 标记 `Effort complete`。

### 3.2 失败熔断（Bounded Retry 耗尽）后的归因与技能分流
- **优化点**：当单票闸门经过 1 次重试仍未通过时，`impl-loop` 停止循环并将 Ticket 保持 `claimed`，同时输出针对性的下一步技能建议：
  - **因接缝模糊或依赖渗漏导致的失败** $\rightarrow$ 建议调用 `/improve-codebase-architecture` 或 `/codebase-design` 重构接缝；
  - **因需求假设冲突导致的失败** $\rightarrow$ 建议调用 `/grill-with-docs` 澄清该 Ticket 的边界；
  - **因第三方库或环境事实不明确** $\rightarrow$ 建议调用 `/research`。

### 3.3 长切片链条下的 Context 预算与主动断点机制
- **优化点**：当一个 Spec 拆解出较多工单（如 $>4$ 张票）或产生大量代码修改时，模型上下文会迅速膨胀。
- **机制**：每完成一张票，`impl-loop` 自动保证 `action-plan.md` 和 ticket 状态已即时持久化，并可在单票完成时提示用户：*“当前 Ticket 已闭环且状态已落盘，可选择继续下一张票，或开启新会话输入 `/impl-loop` 无缝续跑”*。

### 3.4 规范在途工单在 Notes 列的微观计数
- **格式建议**：
  - 在途中：`Status: in-progress | Notes: ticket 02/05 (01 resolved)`
  - 完工时：`Status: done (a1b2c3d) | Notes: 05/05 tickets resolved, integration gate passed`

### 3.5 技能自主发现与调用（Model Invocation）机制保障
- **排查出的阻塞点**：上游 `to-spec`、`to-tickets`、`implement` 最初携带 `disable-model-invocation: true`，导致 Agent 在会话内无法感知到这些技能并报错“不在可用目录中”；且 `impl-loop` 指令中使用了“run /to-spec”等斜杠命令写法，使 Agent 误以为需等待人类输入。
- **已实施修复**：
  1. 移除 `to-spec`、`to-tickets`、`implement` 的 `disable-model-invocation: true`，使其对 Agent 恢复可见与可调用；
  2. 重构 `impl-loop/SKILL.md` 指令，明确交代“Agent 为主动执行者”，当缺失工件时主动加载执行对应技能，不再停顿或提示人类输入命令。

---

## 4. 总结与落地路线

| 优化项目 | 涉及技能/工件 | 优先级 | 预期效果 |
| :--- | :--- | :---: | :--- |
| **完工回写 `action-plan.md`** | `impl-loop` / `docs/action-plan.md` | **P0（已采纳）** | 确保每个 Spec 交付完成后施工总账和恢复点 100% 准确推进。 |
| **解除前置技能的模型调用限制** | `to-spec` / `to-tickets` / `implement` | **P0（已采纳）** | 修复 Agent 误报“技能不在目录中”的阻断问题，实现全自主编排。 |
| **QAS 到测试闸门的追踪** | `to-arch` / `docs/architecture.md` | P1 | 保证非功能性架构需求有明确的自动化测试闸门兜底。 |
| **失败熔断分流指引** | `impl-loop` | P1 | 避免 Agent 在测试不通时死循环，精准引导回退重构。 |
| **Reconcile 漂移自检规则** | `to-arch` | P2 | 增强架构对账的自动化与标准化。 |
