# macOS 系统 TTS

## 概述

macOS 系统 TTS 使用 macOS 自带的 `say` 命令进行语音合成。这是一个完全离线、无需网络连接的 TTS 解决方案，特别适合 Intel Mac 用户。

## 特点

- **完全离线**：无需网络连接，数据完全在本地处理
- **无需额外依赖**：使用 macOS 系统自带功能
- **多语言支持**：支持中文（普通话、粤语、台湾国语）、英文、日文、韩文等多种语言
- **零成本**：无需购买 API 或下载模型

## 使用方法

### 1. 配置文件设置

在 `config.yaml` 中设置：

```yaml
comfyui:
  tts:
    inference_mode: macos
    macos:
      voice: Ting-Ting  # 普通话女声
      speed: 1.0  # 语速（say 命令不支持语速调整，此参数保留用于 API 兼容）
```

### 2. 可用声音

#### 中文

| 声音名称 | 语言 | 说明 |
|---------|------|------|
| Ting-Ting | zh_CN | 普通话女声 |
| Sin-ji | zh_HK | 粤语女声 |
| Mei-Jia | zh_TW | 台湾国语女声 |

#### 英文

| 声音名称 | 语言 | 说明 |
|---------|------|------|
| Alex | en_US | 美式英语男声 |
| Samantha | en_US | 美式英语女声 |
| Victoria | en_US | 美式英语女声 |
| Daniel | en_GB | 英式英语男声 |

#### 其他语言

| 声音名称 | 语言 | 说明 |
|---------|------|------|
| Kyoko | ja_JP | 日语女声 |
| Yuna | ko_KR | 韩语女声 |

### 3. 命令行使用

```bash
# 列出所有可用声音
say -v '?'

# 中文普通话
say -v "Ting-Ting" "你好，这是一个测试。"

# 粤语
say -v "Sin-ji" "你好"

# 输出到文件
say -v "Ting-Ting" -o output.aiff "你好"

# 转换为 MP3（需要 ffmpeg）
ffmpeg -i output.aiff output.mp3
```

## 代码示例

```python
from pixelle_video.services.tts_macos import MacOSTTSClient

# 初始化客户端
client = MacOSTTSClient()

# 同步调用
audio_path = client.synthesize(
    text="你好，世界！",
    voice="Ting-Ting",
    output_path="output/hello.mp3"
)

# 异步调用
import asyncio
audio_path = await client.synthesize_async(
    text="Hello, world!",
    voice="Samantha",
    output_path="output/hello_en.mp3"
)

# 列出可用声音
voices = MacOSTTSClient.list_voices()
for voice in voices:
    print(f"{voice['name']}: {voice['description']}")
```

## 注意事项

1. **仅支持 macOS**：此功能仅在 macOS 系统上可用。在其他操作系统上会抛出 `RuntimeError`。

2. **需要 ffmpeg**：输出格式转换需要 ffmpeg。如果输出 MP3 等格式，请确保已安装 ffmpeg：
   ```bash
   brew install ffmpeg
   ```

3. **语速不支持调整**：macOS 的 `say` 命令不直接支持语速调整。`speed` 参数保留用于 API 兼容，但实际不会生效。

4. **音质**：macOS 系统 TTS 的音质可能不如专业的云端 TTS 服务（如 Edge TTS），但优点是完全离线且免费。

5. **声音可用性**：不同版本的 macOS 可能包含不同的声音。使用 `say -v '?'` 命令查看您的系统上实际可用的声音列表。

## 替代方案

如果 macOS TTS 不满足需求，可以考虑以下替代方案：

1. **Edge TTS**（推荐）
   - `inference_mode: local`
   - 音质更好，支持更多声音
   - 需要网络连接（中国地区可能受限）

2. **ComfyUI TTS**
   - `inference_mode: comfyui`
   - 支持声音克隆
   - 需要配置 ComfyUI 工作流

## 故障排除

### 声音不可用

如果提示某个声音不可用，请先检查系统是否安装了该声音：

```bash
# 列出所有声音
say -v '?'

# 测试特定声音
say -v "Ting-Ting" "测试"
```

### ffmpeg 未安装

如果提示 ffmpeg 未找到：

```bash
# 使用 Homebrew 安装
brew install ffmpeg
```

### 权限问题

如果遇到权限问题，请确保您的应用有权限访问麦克风（虽然 macOS TTS 不需要麦克风，但某些系统版本可能需要相关权限）。

## 版本要求

- macOS 10.9 或更高版本
- Python 3.11+
- ffmpeg（用于音频格式转换）