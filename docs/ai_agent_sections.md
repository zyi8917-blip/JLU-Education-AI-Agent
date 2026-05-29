## 十、AI Agent 八股 · 对照简历项目 {#sec10}

> **来源：** 你整理的 AI Agent 面试 100 题（节选与「吉大未来学习·AI 智能教育 Agent」相关的部分）。  
> **简历项目技术栈：** Next.js 15、Flask、Vue 3、LangGraph、Chroma、DeepSeek API、SSE、RAG。

### 10.0 简历技术 → 本题库映射

| 简历写法 | 必背小节 |
|---------|---------|
| RAG + Chroma + Flask 检索 API | **10.3** Q3～Q6 |
| LangGraph 三节点工作流 | **10.2** Q2、Q3 |
| SSE 流式 + Next.js `/api/chat` 网关 | **10.4** Q1、Q2 |
| API Key 放服务端、历史裁剪 | **10.4** Q3～Q5 |
| 压测 benchmark / 20 轮 100% | **10.5** Q1、Q2 |
| Agent vs 普通聊天 | **10.1** Q1、Q3 |

---

### 10.1 基础概念（5 题）

#### Q1. 什么是 AI Agent？它与传统 AI 系统有何不同？

**答：** AI Agent（智能体）是能**感知环境 → 推理决策 → 执行动作 → 根据反馈调整**以达成目标的系统，核心环节：感知、推理、行动、反馈。

| 对比 | 传统 AI | AI Agent |
|------|---------|----------|
| 模式 | 输入→处理→输出，被动响应 | 主动规划、多轮交互、可调工具 |
| 能力 | 分类/匹配/单轮 QA | 任务分解、工具调用、记忆、纠错 |
| 例子 | 固定知识库问答 | 检索课件 + 调 API + 流式回答 |

**【本项目】** 课堂 Agent 不是「只聊天」：学生提问 → **Chroma RAG 检索** Top-4 课件片段 → **注入 Prompt** → **DeepSeek 流式生成**；测评结束走 **LangGraph** 批量评分与报告组装，属于典型 LLM Agent 应用闭环。

---

#### Q2. LLM Agent 的核心能力有哪些？

**答：** 归纳为五点：

1. **任务理解与分解**：把「帮我分析学习力」拆成评分、报告、画像等子任务。
2. **规划与推理**：CoT、ReAct 等多步推理。
3. **工具调用（Tool Use）**：检索 API、数据库、代码解释器等。
4. **记忆管理**：短期对话上下文 + 长期向量记忆（RAG）。
5. **自我反思与纠错**：根据执行结果调整策略（Reflexion 等）。

**【本项目】** 工具链包括：Flask `/api/v1/rag/course`（检索）、LangGraph 节点（评测/报告）、Next.js `/api/chat`（调模型）；记忆上 **Chroma 长期知识** + **12 轮短期对话**。

---

#### Q3. Agent 和 Chatbot 的本质区别是什么？

| 维度 | Chatbot | AI Agent |
|------|---------|----------|
| 目标 | 完成对话 | **完成任务** |
| 主动性 | 被动回答 | 主动规划、调工具、可追问澄清 |
| 状态 | 常无长期状态 | 有记忆与状态跟踪 |
| 输出 | 纯文本 | 文本 + API 调用 + 结构化数据（如 `portrait_data`） |
| 错误处理 | 难纠正 | 可重试、换工具、降级（如 keyword 检索） |

**【本项目】** 若只做 Chatbot，只会把当前页 `slideContext` 拼进 Prompt；做成 Agent 后增加 **RAG 召回全库课件**、**测评 complete 一次产出画像上下文**，能「做事」而不只是「说话」。

---

#### Q4. Agent 是否必须具备「目标导向」？为什么？

**答：** **是。** 无目标则退化为随机响应，无法衡量有效性。目标驱动规划、工具选择、记忆检索。

- 显式目标：用户指令「根据测评结果给学习建议」。
- 隐式目标：系统预设「提高回答与课件一致性」。

**【本项目】** 课堂模式目标是 **课件 grounded 答疑**；测评链路目标是 **一次 complete 输出可消费的 portrait_data**，目标清晰才可验收（20/20 RAG 命中、流式成功率 100%）。

---

#### Q5. 为什么说「LLM 是构建通用 Agent 的理想基座」？

**答：**

- **强泛化**：跨领域语言理解与常识。
- **零/少样本**：新任务少样本即可适配。
- **自然语言接口**：直接理解人类指令并生成可执行逻辑。
- **模块化扩展**：Function Calling、RAG、工作流框架（LangGraph）可插拔。

对比传统符号 Agent / 纯 RL Agent：任务专用、泛化差、开发成本高。LLM + 工具 + 记忆是当前主流范式。

---

### 10.2 架构 · LangGraph 与状态管理（6 题）

#### Q1. 典型 LLM Agent 架构包含哪些模块？

**答：**

| 模块 | 作用 |
|------|------|
| 输入解析 | 用户指令 → 结构化任务 |
| 规划器 Planner | 分解任务、生成计划 |
| 推理引擎 | CoT / ReAct 多步推理 |
| 工具执行器 | 调 API、检索、写库 |
| 记忆系统 | 短期上下文 + 长期向量库 |
| 反馈环 | 根据工具结果决定继续/重试/结束 |
| 输出生成 | 整合结果返回用户 |

**【本项目】** Next.js `/api/chat` = 网关 + 编排入口；Flask RAG = 工具层；LangGraph = 测评后 **Planner+Executor**；Chroma = 长期记忆；Vue/Next 前端 = 交互层。

---

#### Q2. LangGraph 在你项目中如何工作？（对照 AgentExecutor）

**答（八股）：** LangChain 的 **AgentExecutor** 是「LLM 选工具 → 执行 → Observation → 循环直到 Final Answer」。**LangGraph** 用 **StateGraph** 显式定义节点与边，状态 TypedDict 在节点间传递，适合**固定流程、可测试、可观测**的多步任务。

**【本项目】** `learning_power/backend/app/agents/assessment_workflow.py`：

```
START → evaluate_answers → generate_report → prepare_portrait → END
```

- `evaluate_answers`：LLM 批量评测评题答案  
- `generate_report`：组装报告字段（总分、评语等）  
- `prepare_portrait`：生成 `portrait_data`（`total_dict`、`rating_dict`、`feedback_dict`、`ready_for_chat: true`）

测评 `POST .../complete` **一次调用** `_WORKFLOW.invoke()`，画像 Agent 直接消费，无需前端二次拼装。比把逻辑堆在 Controller 里更清晰，也比开放式 ReAct 循环更可控。

---

#### Q3. 如何实现 Agent 的状态管理（State Management）？

**答：**

1. **显式状态对象**：字典/TypedDict 记录当前阶段、已完成子任务、工具历史。
2. **持久化**：关键状态写 DB，支持跨会话恢复。
3. **状态机**：限定合法转移，防止跳步。
4. **版本/快照**：支持回滚。

**【本项目】** LangGraph 使用 `AssessmentWorkflowState`（`session_id`、`question_answer_pairs`、`report_payload`、`portrait_data`、`workflow_ms` 等）。课堂对话状态在 **messages 数组** + **服务端历史裁剪**（12 轮 / 约 14K 字符）中维护。

---

#### Q4. Memory 模块分哪几类？各自作用？

| 类型 | 特点 | 作用 |
|------|------|------|
| **短期记忆** | 当前会话最近 N 轮 | 对话连贯 |
| **长期记忆** | 向量库 / DB 持久化 | 跨会话、领域知识 |
| **工作记忆** | 当前任务中间变量 | ToT / 多步推理临时状态 |

**【本项目】** 短期 = `/api/chat` 的 `messages`（裁剪后送模型）；长期 = **Chroma `course_agent_kb`**（8 条 chunk：课件 QA、Markdown、PPT 文本）；工作记忆 = LangGraph 各节点写入的 `report_payload` 等中间态。

---

#### Q5. 短期记忆与长期记忆如何协同？

**答：** 新请求到来 → 用 query **检索长期记忆 Top-K** → 片段 **拼入 Prompt（短期上下文）** → 模型生成 → 任务结束后可将摘要 **写回长期记忆**（可选）。

**【本项目】** 学生提问 → `retrieveCourseContext(query, 4)` → 命中片段 append 到 system 的 `## Retrieved knowledge (RAG)` → 与最近 12 轮 user/assistant 一起送 DeepSeek。检索失败则 **keyword 降级**，避免空转。

---

#### Q6. 多 Agent 协作的设计难点？（了解）

**答：** 通信协议、共享状态一致性、责任归属、死锁、性能开销、评估复杂。解决：中心化协调器、消息队列、超时、trace_id 全链路追踪。

**【本项目】** 当前为 **单 Agent + 固定工作流**，未做多 Agent 协作；面试可说「测评 LangGraph 三节点是单进程内编排，若扩展可拆成评分 Agent / 报告 Agent 并由 Meta-Agent 路由」。

---

### 10.3 推理 · RAG · 知识增强（8 题）

#### Q1. Chain-of-Thought（CoT）如何提升推理能力？

**答：** 引导 LLM **显式写出中间步骤**再得结论，提升复杂题准确率、可解释性，减少跳步幻觉；便于判断何时需要调工具。

**局限：** 单路径、难回溯。开放域、需外部事实的任务更适合 **ReAct**。

**【本项目】** 测评评分节点内部 LLM 对每道题做 **分维度分析**（隐含 CoT）；课堂答疑则 **RAG 提供依据** 再生成，相当于「开卷 CoT」。

---

#### Q2. ReAct 框架原理？相比 CoT 有何优势？

**答：** **ReAct = Reason + Act 交替：**

1. **Thought**：分析当前该做什么  
2. **Action**：选工具并调用  
3. **Observation**：读工具结果  
4. 循环直到 **Final Answer**

| 维度 | CoT | ReAct |
|------|-----|-------|
| 信息来源 | 仅模型内部 | 可拉取外部真实数据 |
| 准确性 | 易幻觉 | 观测可验证 |
| 场景 | 封闭推理（数学） | 开放域（搜索、RAG） |

**【本项目】** 课堂链路等价于简化 ReAct：**Thought**（是否需要课件）→ **Action**（调 RAG API）→ **Observation**（Top-4 chunks）→ **Answer**（流式生成）。未做开放式多工具循环，避免死循环与成本失控。

---

#### Q3. RAG 在 Agent 中如何用于长期记忆？

**答：** **RAG = Retrieval-Augmented Generation**

1. **写入**：交互、文档、FAQ 切片 → embedding → 存入向量库  
2. **读取**：query 向量检索 Top-K  
3. **增强**：检索结果拼入 Prompt，再让 LLM 生成  

优势：跨会话复用、动态更新、比微调便宜、减少胡编。

**【本项目】** 离线：`course_qa.json`、`class_agent_QA.md`、PPT JSON → `load_chunks()` → Chroma `PersistentClient`。在线：Next.js `mode=course` 时 Flask `GET /api/v1/rag/course?query=&top_k=4` → 注入 system prompt。

---

#### Q4. 向量数据库（Chroma）如何与 Agent 集成？

**答：**

1. 选 embedding（OpenAI / 开源 bge 等；Chroma 可内置）  
2. 文档切片 → `collection.add(ids, documents)`  
3. 封装 `retrieve(query, top_k)` → `collection.query(query_texts=[query], n_results=k)`  
4. Agent 在推理前调用 retrieve，结果注入上下文  

**【本项目】** collection 名 `course_agent_kb`，路径 `future_learning_demo/.chroma`；Next.js `chroma-store.ts` 优先调 Flask，失败 **keyword fallback**；响应头 `X-RAG-Source: chroma|keyword|none` 可观测。

---

#### Q5. 外部知识库（RAG）vs 微调：哪个更适合注入领域知识？

| 维度 | RAG | 微调 |
|------|-----|------|
| 更新 | 改文档即可 | 重新训练 |
| 容量 | 存储扩展 | 受参数限制 |
| 准确性 | 可引用原文 | 可能失真 |
| 成本 | 低 | 高 |
| 适用 | 事实性、动态知识（课件、FAQ） | 风格、话术、隐式规则 |

**【本项目】** 课件每学期更新，用 **RAG** 最合适；若要做「固定测评评语风格」可叠加轻量 LoRA，当前未做微调。

---

#### Q6. 记忆检索 Top-K 对性能有何影响？

| K | 优点 | 缺点 |
|---|------|------|
| 小（1～2） | Token 少、快 | 易漏关键片段 |
| 中（3～5） | 平衡 | 常用默认 |
| 大（8+） | 信息全 | Prompt 长、噪声多、贵 |

**【本项目】** 固定 **Top-4**：8 条 chunk 规模下 4 条已够覆盖；压测 **20/20 轮 RAG 命中**。若扩库可试 K=5 + Rerank。

---

#### Q7. 如何避免 Agent 推理死循环？

**答：** 最大步数限制、状态去重、禁止连续重复同一工具、超时、Prompt 要求发现重复则停止。

**【本项目】** LangGraph **线性三节点**，无循环边；`/api/chat` 单次请求一次 RAG + 一次流式 completion；用户 **AbortController** 可中断，避免无限生成。

---

#### Q8. 多步推理中的错误传播如何缓解？

**答：** 中间结果校验、多路径（ToT）、回溯、子任务解耦、Reflexion 事后反思、关键步骤规则校验。

**【本项目】** RAG 为空时 **不硬编**，走 keyword 或明确「资料不足」；流式网关记录 `ragSource/ragChunks` 便于排查哪一步断了。

---

### 10.4 工具调用 · SSE 流式 · 安全（6 题）

#### Q1. OpenAI Function Calling / 工具调用原理是什么？

**答：** 预注册函数 **名称 + 描述 + JSON Schema** → LLM 输出结构化 `{name, arguments}` 而非乱写代码 → 应用层执行函数 → 结果作为 Observation 回传 LLM → 可多轮直到 Final Answer。

优势：可解析、可校验、防 SQL/命令注入式胡写。

**【本项目】** 未直接用 OpenAI tools 参数，而是 **固定流程**：`mode=course` 必调 RAG 工具（Flask API），等价于「白名单单工具 + 编排代码」，更安全可控。

---

#### Q2. SSE 是什么？为什么用 SSE 做 LLM 流式输出？

**答：** **Server-Sent Events**：HTTP 长连接，`Content-Type: text/event-stream`，服务端单向推送文本块。

对比 WebSocket：SSE **单向够用**（模型→用户），基于 HTTP，与 Next.js Route Handler 兼容好。

**【本项目】** `/api/chat` 返回：

```http
Content-Type: text/event-stream; charset=utf-8
Cache-Control: no-cache, no-transform
Connection: keep-alive
```

客户端边收边渲染「打字机」；`wrapStreamWithMetrics` 记录 **首 token 时间**（平均 907ms，P95 1452ms）。

---

#### Q3. 如何让 LLM 安全地调用外部 API？（API Key 放哪）

**答：**

- **设计层**：工具白名单、参数校验、最小权限  
- **执行层**：Key 仅存 **服务端**环境变量，前端只调同源 BFF  
- **监控层**：日志审计、异常拦截  

**【本项目】** DeepSeek `OPENAI_API_KEY` 只在 Next.js 服务端；浏览器只请求 `/api/chat`，**Key 不出前端**。Flask RAG 内网 `127.0.0.1:5000`，不暴露向量库。

---

#### Q4. 如何防止 LLM 滥用或误用工具？

**答：** 最小权限、白名单、敏感操作二次确认、沙箱、速率限制、全量审计。

**【本项目】** 课堂 Agent **不能** arbitrary 调 shell/删库；仅允许 **RAG 检索 + 聊天 completion**；无 Key 时 **脚本关键词模式**，限制能力边界。

---

#### Q5. 幻觉（Hallucination）在 Agent 中危害为何更大？

**答：** Chatbot 幻觉只误导信息；**Agent 幻觉可能触发错误行动**（错误下单、错误医疗建议）。缓解：**RAG grounding**、工具验证、关键操作多源确认、不确定时说「不知道」。

**【本项目】** system prompt 要求基于 **Retrieved knowledge** 回答；RAG 片段来自真实课件；检索为空时降级而非编造课件内容。

---

#### Q6. 如何防止 Prompt Injection？

**答：** 用户输入与 system prompt **隔离**；Function Calling 结构化输出；工具调用前校验；敏感操作不依赖用户文本拼接进 system。

**【本项目】** `userQuery` 仅用于 **RAG query** 和 user message，不覆盖 system 安全指令；服务端固定 system 模板 + 追加 RAG 块，而非让用户自定义 system。

---

### 10.5 评估 · 性能 · 项目综合（5 题）

#### Q1. 如何评估 Agent 任务完成率？

**答：** **任务成功率 = 成功任务数 / 总任务数**。需定义「成功」：目标达成、字段完整、无违规。

**【本项目】** 可量化指标（`benchmark-results.json`）：

| 指标 | 结果 |
|------|------|
| 20 轮流式成功率 | **100%** |
| 首 token（客户端） | 平均 **907ms**，P95 **1452ms** |
| Abort 中断 | **100%** |
| Chroma RAG 命中 | **20/20** |

口述：「我们写了 `benchmark:chat`，自动化跑 20 轮长对话，记录首 token 与 RAG 来源。」

---

#### Q2. Agent 推理延迟高的主要原因？你如何优化？

**答：** LLM 推理、工具/RAG 延迟、多轮循环、记忆检索、网络 I/O。

**优化：** 上下文压缩、Top-K 控制、流式输出改善**首 token 体验**、缓存、异步。

**【本项目】** 历史 **12 轮 + 约 14K 字符裁剪** 防超长失败；RAG Flask 超时 4s 后 keyword 降级；SSE 流式让用户 **907ms 首 token** 即可见输出，而非等全文。

---

#### Q3. 如何减少 Token 消耗？

**答：** 对话摘要、结构化记忆、工具结果只取必要字段、精简 system prompt、早停。

**【本项目】** **Top-4** 而非全库；历史裁剪；RAG 只 append 召回 chunk，不塞整本课件。

---

#### Q4. 请结合项目介绍：如何设计「教育课件答疑 Agent」？

**答（综合八股 + 简历）：**

| 组件 | 本项目实现 |
|------|-----------|
| 输入 | 学生提问 + `mode=course` |
| 知识 | Chroma 8 chunk，Flask 检索 API |
| 推理 | RAG 注入 + DeepSeek 流式生成 |
| 测评链路 | LangGraph 三节点 → `portrait_data` |
| 网关 | Next.js `/api/chat`，SSE，Abort |
| 降级 | 无 Key → 关键词脚本；RAG 失败 → keyword |
| 评估 | benchmark 20 轮，指标可复现 |

闭环：**测评 → 报告 → 画像答疑 → 课件伴学**，本地可部署。

---

#### Q5. 当前 LLM Agent 最大瓶颈？未来 3 年趋势？（简答）

**答：** **最大瓶颈：可靠性**——幻觉驱动行动、复杂任务易偏航、工具泛化差、评估标准不统一。

**趋势：** LLM + 规则/工作流（LangGraph）混合、RAG + 知识图谱、端侧轻量 Agent、多模态、Constitutional AI 与安全内建。

**【本项目】** 用 **固定 LangGraph + RAG** 换可靠性，而非全自动 ReAct 乱跑；符合当前工程化落地路径。

---

### 10.6 面试 30 秒 · AI 项目口述（背这段）

> 我做的是教育场景 AI Agent：**RAG** 把课件和 QA 存 Chroma，Flask 提供检索，课堂提问 Top-4 召回后注入 Prompt，解决胡编；**LangGraph** 把测评后的评分、报告、画像上下文串成三节点，complete 一次返回 portrait_data；**Next.js** 做 `/api/chat` 网关，SSE 流式、Key 放服务端，历史裁 12 轮；压测 20 轮流式成功率 100%，首 token 平均 907ms，RAG 20/20 命中。
