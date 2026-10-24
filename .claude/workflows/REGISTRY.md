# Pixelle-Video Workflow Registry

项目路径: `/Users/zoe/Documents/zwork/Pixelle-Video`
项目前缀: `pv`
Agent 前缀: `dev-pv`

## 已实例化的工作流

| 工作流 | 文件 | 用途 |
|--------|------|------|
| 功能开发 | `feature-implementation.yaml` | 新功能开发流程 |
| Bug 修复 | `bug-fix.yaml` | Bug 修复流程 |
| 代码审查 | `code-review.yaml` | 代码审查流程 |

## 使用方式

```bash
# 运行工作流
/workflow-runner .claude/workflows/feature-implementation.yaml

# 或指定任务
/workflow-runner .claude/workflows/bug-fix.yaml --task "修复登录按钮无响应"
```

## 创建时间

2026-10-23

## 模板来源

`~/.claude/workflow-templates/`