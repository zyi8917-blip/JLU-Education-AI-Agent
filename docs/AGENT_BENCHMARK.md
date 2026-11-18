# Agent 链路压测说明

## 前置

```bash
cd future_learning_demo
npm install
cp .env.example .env.local   # 配置 OPENAI_API_KEY
pip install chromadb         # 在 learning_power/backend
npm run rag:index            # 调用 Python 构建 .chroma（无则走关键词 RAG）
# 课堂 RAG 检索需 Flask: cd learning_power/backend && python run.py
npm run dev                  # 另开终端
npm run benchmark:chat
npm run benchmark:rag           # RAG Top-4 召回评测 → docs/rag-eval-results.json
```

结果写入 `future_learning_demo/docs/benchmark-results.json`，运行时指标追加到 `future_learning_demo/.metrics/chat-metrics.jsonl`。

## 指标口径

| 指标 | 含义 |
|------|------|
| `firstTokenMs` | 上游 SSE 首包到达时间 |
| `abortRate` | 用户/客户端中断请求占比 |
| `rounds20.successRate` | 20 轮历史裁剪后仍成功完成流式请求的比例 |
| `ragChromaRate` | 使用 Chroma 命中（相对关键词回退）占比 |

## 最近一次实测（2026-10-01，本机复跑）

| 指标 | 值 |
|------|-----|
| 20 轮流式成功率 | **100%** |
| 首 token（客户端） | 平均 **197ms**，P95 **358ms** |
| Abort 中断 | **100%** 成功 |
| Chroma RAG（X-RAG-Source） | **6/20**（其余为关键词回退；需 Flask 5000 稳定在线） |

历史参考（2026-05-21）：首 token 平均 907ms / P95 1452ms，Chroma 20/20。

## RAG 检索评测（2026-10-01）

| 指标 | 值 |
|------|-----|
| QA 条数 | 9 |
| Top-4 答案片段命中 | **7/9（77.8%）** |
| 后端 | LangChain |

见 `future_learning_demo/docs/rag-eval-results.json`。

完整 JSON：`future_learning_demo/docs/benchmark-results.json`  
简历定稿：`docs/RESUME_AGENT_PROJECT.md`
