# JLU Education AI Agent Platform

吉大未来学习 · AI 智能教育 Agent 平台（Monorepo）

**Agent 技术栈：** LangGraph · LangChain（RAG / LCEL）· Chroma · DeepSeek · SSE

## 结构

| 目录 | 说明 |
|------|------|
| `future_learning_demo/` | Next.js 15 课堂 Agent、SSE 流式、RAG 网关 |
| `learning_power/` | Flask + LangGraph 测评 + **LangChain RAG** |
| `scene-content-kit/` | 课件 Slide/Quiz 渲染组件 |
| `docs/` | 架构、RAG、简历说明 |

## 快速开始

### 1. 课堂 Agent（Next.js）

```bash
cd future_learning_demo
cp .env.example .env.local   # 配置 OPENAI_API_KEY
npm install
npm run rag:index            # LangChain 构建 Chroma 索引（需 Python 依赖）
npm run dev -- -p 3001
npm run benchmark:chat       # 流式压测（需 dev + Flask 5000 + .env.local）
npm run benchmark:rag        # RAG Top-4 命中率
```

### 2. 测评后端（Flask）

```bash
cd learning_power/backend
cp .env.example .env
pip install -r requirements.txt
python run.py
# Windows 推荐单实例：.\scripts\start_flask.ps1
```

Windows 若 `pip install -r requirements.txt` 因 `chroma-hnswlib` 编译失败，可先清代理后重装，或仅安装 Agent 相关包（`langchain*`、`chromadb`、`sentence-transformers`、`openai`）。Embedding 模型下载可设 `HF_ENDPOINT=https://hf-mirror.com`。

### 3. 测评前端（Vue，可选）

```bash
cd learning_power/frontend
npm install
npm run dev
```

## 文档

- [Agent 架构（面试用）](docs/ARCHITECTURE.md)
- [LangChain RAG](docs/RAG.md)
- [PBL 多 Agent](docs/PBL_AGENTS.md)
- [LangGraph 测评流水线](docs/LANGGRAPH_ASSESSMENT_PIPELINE.md)
- [Agent 压测说明](docs/AGENT_BENCHMARK.md)
- [简历定稿](docs/RESUME_AGENT_PROJECT.md)

## License

For learning and portfolio use.
