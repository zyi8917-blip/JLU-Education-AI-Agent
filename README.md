# JLU Education AI Agent Platform

吉大未来学习 · AI 智能教育 Agent 平台（Monorepo）

## 结构

| 目录 | 说明 |
|------|------|
| `future_learning_demo/` | Next.js 15 课堂 Agent、SSE 流式、Chroma RAG |
| `learning_power/` | Flask + Vue 学习力测评、LangGraph 测评编排 |
| `scene-content-kit/` | 课件 Slide/Quiz 渲染组件 |
| `docs/` | 项目文档与简历说明 |

## 快速开始

### 1. 课堂 Agent（Next.js）

```bash
cd future_learning_demo
cp .env.example .env.local   # 配置 OPENAI_API_KEY
npm install
npm run rag:index            # 需 Python chromadb
npm run dev
```

### 2. 测评后端（Flask）

```bash
cd learning_power/backend
cp .env.example .env
pip install -r requirements.txt
python run.py
```

### 3. 测评前端（Vue）

```bash
cd learning_power/frontend
npm install
npm run dev
```

## 文档

- [LangGraph 测评流水线](docs/LANGGRAPH_ASSESSMENT_PIPELINE.md)
- [Agent 压测说明](docs/AGENT_BENCHMARK.md)

## License

For learning and portfolio use.
