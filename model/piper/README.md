# Piper TTS 集成说明

## 概述

Piper TTS 是一个离线语音合成引擎，已集成到 Pixelle-Video 作为默认 TTS 服务。

## 配置

### 1. 安装依赖

```bash
# 安装 piper-tts
uv pip install piper-tts

# macOS 12.0 x86_64 用户需要安装兼容版本的 onnxruntime
uv pip install "onnxruntime<1.17"
```

### 2. 下载模型

中文模型推荐：`zh_CN-huayan-medium.onnx`

```bash
# 模型下载地址
# https://huggingface.co/rhasspy/piper-voices
```

当前模型路径：`model/piper/zh_CN-huayan-medium.onnx`

### 3. 配置文件

在 `config.yaml` 中配置：

```yaml
comfyui:
  tts:
    # 设置 Piper 为默认 TTS
    inference_mode: piper
    
    # Piper 配置
    piper:
      model_path: model/piper/zh_CN-huayan-medium.onnx
```

## 使用方法

### Python API

```python
from pixelle_video.services.tts_service import TTSService

# 创建服务
config = {
    "inference_mode": "piper",
    "piper": {
        "model_path": "model/piper/zh_CN-huayan-medium.onnx"
    }
}
service = TTSService(config=config, core=None)

# 生成语音
audio_path = await service(
    text="你好，世界！",
    output_path="output/hello.mp3"
)
```

### 直接使用客户端

```python
from pixelle_video.services.tts_piper import get_piper_tts_client

# 创建客户端
client = get_piper_tts_client(
    model_path="model/piper/zh_CN-huayan-medium.onnx"
)

# 生成语音
audio_path = await client.synthesize_async(
    text="这是测试语音",
    output_path="output/test.mp3"
)
```

## 已知问题

### 1. onnxruntime 兼容性

**问题**：onnxruntime 1.31.0 不支持 macOS 12.0 x86_64

**解决方案**：安装兼容版本

```bash
uv pip install "onnxruntime<1.17"
```

**受影响版本**：
- onnxruntime >= 1.17.0 仅支持 macOS 14.0+

### 2. ffmpeg 依赖

**问题**：音频转换需要 ffmpeg

**解决方案**：安装 ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

## 测试

运行测试脚本验证集成：

```bash
uv run python model/piper/test_piper.py
```

## 可用模型

### 中文
- `zh_CN-huayan-medium.onnx` - 普通话女声（花音）

### 英文
- `en_US-lessac-medium.onnx` - 美式英语女声
- `en_US-ryan-medium.onnx` - 美式英语男声

### 其他语言
更多模型请访问：https://huggingface.co/rhasspy/piper-voices

## 输出格式

- Piper 原生输出：WAV 格式
- 自动转换为：MP3 格式（通过 ffmpeg）
- 音质设置：高质量（libmp3lame, quality=2）

## 性能特点

- ✅ 完全离线，无需网络
- ✅ 中文支持良好
- ✅ 生成速度快
- ⚠️ 需要 ffmpeg 进行格式转换
- ⚠️ 音色选择有限（每模型固定音色）

## 与其他 TTS 对比

| 特性 | Piper | Edge TTS | macOS TTS |
|------|-------|----------|-----------|
| 离线 | ✅ | ❌ | ✅ |
| 网络依赖 | ❌ | ✅ | ❌ |
| 中文音色 | 1 | 多个 | 3 |
| 音质 | 中 | 高 | 高 |
| 速度 | 快 | 中 | 快 |
| 跨平台 | ✅ | ✅ | ❌ (仅 macOS) |

## 更新日志

### 2026-10-24
- ✅ 创建 Piper TTS 客户端 (`tts_piper.py`)
- ✅ 集成到 TTS 服务 (`tts_service.py`)
- ✅ 更新配置文件（设为默认）
- ✅ 添加 `piper-tts` 依赖
- ⚠️ 发现 onnxruntime 兼容性问题（macOS 12.0）