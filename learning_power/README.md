# 学生创造力测评系统

> 基于 AI 的学生创造力智能测评与分析系统

## 🎯 项目简介

这是一个使用 **Vue 3 + Flask** 前后端分离架构开发的学生创造力测评系统，集成了 AI 智能评分、数据分析和可视化展示功能。

### 主要功能

- ✅ **学生管理** - 学生档案的增删改查
- ✅ **智能测评** - AI 自动生成题目和评分
- ✅ **结果分析** - 多维度数据分析和可视化
- ✅ **学生画像** - 基于测评结果的智能画像分析
- ✅ **系统设置** - 灵活的参数配置

### 技术栈

**前端：**
- Vue 3 - 渐进式 JavaScript 框架
- Vite - 下一代前端构建工具
- Element Plus - Vue 3 组件库
- ECharts - 数据可视化图表库
- Pinia - Vue 状态管理
- Vue Router - 路由管理

**后端：**
- Flask - Python Web 框架
- SQLAlchemy - ORM 数据库工具
- LangGraph - AI 工作流编排
- LangChain - LLM 应用框架
- Flask-CORS - 跨域资源共享
- Flask-Migrate - 数据库迁移

**AI：**
- SiliconFlow API
- DeepSeek-V3 模型

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 为 .env 并修改）
cp .env.example .env

# 启动后端服务
python run.py
```

后端服务将在 `http://localhost:5000` 启动

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

### 3. 访问系统

打开浏览器访问：`http://localhost:3000`

---

## 📁 项目结构

```
learning_power/
├── backend/                 # Flask 后端
│   ├── app/                # 应用代码
│   │   ├── api/           # API 路由
│   │   │   ├── students.py      # 学生管理
│   │   │   ├── assessments.py   # 测评管理
│   │   │   ├── analysis.py      # 分析报告
│   │   │   ├── chat.py          # 智能对话
│   │   │   └── system.py        # 系统设置
│   │   ├── models/        # 数据模型
│   │   │   ├── student.py       # 学生模型
│   │   │   └── assessment.py    # 测评模型
│   │   ├── utils/         # 工具函数
│   │   ├── config.py      # 配置文件
│   │   └── __init__.py    # 应用初始化
│   ├── migrations/        # 数据库迁移
│   ├── instance/          # 数据库实例
│   ├── run.py             # 启动脚本
│   └── requirements.txt   # Python 依赖
├── frontend/               # Vue 前端
│   ├── src/               # 源代码
│   │   ├── views/        # 页面组件
│   │   │   ├── Home.vue         # 首页
│   │   │   ├── Students.vue     # 学生管理
│   │   │   ├── Assessment.vue   # 开始测评
│   │   │   ├── Analysis.vue     # 结果分析
│   │   │   ├── Persona.vue      # 学生画像
│   │   │   └── Settings.vue     # 系统设置
│   │   ├── components/   # 通用组件
│   │   ├── router/       # 路由配置
│   │   ├── api/          # API 调用
│   │   └── utils/        # 工具函数
│   ├── public/            # 静态资源
│   ├── index.html         # HTML 模板
│   ├── vite.config.js     # Vite 配置
│   └── package.json       # npm 配置
└── README.md              # 本文件
```

---

## 🔧 配置说明

### 后端配置 (.env)

```env
# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///./creativity_assessment.db

# AI配置
SILICONFLOW_API_KEY=your-api-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL_CHAT_A=deepseek-ai/DeepSeek-V3
SILICONFLOW_MODEL_CHAT_B=deepseek-ai/DeepSeek-V3

# 测评配置
MAX_QUESTIONS=10
TIME_LIMIT_MINUTES=30

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

### 前端配置 (vite.config.js)

前端通过 Vite 代理转发 API 请求到后端：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5000',
      changeOrigin: true
    }
  }
}
```

---

## 📡 API 接口

### 学生管理
- `GET /api/v1/students` - 获取学生列表
- `POST /api/v1/students` - 创建学生
- `PUT /api/v1/students/<student_id>` - 更新学生信息
- `DELETE /api/v1/students/<student_id>` - 删除学生

### 测评管理
- `POST /api/v1/assessments/session` - 创建测评会话
- `POST /api/v1/assessments/answer` - 提交答案
- `POST /api/v1/assessments/complete` - 完成测评
- `GET /api/v1/assessments/history/<student_id>` - 获取测评历史

### 分析报告
- `GET /api/v1/analysis/student/<student_id>` - 获取学生分析报告
- `GET /api/v1/analysis/portrait/<student_id>` - 获取学生画像

### 智能对话
- `POST /api/v1/chat/portrait` - 与学习力画像助手对话

### 系统设置
- `GET /api/v1/system/config` - 获取系统配置
- `PUT /api/v1/system/config` - 更新系统配置

---

## 🎨 功能特性

### 1. 学生管理
- 完整的学生档案管理（增删改查）
- 支持按姓名、学号搜索
- 分页展示学生列表

### 2. 智能测评
- AI 自动生成个性化题目
- 实时答题和进度跟踪
- 多维度智能评分

### 3. 结果分析
- 雷达图展示多维度能力
- 历史趋势分析
- 详细的评分反馈

### 4. 学生画像
- 基于测评结果的智能画像
- AI 助手对话功能
- 个性化学习建议

### 5. 系统设置
- 灵活的测评参数配置
- 题目数量和时间限制设置

---

## 🛠️ 开发指南

### 数据库迁移

```bash
cd backend

# 初始化迁移
flask db init

# 生成迁移脚本
flask db migrate -m "描述"

# 执行迁移
flask db upgrade
```

### 前端构建

```bash
cd frontend

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

---

## 📝 许可证

本项目仅供学习和研究使用。

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📧 联系方式

如有问题，请联系项目维护者。

