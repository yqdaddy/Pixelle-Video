# 表单数据持久化功能

## 功能说明

用户填写的表单数据会自动保存到本地文件，下次刷新或重新打开页面后会自动恢复。

## 实现方式

使用 Streamlit 的 `st.session_state` 结合本地 JSON 文件存储：

- **存储位置**: `temp/form_data.json`（已在 .gitignore 中）
- **自动保存**: 每次用户修改表单时自动保存
- **自动恢复**: 页面加载时自动从文件加载

## 持久化的字段

### 内容输入 (content_input.py)
- `batch_mode` - 批处理模式开关
- `processing_mode` - 处理模式（生成/固定）
- `input_text` - 主要文本内容
- `input_title` - 标题
- `n_scenes` - 分镜数量
- `split_mode` - 分割模式
- `batch_topics_text` - 批处理主题列表
- `batch_title_prefix` - 标题前缀
- `batch_n_scenes` - 批处理分镜数

### BGM 设置
- `bgm_choice` - 背景音乐选择
- `bgm_volume` - 音量设置

### 样式配置 (style_config.py)
- `tts_inference_mode` - TTS 模式（local/macos/comfyui）
- `tts_local_voice` - 本地 TTS 声音
- `tts_local_speed` - 本地 TTS 语速
- `tts_macos_voice` - macOS TTS 声音
- `template_type_selector` - 模板类型
- `selected_template` - 选中的模板
- `last_template_type` - 上次选择的模板类型
- `standard_image_workflow_source` - 图像工作流来源
- `standard_image_workflow_source_select` - 图像工作流选择
- `standard_video_workflow_source` - 视频工作流来源
- `standard_video_workflow_source_select` - 视频工作流选择
- `prompt_prefix` - 提示词前缀

## 核心工具

### web/utils/form_persistence.py

提供以下核心函数：

```python
# 保存表单数据
save_form_data(data: Dict[str, Any]) -> None

# 加载表单数据
load_form_data() -> Dict[str, Any]

# 获取持久化的值（优先级：session_state > 文件 > 默认值）
get_persisted_value(key: str, default: Optional[Any] = None) -> Any

# 更新单个值并保存
update_form_value(key: str, value: Any) -> None

# 清空所有数据
clear_form_data() -> None
```

## 使用示例

### 在组件中添加持久化

```python
from web.utils.form_persistence import get_persisted_value, update_form_value

# 1. 获取持久化的值
text = st.text_area(
    "输入文本",
    value=get_persisted_value("input_text", ""),
    key="input_text"
)

# 2. 保存到持久化
update_form_value("input_text", text)
```

### 优先级机制

1. **session_state 最高优先级** - 当前会话中的值
2. **持久化文件次之** - 上次保存的值
3. **默认值最后** - 如果都不存在

## 注意事项

1. **敏感信息不保存** - API Key 等敏感信息不应持久化（settings.py 未修改）
2. **自动清理** - 数据保存在 temp/ 目录，不会提交到 Git
3. **JSON 格式** - 支持中文字符，使用 UTF-8 编码
4. **原子写入** - 使用临时文件 + 重命名，防止数据损坏

## 修改的文件

1. `web/utils/form_persistence.py` - 新建，持久化工具模块
2. `web/components/content_input.py` - 添加内容输入持久化
3. `web/components/style_config.py` - 添加样式配置持久化

## 测试验证

运行以下命令验证功能：

```bash
# 检查语法
uv run python -m py_compile web/utils/form_persistence.py web/components/content_input.py web/components/style_config.py

# 启动应用测试
uv run streamlit run web/app.py
```

测试流程：
1. 填写表单数据
2. 刷新页面
3. 验证数据是否自动恢复