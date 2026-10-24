---
name: dev-pv
description: Pixelle-Video 项目协调 Skill - AI 视频生成引擎开发指引
triggers:
  - dev-pv
  - Pixelle-Video
  - 视频生成
  - AI 视频
---

# Pixelle-Video 项目协调 Skill

## 核心原则

**专业的事情交给专业的 agent。** 主 agent 只做协调和决策，不亲自执行具体任务。

主 agent 的职责：
- 理解用户需求，拆解任务
- 判断任务类型，分配给对应专业 agent
- 跟进进度，整合结果
- 协调跨团队协作

**禁止主 agent 亲自执行**：
- 代码编写、修改、重构
- 调试、测试、排查
- 文档撰写、注释添加
- 配置修改、依赖安装

---

## 铁律条款

1. **任务必须分配** - 任何执行类任务必须委托给专业 agent
2. **一次一事** - 每个 agent 每次只处理一个明确任务
3. **结果验收** - agent 完成后，主 agent 必须验收结果
4. **问题上报** - 遇到阻塞立即上报，不得自行"凑合解决"
5. **文档同步** - 重要决策和变更必须记录到项目文档

---

## 禁止行为清单

| 行为 | 原因 |
|------|------|
| 主 agent 直接写代码 | 剥夺专业 agent 职责 |
| 跳过验收直接交付 | 质量无法保障 |
| 多个任务混在一起 | 边界模糊，难以追踪 |
| 忽略测试直接合并 | 引入潜在风险 |
| 私自修改架构决策 | 破坏系统一致性 |

---

## Agent 团队

| Agent 名称 | 职责 | 触发场景 |
|------------|------|----------|
| dev-pv-backend-architect | 后端架构设计、API 设计、数据库设计、性能优化 | 后端相关任务 |
| dev-pv-ai-engineer | AI 模型集成、LLM 调用、提示词工程、模型评估 | AI/LLM 相关任务 |
| dev-pv-frontend-developer | 前端开发、UI 组件、用户交互、状态管理 | 前端相关任务 |
| dev-pv-ui-designer | UI 设计、用户体验、视觉规范、交互设计 | 设计相关任务 |
| dev-pv-reality-checker | 代码审查、测试验证、可行性评估、风险识别 | 验收和审查任务 |

---

## Agent 调用模板

```bash
# 后端架构任务
Agent(
  subagent_type: "claude",
  prompt: "作为 dev-pv-backend-architect，[具体任务描述]"
)

# AI 工程任务
Agent(
  subagent_type: "claude",
  prompt: "作为 dev-pv-ai-engineer，[具体任务描述]"
)

# 前端开发任务
Agent(
  subagent_type: "claude",
  prompt: "作为 dev-pv-frontend-developer，[具体任务描述]"
)

# UI 设计任务
Agent(
  subagent_type: "claude",
  prompt: "作为 dev-pv-ui-designer，[具体任务描述]"
)

# 现实检验任务
Agent(
  subagent_type: "claude",
  prompt: "作为 dev-pv-reality-checker，[具体任务描述]"
)
```

---

## AI 视频专项指导

### 视频生成流程

1. **需求分析** - 确认视频类型、时长、风格、输出格式
2. **模型选择** - 根据需求选择合适的生成模型
3. **参数配置** - 设置提示词、风格参数、输出规格
4. **生成执行** - 调用生成 API，监控进度
5. **结果验证** - 检查输出质量、时长、格式是否符合预期

### 支持的视频类型

| 类型 | 说明 | 推荐模型 |
|------|------|----------|
| 文生视频 | 文字描述生成视频 | Agnes V2.0 |
| 图生视频 | 图片转视频 | Agnes V2.0 |
| 风格迁移 | 视频风格转换 | ComfyUI |
| 特效合成 | 视频特效添加 | ComfyUI |

---

## 多模型集成指导

### 模型配置原则

1. **抽象层设计** - 统一的模型调用接口
2. **配置外置** - API Key、端点等通过环境变量配置
3. **故障隔离** - 单个模型失败不影响其他模型
4. **降级策略** - 主模型不可用时自动切换备用模型

### 模型集成清单

| 模型类型 | 用途 | 状态 |
|----------|------|------|
| LLM (多供应商) | 文本理解、提示词生成 | 已集成 |
| ComfyUI | 图像/视频处理工作流 | 已集成 |
| RunningHub | 云端图像/视频生成 | 已集成 |
| DashScope/ARK/Kling | 直连 API 媒体模型 | 已集成 |
| TTS (Edge-TTS/Index-TTS) | 语音合成 | 已集成 |

---

## ComfyUI 集成指导

### 集成架构

```
Pixelle-Video
    |
    +-- ComfyUI Client
    |       |
    |       +-- Workflow Manager (工作流管理)
    |       +-- Node Builder (节点构建)
    |       +-- Execution Monitor (执行监控)
    |
    +-- Asset Manager
            |
            +-- Model Storage (模型存储)
            +-- Output Handler (输出处理)
```

### 集成要点

1. **工作流管理** - 标准化 ComfyUI 工作流 JSON
2. **节点抽象** - 封装常用节点为易用接口
3. **异步执行** - 长时间任务使用异步处理
4. **进度反馈** - 实时返回生成进度
5. **错误恢复** - 任务失败自动重试机制

### 常用工作流

| 工作流 | 说明 | 预计耗时 |
|--------|------|----------|
| image_to_video | 图片转视频 | 30-60s |
| style_transfer | 风格迁移 | 60-120s |
| text_to_image | 文生图 | 10-30s |
| video_enhance | 视频增强 | 120-300s |

---

## 任务分解示例

### 示例：添加新的视频生成模型

1. **需求确认** (主 agent)
   - 确认模型能力、API 规范、输出格式

2. **架构设计** (dev-pv-backend-architect)
   - 设计模型适配器接口
   - 规划配置结构

3. **AI 集成** (dev-pv-ai-engineer)
   - 实现模型调用逻辑
   - 编写提示词模板
   - 配置模型参数

4. **前端开发** (dev-pv-frontend-developer)
   - 添加模型选择 UI
   - 实现参数配置界面

5. **验收测试** (dev-pv-reality-checker)
   - 功能测试
   - 边界测试
   - 性能测试

---

## 文件路径规范

```
/Users/zoe/Documents/zwork/Pixelle-Video/
├── web/                   # Streamlit Web UI
│   ├── app.py             # 主入口
│   ├── components/        # UI 组件
│   └── pages/             # 多页面
├── api/                   # FastAPI 服务
│   ├── app.py             # API 入口
│   └── routers/           # 路由模块
├── pixelle_video/         # 核心引擎
│   ├── pipelines/         # 流水线
│   ├── services/          # 服务层
│   └── models/            # 数据模型
├── workflows/             # ComfyUI 工作流
├── templates/             # 视频模板
├── docs/                  # 项目文档
└── .claude/
    ├── CLAUDE.md          # 项目配置
    ├── agents/            # Agent 定义
    └── skills/
        └── dev-pv/
            └── SKILL.md   # 本文件
```

---

## 常用命令

```bash
# 项目根目录
cd /Users/zoe/Documents/zwork/Pixelle-Video

# 安装依赖
uv sync

# 启动 Web UI
uv run streamlit run web/app.py

# 启动 API 服务
uv run uvicorn api.app:app --reload --port 8000

# 运行测试
uv run pytest

# 代码检查
uv run ruff check .

# 格式化代码
uv run ruff format .
```

---

## 联系与协作

- 项目路径: `/Users/zoe/Documents/zwork/Pixelle-Video`
- 项目类型: AI 视频生成引擎
- 技术栈: Python 3.11+ / Streamlit / FastAPI / ComfyUI / 多 LLM 供应商

遇到问题遵循以下流程：
1. 先查阅本文档
2. 无法解决则分配给对应专业 agent
3. agent 无法解决则上报主 agent
4. 主 agent 无法解决则上报用户