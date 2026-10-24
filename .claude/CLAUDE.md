# Pixelle-Video 项目配置

> AI 全自动短视频引擎 —— 一句话生成完整视频

## 项目简介

Pixelle-Video 是一个 AI 驱动的视频生成平台，只需输入主题即可自动完成：
- 文案撰写 (LLM)
- AI 配图/视频生成 (ComfyUI / API)
- 语音合成 (TTS)
- 视频合成与输出

**核心特性**：
- 多模型支持：通义千问、GPT、DeepSeek、Ollama
- 灵活工作流：ComfyUI 本地 / RunningHub 云端 / 直连 API
- 视频尺寸：竖屏(1080x1920)、横屏(1920x1080)、方形(1080x1080)
- 扩展模块：数字人口播、图生视频、动作迁移

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Streamlit | Web UI (`web/app.py`) |
| 后端 | FastAPI | API 服务 (`api/app.py`) |
| 核心引擎 | Python 3.11+ | `pixelle_video/` |
| 工作流引擎 | ComfyUI / ComfyKit | 图像/视频/TTS 工作流 |
| LLM | OpenAI SDK 兼容 | 多模型统一接口 |
| TTS | Edge-TTS / Index-TTS | 多音色/声音克隆 |
| 视频合成 | ffmpeg + moviepy | 视频处理 |
| 视频模板 | Jinja2 HTML | `templates/` |

## 目录结构

```
Pixelle-Video/
├── web/                    # Streamlit Web UI
│   ├── app.py              # 主入口
│   ├── components/         # UI 组件
│   ├── pages/              # 多页面
│   └── pipelines/          # 前端流水线
├── api/                    # FastAPI 服务
│   ├── app.py              # API 入口
│   ├── routers/            # 路由模块
│   └── schemas/            # 数据模型
├── pixelle_video/          # 核心引擎
│   ├── config/             # 配置管理
│   ├── models/             # 数据模型
│   ├── pipelines/          # 后端流水线
│   ├── services/           # 服务层
│   └── utils/              # 工具函数
├── workflows/              # ComfyUI 工作流
│   ├── runninghub/         # 云端工作流
│   └── selfhost/           # 本地工作流
├── templates/              # 视频模板
│   ├── 1080x1920/          # 竖屏模板
│   ├── 1920x1080/          # 横屏模板
│   └── 1080x1080/          # 方形模板
└── bgm/                    # 背景音乐
```

---

## Agent 团队

### 协调入口

| 触发方式 | 说明 |
|----------|------|
| `/dev-pv` | 统一入口，根据任务类型自动分派 |

**详细协调规则见**: `.claude/skills/dev-pv/SKILL.md`

### 专职 Agent

| Agent | 触发方式 | 职责 |
|-------|----------|------|
| **后端架构师** | `/dev-pv-backend-architect` | FastAPI 服务设计、数据模型、流水线架构、API 设计 |
| **AI 工程师** | `/dev-pv-ai-engineer` | LLM 集成、ComfyUI 工作流、TTS 服务、模型 API 对接 |
| **前端开发者** | `/dev-pv-frontend-developer` | Streamlit UI 组件、页面交互、状态管理 |
| **UI 设计师** | `/dev-pv-ui-designer` | 视频模板设计、样式优化、视觉风格 |
| **现实检验者** | `/dev-pv-reality-checker` | 代码审查、性能分析、边界测试、可行性评估 |

---

## 使用指南

### 启动服务

```bash
# Web UI (推荐)
uv run streamlit run web/app.py

# API 服务
uv run uvicorn api.app:app --reload --port 8000

# Docker
docker-compose up -d
```

### 配置文件

复制配置模板并填写 API Key：

```bash
cp config.example.yaml config.yaml
```

**关键配置项**：
- `llm.api_key` - LLM API 密钥
- `api_providers.*` - 图像/视频模型直连配置
- `comfyui.comfyui_url` - 本地 ComfyUI 地址
- `comfyui.runninghub_api_key` - 云端 RunningHub 密钥

### 开发流程

1. **新功能开发**：`/dev-pv` 描述需求，自动分派
2. **Bug 修复**：提供错误信息和复现步骤
3. **架构变更**：`/dev-pv-backend-architect` 方案设计
4. **UI 优化**：`/dev-pv-ui-designer` 视觉调整
5. **代码审查**：`/dev-pv-reality-checker` 质量检验

---

## 特殊配置指引

### ComfyUI 工作流

工作流放置在 `workflows/` 目录：

| 目录 | 说明 |
|------|------|
| `selfhost/` | 本地 ComfyUI 工作流 |
| `runninghub/` | 云端 RunningHub 工作流 |

**工作流命名规范**：
- `tts_*.json` - TTS 语音合成
- `image_*.json` - 图像生成
- `video_*.json` - 视频生成

### 视频模板

模板放置在 `templates/` 目录，按尺寸分组：

**命名规范**：
- `static_*.html` - 静态模板（无 AI 媒体）
- `image_*.html` - 图片模板
- `video_*.html` - 视频模板

### API 媒体模型

支持直连以下供应商：
- **OpenAI** - GPT 图像生成
- **DashScope** - 通义万象图像/视频
- **ARK** - 字节 Seedream/Seedance
- **Kling** - 可灵视频生成

配置示例见 `config.example.yaml` 的 `api_providers` 部分。

### 常用命令

```bash
# 运行测试
uv run pytest

# 代码检查
uv run ruff check .

# 格式化
uv run ruff format .

# 依赖更新
uv lock --upgrade
```

---

## 相关文档

- [用户文档](https://aidc-ai.github.io/Pixelle-Video/zh)
- [FAQ](docs/FAQ_CN.md)
- [视频教程](https://www.bilibili.com/video/BV1WzyGBnEVp/)