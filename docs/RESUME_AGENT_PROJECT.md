# 吉大未来学习·AI 智能教育 Agent 平台（简历定稿）

**2025.12 – 2026.05**　　　　**吉大未来学习·AI 智能教育 Agent 平台**　　　　**Agent 应用开发（全栈）**

**项目简介：**  
面向 **《人工智能基础》** 课程学习与 **学习力测评** 场景，针对课堂答疑与课件内容脱节、测评结束后画像对话缺少统一上下文、模型密钥不宜放在前端等痛点，实现「测评 → 报告 → 画像答疑 → 课件伴学」可本地部署的 Agent 应用闭环。通过 LangGraph 串联测评后处理、Chroma 检索课件与 QA 知识、Next.js 服务端流式网关，在本地压测下 **20 轮长对话流式成功率 100%**，首 token **平均 907ms（P95 1452ms）**，向量检索 **20/20 轮命中**。

**技术栈：**

- **Agent 编排：** LangGraph（线性三节点：批量评测 → 报告组装 → 画像上下文）  
- **知识增强：** Chroma 向量库 + Flask 检索 API（8 条知识片段）  
- **应用层：** Next.js 15、Flask、Vue 3、TypeScript  
- **模型与交互：** DeepSeek API（OpenAI 兼容）、SSE 流式输出、AbortController 中止生成  
- **工程化：** 统一消息协议与历史裁剪、脚本/真模型双模式、`benchmark:chat` 指标记录  

**个人职责：**

- **构建 RAG 知识增强链路：** 针对仅依赖当前页 `slideContext` 拼接、回答易偏离课件的问题，将课件 JSON、课堂 QA、Markdown 讲义切分后写入 **Chroma**，由 **Flask** 提供检索接口；课堂 Agent 按学生提问 **Top-4** 召回并注入 Prompt。本地压测 **20/20** 轮请求均走向量检索，知识库共 **8** 条 chunk，回答与课件一致性明显提升。  

- **LangGraph 测评后处理编排：** 针对测评完成后「评分、报告字段、画像对话上下文」分散在接口逻辑中、不便维护的问题，使用 **LangGraph** 搭建线性三节点工作流（`evaluate_answers` → `generate_report` → `prepare_portrait`），测评 `complete` 一次返回 **`portrait_data`**，画像 Agent 可直接消费，无需前端二次拼装。  

- **服务端流式网关与安全：** 针对 API Key 不能暴露前端、长回答等待体验差、多轮对话易超长失败等问题，在 **Next.js Route Handler** 封装 `/api/chat` 统一调模型，采用 **SSE 流式** 输出，并按 **最近 12 轮 + 约 14K 字符** 裁剪历史；支持用户 **Abort** 停止生成。压测首 token **平均 907ms、P95 1452ms**，**20 轮**流式成功率 **100%**，中断后不再追加内容。  

- **全栈 Demo 与可演示稳定性：** 针对答辩或弱网环境可能无 API Key 的情况，**Vue + Flask** 负责测评与画像对话，**Next.js** 负责沉浸式课堂；无 Key 时降级为 **关键词脚本问答**，有 Key 时切换真模型，并编写 **`benchmark:chat`** 将指标写入 `benchmark-results.json`，保证主流程可反复演示、结果可复现。  

---

## 压测数据出处（面试自备）

| 指标 | 值 |
|------|-----|
| 20 轮流式成功率 | 100% |
| 首 token（客户端） | 平均 907ms，P95 1452ms |
| Abort 中断 | 100% |
| Chroma RAG | 20/20 |

详见：`future_learning_demo/docs/benchmark-results.json`（2026-05-21）
