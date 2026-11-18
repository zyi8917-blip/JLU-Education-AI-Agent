# Agent 架构（简历 / 面试用）

## 技术栈一览

**LangGraph** · **LangChain**（RAG / LCEL / ChatOpenAI）· **Chroma** · **DeepSeek API** · **SSE** · Next.js · Flask

## 三条链路

### 1. 测评 — LangGraph

```
答题完成 → quick-complete → LangGraph StateGraph
  evaluate_answers → generate_report → prepare_portrait → portrait_data
```

代码：`learning_power/backend/app/agents/assessment_workflow.py`  
评测节点默认 **`lc_batch_evaluate.py`**（`ChatPromptTemplate` + `ChatOpenAI` + JSON 解析），`USE_LC_EVAL=false` 时回退 OpenAI SDK。

### 2. 课堂 — LangChain RAG + Next 流式网关

```
用户提问 → Next /api/chat → Flask GET /rag/course (LangChain Retriever)
         → 片段注入 system prompt → DeepSeek SSE 流式返回
```

代码：`app/rag/lc_course_rag.py`，`future_learning_demo/app/api/chat/route.ts`

可选：`POST /api/v1/rag/qa` 完整 LCEL 链（Flask 内完成生成）

**Tool Agent：** `@tool search_course_materials` → `POST /api/v1/agent/course`（LangChain Tool Calling）

**RAG 评测：** `npm run benchmark:rag` → `docs/rag-eval-results.json`

### 3. 画像 / PBL — Prompt + LLM

- 画像：`POST /api/v1/chat/portrait`（消费 portrait_data；默认 **`lc_portrait_chat.py`** LangChain 消息链）
- PBL：Next `/api/chat` mode=project，多 Agent 分阶段 Prompt（见 `docs/PBL_AGENTS.md`），PBL 模式同样注入 RAG

## 指标

见 `future_learning_demo/docs/benchmark-results.json`（流式成功率、首 token、RAG 来源）
