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
```

结果写入 `future_learning_demo/docs/benchmark-results.json`，运行时指标追加到 `future_learning_demo/.metrics/chat-metrics.jsonl`。

## 指标口径

| 指标 | 含义 |
|------|------|
| `firstTokenMs` | 上游 SSE 首包到达时间 |
| `abortRate` | 用户/客户端中断请求占比 |
| `rounds20.successRate` | 20 轮历史裁剪后仍成功完成流式请求的比例 |
| `ragChromaRate` | 使用 Chroma 命中（相对关键词回退）占比 |

## 最近一次实测（2026-05-21）

| 指标 | 值 |
|------|-----|
| 20 轮流式成功率 | **100%** |
| 首 token（客户端） | 平均 **907ms**，P95 **1452ms** |
| Abort 中断 | **100%** 成功 |
| Chroma RAG | **100%**（20/20） |

完整 JSON：`future_learning_demo/docs/benchmark-results.json`  
简历定稿：`docs/RESUME_AGENT_PROJECT.md`
