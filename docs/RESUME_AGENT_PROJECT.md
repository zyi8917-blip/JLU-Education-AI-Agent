# 吉大未来学习·AI 智能教育 Agent 平台（简历定稿）

**2025.12 – 2026.05**　　　　**吉大未来学习·AI 智能教育 Agent 平台**　　　　**Agent 应用开发（全栈）**

**项目简介：**  
面向《人工智能基础》课程与学习力测评，实现「测评 → 报告 → 画像答疑 → 课件伴学 → PBL 多 Agent」闭环。**LangGraph** 编排测评后处理，**LangChain** 构建 Chroma RAG（Retriever + LCEL 问答链），Next.js 提供 SSE 流式网关。压测 **20 轮流式成功率 100%**（`benchmark:chat`）；LangChain RAG 检索评测 **Top-4 命中率 77.8%**（`benchmark:rag`）；提供 **Tool Calling 课件检索 Agent** 与 **PBL 三阶段多 Agent** 叙事。

**技术栈：**

- **Agent 编排：** LangGraph（测评：评分 → 报告 → 画像上下文）  
- **LangChain：** HuggingFace Embeddings + Chroma VectorStore + Retriever；LCEL（RAG \| Prompt \| ChatOpenAI）  
- **知识增强：** Top-4 召回，课件/QA/Markdown 多源 chunk  
- **应用层：** Next.js 15、Flask、TypeScript  
- **模型与交互：** DeepSeek（OpenAI 兼容）、SSE 流式、Abort 中止  
- **工程化：** `benchmark:chat` 指标、脚本/真模型双模式  

**个人职责：**

- **LangChain RAG：** 将课件与 QA 转为 `Document`，经 **LangChain Chroma** 建索引；课堂 Agent 通过 Retriever **Top-4** 召回并注入 Prompt；提供 **`/api/v1/rag/qa` LCEL 链** 与 **`@tool` 课件检索 + Tool Calling Agent**（`/api/v1/agent/course`）；`npm run benchmark:rag` 输出检索命中率。  

- **LangGraph 测评编排：** 三节点 StateGraph（`evaluate_answers` → `generate_report` → `prepare_portrait`），一次返回 **`portrait_data`** 供画像 Agent 消费。  

- **SSE 流式网关：** Next.js `/api/chat` 统一调模型，**12 轮 + 14K** 历史裁剪，Key 仅存服务端；压测首 token **907ms / P95 1452ms**，20 轮成功率 **100%**。  

- **多 Agent 协作：** PBL 教练 / 设计 / 评估分阶段 Prompt + 流式对话；测评官、画像助手、课堂 Agent 分场景落地。  

---

## 压测数据出处（面试自备）

| 指标 | 值 |
|------|-----|
| 20 轮流式成功率 | 100% |
| 首 token（客户端） | 平均 907ms，P95 1452ms |
| Chroma RAG | 20/20 |

详见：`future_learning_demo/docs/benchmark-results.json`  
架构说明：`docs/ARCHITECTURE.md` · RAG：`docs/RAG.md`
