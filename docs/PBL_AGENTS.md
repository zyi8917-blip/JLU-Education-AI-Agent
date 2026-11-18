# PBL 多 Agent 协作

## 三阶段 Agent

| 阶段 | Agent | 用户轮次 | 职责 |
|------|--------|----------|------|
| coach | 课程教练 Agent | 第 1～2 轮 | 澄清服务对象与课堂场景 |
| design | 方案设计 Agent | 第 3～4 轮 | 功能模块与使用流程 |
| review | 评估反馈 Agent | 第 5 轮起 | 完整性检查、风险与优化 |

实现：`future_learning_demo/src/lib/chat/project-prompts.ts`（`resolveProjectPhase` + `buildProjectSystemPrompt`）

UI：`project-chat.tsx` 展示当前 Agent 名称与里程碑列表。

## 后端元数据 API

`POST /api/v1/agent/pbl`  
Body: `{ "phase": "coach" }`  
返回阶段说明与 pipeline，便于面试演示「多 Agent 编排」。

## Tool 增强（可选）

课堂事实类问题可走 `POST /api/v1/agent/course`（LangChain `@tool` + `search_course_materials`）。
