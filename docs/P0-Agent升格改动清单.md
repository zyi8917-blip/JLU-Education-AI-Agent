# P0：Agent 升格改动清单（第 1～4 项）

本文档面向 **Agent 开发岗** 面试可演示目标，对仓库内 **`future_learning_demo/`**（Next.js 15 App Router）给出 **可落地的文件级改动清单**。实施时以 `future_learning_demo` 为工作根目录。

**仓库路径：** `FutureLearning/future_learning_demo`

---

## 目标范围（P0-1～P0-4）

| 编号 | 目标 | 验收标准（自测） |
|------|------|------------------|
| P0-1 | 服务端统一调模型，Key 仅服务端可见 | 浏览器 Network 请求体/前端 bundle 中无 API Key；仅调用同源 `/api/...` |
| P0-2 | 流式输出 + 可中止 | 助手回复逐字出现；切换页面或点「停止」后不再追加内容 |
| P0-3 | 固定消息协议 + 上下文裁剪 | 请求 JSON 结构稳定；超长历史不会撑爆单次请求（有截断或摘要策略） |
| P0-4 | 至少一条业务链路走真模型 | 建议首选 **课堂问答**（`CourseQaPanel`）；保留「演示模式」开关可选 |

---

## 目录约定

以下路径均相对于 **`future_learning_demo/`**。

---

## P0-1：服务端模型网关（环境变量 + Route Handler）

### 新增文件

| 文件路径 | 职责 |
|----------|------|
| `.env.local` | 本地密钥（**勿提交 Git**）。包含 `OPENAI_API_KEY` 或 `DASHSCOPE_API_KEY` 等，以及可选 `OPENAI_BASE_URL`、`AGENT_MODEL` |
| `.env.example` | 提交仓库的占位说明，无真实密钥，列出变量名与示例 |
| `app/api/chat/route.ts` | **POST** 入口：读 body → 调 OpenAI 兼容 `chat.completions`（或当前选用的 SDK）→ 返回流（见 P0-2） |
| `src/lib/llm/env.ts` | 读取 `process.env` 中的模型名、base URL、timeout；缺失时抛明确错误或返回 503 |
| `src/lib/llm/openai-stream.ts`（或 `stream-completion.ts`） | 封装 `fetch` 到 `${BASE_URL}/chat/completions`，`stream: true`，解析 SSE 行，转为 `ReadableStream<Uint8Array>` 供 Route 透传 |

### 修改文件

| 文件路径 | 改动要点 |
|----------|----------|
| `.gitignore` | 确保包含 `.env.local`、`.env*.local` |
| `package.json` | 若不用原生 `fetch` 解析流，可添加 `openai` 官方 SDK（服务端仅用）；版本与 Next 15 兼容即可 |
| `next.config.ts` | 若部署环境需 `serverActions` / 外部图片域名等，按需配置；一般 **无需** 把 Key 写进 `env` 的 `NEXT_PUBLIC_*` |

### 删除 / 避免

- 任何 `NEXT_PUBLIC_*` 形式的模型 Key。
- 在前端组件中直接 `fetch('https://api.openai.com/...')` 且带 Key。

---

## P0-2：流式响应 + AbortController

### 修改 / 新增（服务端）

| 文件路径 | 改动要点 |
|----------|----------|
| `app/api/chat/route.ts` | 返回 `new Response(readableStream, { headers: { Content-Type: text/event-stream; charset=utf-8, Cache-Control: no-cache, Connection: keep-alive } })`；从 `request.signal` 转发中止到上游 `AbortController` |
| `src/lib/llm/openai-stream.ts` | 上游 `fetch(..., { signal })`；reader 循环中检测 `abort` 并 `cancel()` |

### 修改文件（客户端）

| 文件路径 | 改动要点 |
|----------|----------|
| `src/components/course-qa-panel.tsx` | 用 `fetch('/api/chat', { method: 'POST', body: JSON.stringify(...), signal })`；`ReadableStream` + `TextDecoder` 增量更新最后一条 assistant 消息；组件 `useEffect` cleanup 里 `abort()` |
| `src/components/chat-panel.tsx`（可选） | 若需在 UI 上显示「生成中 / 停止」，可增加可选 props：`isStreaming`、`onStop`，**非必须** |

### 新增（可选但推荐）

| 文件路径 | 职责 |
|----------|------|
| `src/lib/chat/stream-client.ts` | 封装「POST + 读 SSE/NDJSON + onDelta 回调」，供 `course-qa-panel` 与后续 `project-chat` 复用 |

---

## P0-3：消息协议与上下文裁剪

### 新增文件

| 文件路径 | 职责 |
|----------|------|
| `src/lib/chat/types.ts` | `export type ChatRole = 'system' | 'user' | 'assistant'`；`export type ApiChatMessage = { role: ChatRole; content: string }`；请求体类型 `ChatRequestBody`（如 `messages`, `mode: 'course' | 'project'`, `slideContext?: string`） |
| `src/lib/chat/build-messages.ts` | 输入：前端 `ChatMessage[]` + 当前课件摘要/页码 + system 模板字符串 → 输出：`ApiChatMessage[]`；内联实现 **裁剪**：例如只保留最近 **N** 轮 user/assistant，或总字符上限 **M**，超长则丢弃中间轮或仅保留 system + 最近 1 轮 |
| `src/lib/chat/system-prompts.ts` | `courseAgentSystem`、`projectCoachSystem` 等常量，便于版本管理与面试讲解 |

### 修改文件

| 文件路径 | 改动要点 |
|----------|----------|
| `app/api/chat/route.ts` | `await request.json()` 后用 zod 或手写校验 `ChatRequestBody`；非法结构返回 **400** + JSON 错误信息（勿流式错误体混用，建议错误用 JSON） |
| `src/components/course-qa-panel.tsx` | 发送前组装 `messages`：含历史 `ChatMessage` 转 `ApiChatMessage`（agent→assistant，user→user）；首条或合并进一条 **system**（课程规则、引用课件要求） |

### 验收建议

- 人工制造 20 轮对话，确认请求仍成功且延迟可控。
- 文档中写明采用的 **N / M** 数值，面试可直说「当前是启发式裁剪，后续可换摘要模型」。

---

## P0-4：课堂链路接入真模型（替换脚本优先）

### 修改文件（核心）

| 文件路径 | 改动要点 |
|----------|----------|
| `src/components/course-qa-panel.tsx` | **保留** `courseQaData` 的推荐问题 UI；发送逻辑改为：若 `process.env.NEXT_PUBLIC_USE_LLM === 'true'` 或运行时开关（localStorage 开关 + 默认 true/false 自行约定）走 `/api/chat`，否则走现有 `matchAnswer` 脚本逻辑（便于答辩现场降级） |
| `src/data/demo-data.ts`（或新建 `src/data/course-context.ts`） | 从 `slideDeck`（`src/data/slides.ts`）导出 **当前课全局摘要** 或「当前页标题 + 要点」拼接函数，供 `course-qa-panel` 传入 `build-messages` 作为 `slideContext` |

### 修改文件（数据源）

| 文件路径 | 改动要点 |
|----------|----------|
| `src/components/course-slide-viewer.tsx` | 通过 **React Context** 或 **状态提升**（改 `app/(demo)/course/page.tsx` 为 client 包裹层，或新建 `course-session-provider.tsx`）把 **`currentSlideIndex` / 当前页 `title`+`data` 摘要** 下发给 `CourseQaPanel`，使每轮提问附带「当前页上下文」 |

### 修改文件（页面组合）

| 文件路径 | 改动要点 |
|----------|----------|
| `app/(demo)/course/page.tsx` | 若采用状态提升：改为 client 组件或内层 `<CourseLayout>`，统一持有 `slideIndex`，子组件 `CourseSlideViewer` + `CourseQaPanel` 共享 |

### 暂缓（第二期再接真模型）

| 文件路径 | 说明 |
|----------|------|
| `src/components/project-chat.tsx` | P0 验收只需 **一条** 链路；项目教练可复用同一 `/api/chat` + `mode: 'project'` + 不同 `system-prompts.ts` |

---

## 依赖与配置小结

| 项 | 说明 |
|----|------|
| `package.json` | 按需增加 `openai` 或继续使用 `fetch` + 手动解析 SSE |
| `.env.local` | `AGENT_MODEL=gpt-4o-mini`（示例）、`OPENAI_API_KEY=...`、`OPENAI_BASE_URL=`（可选，兼容国内代理） |
| 文档 | 本文件 + 建议在 `future_learning_demo/README.md` 增加一节「Agent 模式启动说明」 |

---

## 建议开发顺序（减少返工）

1. 新增 `types.ts` + `build-messages.ts` + `system-prompts.ts`（无网络，纯单测可写）。
2. 实现 `app/api/chat/route.ts` + `openai-stream.ts`，用 `curl` 或 Thunder Client 验证流式。
3. 改 `course-qa-panel.tsx` + 课件上下文上报（`course/page` 或 Context）。
4. 加 `.env.example`、错误处理与可选「脚本降级」开关。

---

## 版本信息

- 文档针对：`FutureLearning/future_learning_demo`（Next **15.3.1**、React **19**）。
- 若升级 Next 大版本，请核对 App Router 的 `Route Handler` 流式与 `fetch` 缓存行为是否变化。