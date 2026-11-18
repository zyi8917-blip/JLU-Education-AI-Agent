# LangChain RAG

## 栈

| 组件 | 实现 |
|------|------|
| 文档 | `course_rag.load_chunks()` → LangChain `Document` + metadata |
| Embedding | `HuggingFaceEmbeddings`（默认 `sentence-transformers/all-MiniLM-L6-v2`） |
| 向量库 | LangChain `Chroma`（路径 `future_learning_demo/.chroma`） |
| 检索 | `vectorstore.as_retriever(k=4)` |
| 问答链 | LCEL：`Retriever → ChatPromptTemplate → ChatOpenAI → StrOutputParser` |

## 环境变量

```env
USE_LC_RAG=true          # 默认 true；false 时回退原生 chromadb 客户端
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 构建索引

```bash
cd future_learning_demo && npm run rag:index
# 或
cd learning_power/backend && python scripts/build_course_rag.py
```

若 HuggingFace 超时，可先设置镜像（PowerShell）：

```powershell
$env:HF_ENDPOINT='https://hf-mirror.com'
python scripts/build_course_rag.py
```

当前索引：**21 chunks**（QA + Markdown + Slide + `course_slides_kb.json`）。

## API

- `GET /api/v1/rag/course?query=...&top_k=4` — Next.js 课堂 Agent 使用（Retriever）
- `POST /api/v1/rag/qa` — LangChain LCEL 一站式 RAG 问答（Body: `{"question":"..."}`）
- `POST /api/v1/agent/course` — Tool Calling Agent（`search_course_materials` @tool）

## 评测

```bash
cd future_learning_demo && npm run benchmark:rag
```

结果：`future_learning_demo/docs/rag-eval-results.json`

## 与 LangGraph 分工

- **LangGraph**：测评后处理（评分 → 报告 → portrait_data）
- **LangChain**：课件 RAG 与检索增强问答
