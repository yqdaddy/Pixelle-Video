# 测试建议

## 测试环境准备

### 1. 安装依赖
```bash
# 安装 Playwright
pip install playwright

# 安装浏览器
playwright install chromium
```

### 2. 检查 FFmpeg
```bash
# 确认 FFmpeg 已安装
ffmpeg -version

# macOS 安装
brew install ffmpeg

# Ubuntu/Debian 安装
sudo apt-get install ffmpeg
```

---

## 测试场景

### 场景 1: 动画检测

**测试目标：** 验证动画检测逻辑是否正确

**测试用例：**
```python
from pixelle_video.services.frame_html import HTMLFrameGenerator

# 测试动画模板
animated = HTMLFrameGenerator("templates/1080x1920/static_excerpt_animated.html")
assert animated.has_animations() == True, "动画模板应该被检测到"

# 测试静态模板
static = HTMLFrameGenerator("templates/1080x1920/image_default.html")
assert static.has_animations() == False, "静态模板不应被检测为动画"
```

**验证点：**
- ✅ 包含 `@keyframes` 的模板被识别为动画
- ✅ 包含 `animation:` 属性的模板被识别为动画
- ✅ 不包含动画的模板不被误判
- ✅ `animation-name` 等属性不触发误判

---

### 场景 2: 多帧生成

**测试目标：** 验证多帧渲染功能

**测试用例：**
```python
import asyncio
from pixelle_video.services.frame_html import HTMLFrameGenerator

async def test_multi_frame():
    generator = HTMLFrameGenerator("templates/1080x1920/static_excerpt_animated.html")

    frames = await generator.generate_animated_frames(
        title="测试标题",
        text="这是一段测试文本，用于验证动画渲染功能。",
        frame_count=5,
        total_duration=2.0
    )

    # 验证帧数量
    assert len(frames) == 5, "应该生成 5 帧"

    # 验证文件存在
    for frame in frames:
        assert os.path.exists(frame), f"帧文件应该存在: {frame}"

    # 验证文件命名
    for i, frame in enumerate(frames):
        expected_name = f"frame_{i:04d}.png"
        assert expected_name in frame, f"帧命名应该符合格式: {expected_name}"

asyncio.run(test_multi_frame())
```

**验证点：**
- ✅ 生成指定数量的帧
- ✅ 帧文件存在
- ✅ 帧命名符合 `frame_%04d.png` 格式
- ✅ 帧文件大小合理（非空文件）
- ✅ 时间间隔正确（日志中显示）

---

### 场景 3: 帧合成视频

**测试目标：** 验证从帧序列生成视频

**测试用例：**
```python
from pixelle_video.services.video import VideoService
import tempfile
import subprocess

def test_frame_to_video():
    # 生成测试音频
    audio_path = tempfile.mktemp(suffix=".mp3")
    subprocess.run([
        "ffmpeg",
        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=mono",
        "-t", "3",
        "-q:a", "9",
        "-acodec", "libmp3lame",
        "-y", audio_path
    ], check=True)

    # 使用前面测试生成的帧
    video_service = VideoService()
    output_path = tempfile.mktemp(suffix=".mp4")

    video_path = video_service.create_video_from_frames(
        frames=frames,  # 来自场景 2
        audio=audio_path,
        output=output_path,
        fps=2
    )

    # 验证视频存在
    assert os.path.exists(video_path), "视频文件应该存在"

    # 验证视频时长
    result = subprocess.run(
        ["ffmpeg", "-i", video_path],
        capture_output=True,
        text=True
    )
    # 检查 Duration 行

    # 清理
    os.unlink(audio_path)
    os.unlink(video_path)
```

**验证点：**
- ✅ 视频文件生成成功
- ✅ 视频时长匹配音频时长
- ✅ 视频可以播放
- ✅ 视频包含音频轨道
- ✅ 视频编码正确（H.264）

---

### 场景 4: 完整 Pipeline 测试

**测试目标：** 验证完整视频生成流程

**测试用例：**
```python
from pixelle_video import PixelleVideoCore

async def test_full_pipeline():
    # 初始化核心
    pixelle_video = PixelleVideoCore()

    # 使用动画模板生成视频
    result = await pixelle_video.generate_video(
        text="这是一段测试文本，用于验证完整的动画视频生成流程。",
        frame_template="1080x1920/static_excerpt_animated.html",
        n_storyboard=1,
        tts_speed=1.2
    )

    # 验证结果
    assert os.path.exists(result.video_path), "最终视频应该存在"
    assert result.duration > 0, "视频时长应该大于 0"

    # 检查 storyboard
    frame = result.storyboard.frames[0]
    assert hasattr(frame, 'animated_frames'), "Frame 应该有 animated_frames 属性"
    assert frame.animated_frames is not None, "应该生成动画帧"
    assert len(frame.animated_frames) > 0, "应该有多帧"

    print(f"✅ 视频生成成功: {result.video_path}")
    print(f"   时长: {result.duration:.2f}s")
    print(f"   帧数: {len(frame.animated_frames)}")

asyncio.run(test_full_pipeline())
```

**验证点：**
- ✅ 完整流程无报错
- ✅ 最终视频生成成功
- ✅ 动画效果可见（视觉检查）
- ✅ 音频与视频同步
- ✅ 资源正确清理

---

### 场景 5: 性能测试

**测试目标：** 验证性能表现

**测试用例：**
```python
import time

async def test_performance():
    generator = HTMLFrameGenerator("templates/1080x1920/static_excerpt_animated.html")

    # 测试不同帧数
    for frame_count in [5, 10, 20]:
        start_time = time.time()

        frames = await generator.generate_animated_frames(
            title="性能测试",
            text="测试文本",
            frame_count=frame_count,
            total_duration=5.0
        )

        elapsed = time.time() - start_time
        fps = frame_count / elapsed

        print(f"帧数: {frame_count}, 耗时: {elapsed:.2f}s, 速度: {fps:.2f} fps")

        # 性能基线：至少 0.5 fps
        assert fps > 0.5, f"渲染速度过慢: {fps:.2f} fps"

asyncio.run(test_performance())
```

**验证点：**
- ✅ 渲染速度合理（> 0.5 fps）
- ✅ 浏览器实例复用正常
- ✅ 内存使用稳定
- ✅ 无内存泄漏

---

## 测试命令

### 1. 快速验证
```bash
# 运行验证脚本
python3 verify_implementation.py
```

### 2. 完整测试
```bash
# 安装 Playwright 浏览器
playwright install chromium

# 运行完整测试
python3 test_animated_simple.py
```

### 3. 单元测试
```bash
# 运行单元测试
pytest tests/test_animated_frames.py -v
```

---

## 可视化验证

### 方法 1: 生成测试视频
```python
import asyncio
from pixelle_video.services.frame_html import HTMLFrameGenerator
from pixelle_video.services.video import VideoService

async def create_test_video():
    # 生成帧
    generator = HTMLFrameGenerator("templates/1080x1920/static_excerpt_animated.html")
    frames = await generator.generate_animated_frames(
        title="动画测试",
        text="这是一段动画测试文本",
        frame_count=10,
        total_duration=5.0
    )

    # 生成静音音频
    import subprocess
    subprocess.run([
        "ffmpeg", "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=mono",
        "-t", "5", "-y", "test_audio.mp3"
    ])

    # 合成视频
    video_service = VideoService()
    video_path = video_service.create_video_from_frames(
        frames=frames,
        audio="test_audio.mp3",
        output="test_animated.mp4",
        fps=2
    )

    print(f"视频已生成: {video_path}")
    print("请用视频播放器打开查看动画效果")

asyncio.run(create_test_video())
```

### 方法 2: 查看单帧
```python
# 生成单帧并打开查看
import asyncio
from pixelle_video.services.frame_html import HTMLFrameGenerator

async def preview_frame():
    generator = HTMLFrameGenerator("templates/1080x1920/static_excerpt_animated.html")

    # 生成多帧
    frames = await generator.generate_animated_frames(
        title="预览",
        text="测试文本",
        frame_count=5,
        total_duration=2.0
    )

    # 打开第一帧和最后一帧对比
    import subprocess
    subprocess.run(["open", frames[0]])  # macOS
    subprocess.run(["open", frames[-1]])  # macOS

asyncio.run(preview_frame())
```

---

## 预期结果

### 动画模板
- **static_excerpt_animated.html**: 文字逐行淡入，署名缓慢出现
- **image_simple_black_animated.html**: 黑色背景上的动画效果
- **image_film_animated.html**: 胶片风格的动画

### 性能指标
- 帧生成速度：> 0.5 fps
- 视频合成速度：< 5 秒（10 帧 + 5 秒音频）
- 内存占用：< 500 MB

### 视频质量
- 分辨率：1080x1920（竖屏）
- 编码：H.264
- 帧率：2 fps（动画帧）
- 音频：AAC 192kbps

---

## 常见问题排查

### 问题 1: Playwright 浏览器未安装
```
错误: Executable doesn't exist at /path/to/chromium
解决: playwright install chromium
```

### 问题 2: FFmpeg 未找到
```
错误: FFmpeg not found
解决: brew install ffmpeg (macOS)
```

### 问题 3: 帧渲染速度慢
```
原因: 浏览器启动耗时
优化: 已实现浏览器实例复用
验证: 检查日志 "Initialized Playwright Chromium browser" 只出现一次
```

### 问题 4: 视频时长不匹配
```
原因: 音频时长与帧序列时长不一致
检查: 查看日志中的 "Audio duration" 和 "Target output duration"
解决: 使用 -t 参数强制匹配音频时长
```

---

## 测试清单

### 功能测试
- [ ] 动画检测正常工作
- [ ] 多帧生成成功
- [ ] 帧命名规范正确
- [ ] 帧合成视频成功
- [ ] 视频时长匹配音频
- [ ] 动画效果可见

### 性能测试
- [ ] 渲染速度 > 0.5 fps
- [ ] 浏览器实例复用
- [ ] 内存使用稳定
- [ ] 无内存泄漏

### 兼容性测试
- [ ] 静态模板继续工作
- [ ] 向后兼容性良好
- [ ] 无破坏性变更

### 边界测试
- [ ] 空输入处理
- [ ] 无效模板处理
- [ ] 长时长动画（> 30 秒）
- [ ] 多帧数量（> 50 帧）

---

## 测试报告模板

```markdown
# 测试报告

## 测试环境
- Python 版本:
- Playwright 版本:
- FFmpeg 版本:
- 操作系统:

## 测试结果

### 功能测试
- 动画检测: ✅ / ❌
- 多帧生成: ✅ / ❌
- 视频合成: ✅ / ❌

### 性能测试
- 渲染速度: X fps
- 内存占用: X MB

### 发现的问题
1. 问题 1
2. 问题 2

### 截图/视频
（附上测试生成的视频截图）
```