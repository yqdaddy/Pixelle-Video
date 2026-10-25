# 多帧动画渲染功能实现文档

## 概述

成功实现了视频模板的多帧动画渲染功能，使 CSS 动画模板能够生成动态视频。

## 修改的文件

### 1. `pixelle_video/services/frame_html.py`

**新增方法：**

#### `has_animations() -> bool`
检测模板是否包含 CSS 动画。

```python
def has_animations(self) -> bool:
    """
    Check if template contains CSS animations

    Detects animation-related CSS:
    - @keyframes rules
    - animation properties

    Returns:
        True if template contains animations, False otherwise
    """
    html_content = self.template.lower()

    # Check for @keyframes rules
    if '@keyframes' in html_content:
        return True

    # Check for animation property
    if re.search(r'\banimation\s*:', html_content):
        return True

    return False
```

#### `generate_animated_frames() -> list[str]`
生成多帧动画序列。

```python
async def generate_animated_frames(
    self,
    title: str,
    text: str,
    image: str,
    ext: Optional[Dict[str, Any]] = None,
    output_dir: Optional[str] = None,
    frame_count: int = 10,
    total_duration: float = 5.0
) -> list[str]:
    """
    Generate multiple frames from animated HTML template

    Renders frames at evenly spaced time intervals to capture animation effects.

    Args:
        frame_count: Number of frames to generate (default: 10)
        total_duration: Total animation duration in seconds (default: 5.0)

    Returns:
        List of paths to generated frame images
    """
```

**关键实现：**

- 使用 Playwright 的 `page.wait_for_timeout()` 控制动画时间
- 在时间点 t=0, 0.5s, 1s, ... 截取帧
- 帧均匀分布在总时长内
- 支持自定义帧数和时长

### 2. `pixelle_video/services/video.py`

**新增方法：**

#### `create_video_from_frames() -> str`
从多帧图像序列创建视频。

```python
def create_video_from_frames(
    self,
    frames: List[str],
    audio: str,
    output: str,
    fps: int = 2,
) -> str:
    """
    Create video from multiple frames with audio

    Args:
        frames: List of frame image paths (must be ordered)
        audio: Audio file path
        output: Output video path
        fps: Frames per second for the frames (default: 2 fps)

    Returns:
        Path to the output video
    """
```

**FFmpeg 命令：**

```bash
ffmpeg -framerate 2 -i frame_%04d.png -i audio.mp3 -t <duration> \
  -c:v libx264 -c:a aac -pix_fmt yuv420p output.mp4
```

### 3. `pixelle_video/models/storyboard.py`

**新增字段：**

```python
@dataclass
class StoryboardFrame:
    # ... existing fields ...
    animated_frames: Optional[List[str]] = None  # Animated frame paths
```

### 4. `pixelle_video/services/frame_processor.py`

**修改的方法：**

#### `_compose_frame_html()`
- 检测模板是否有动画
- 如果是动画模板，调用 `generate_animated_frames()`
- 自动根据音频时长调整帧数
- 存储帧路径到 `frame.animated_frames`

```python
async def _compose_frame_html(...):
    generator = HTMLFrameGenerator(template_path)
    has_animations = generator.has_animations()

    if has_animations:
        logger.info(f"  → Detected animated template, generating multiple frames")

        # Use audio duration if available
        if frame.duration:
            total_duration = frame.duration
            frame_count = max(10, int(total_duration * 2))  # 2 fps

        frame_paths = await generator.generate_animated_frames(...)
        frame.animated_frames = frame_paths
        return frame_paths[0]
    else:
        # Static template: generate single frame
        composed_path = await generator.generate_frame(...)
        return composed_path
```

#### `_step_create_video_segment()`
- 检查是否有动画帧
- 选择合适的视频合成方式

```python
async def _step_create_video_segment(...):
    has_animated_frames = hasattr(frame, 'animated_frames') and frame.animated_frames

    if has_animated_frames:
        # Animated template: Create video from multiple frames
        segment_path = video_service.create_video_from_frames(
            frames=frame.animated_frames,
            audio=frame.audio_path,
            output=output_path,
            fps=2
        )
    elif frame.media_type == "image":
        # Static image workflow
        ...
```

## 工作流程

### 静态模板流程
```
HTML Template → Single Frame → Video (image + audio)
```

### 动画模板流程
```
HTML Template → Animation Detection → Multiple Frames → Video (frames + audio)
                       ↓
                  has_animations() = True
                       ↓
              generate_animated_frames()
                       ↓
              [frame_0.png, frame_1.png, ..., frame_n.png]
                       ↓
              create_video_from_frames()
```

## 性能优化

### 1. 浏览器实例复用
使用类级别的 `_browser` 实例，避免重复启动浏览器。

```python
class HTMLFrameGenerator:
    _browser = None
    _playwright = None

    @classmethod
    async def _ensure_browser(cls):
        if cls._browser and cls._browser.is_connected():
            return cls._browser
        # ... create new browser ...
```

### 2. 自动帧数调整
根据音频时长自动计算最优帧数：

```python
if frame.duration:
    frame_count = max(10, int(total_duration * 2))  # 2 fps for smooth animation
```

### 3. 错误处理
- 动画超时回退单帧渲染（待实现）
- 浏览器连接失败自动重试

## 测试验证

### Test 1: 动画检测
```python
# Animated template
generator = HTMLFrameGenerator("static_excerpt_animated.html")
assert generator.has_animations() == True

# Static template
generator = HTMLFrameGenerator("image_default.html")
assert generator.has_animations() == False
```

### Test 2: 多帧渲染
```python
frames = await generator.generate_animated_frames(
    title="测试标题",
    text="测试文本",
    frame_count=5,
    total_duration=2.0
)
# Output: 5 frames at t=0s, 0.4s, 0.8s, 1.2s, 1.6s
```

### Test 3: 帧合成视频
```bash
ffmpeg -framerate 2 -i frame_%04d.png -i audio.mp3 -t 3 \
  -c:v libx264 -c:a aac -pix_fmt yuv420p output.mp4
```

## 使用示例

### 1. 基本使用
```python
from pixelle_video.services.frame_html import HTMLFrameGenerator

# Load animated template
generator = HTMLFrameGenerator("templates/1080x1920/static_excerpt_animated.html")

# Check if animated
if generator.has_animations():
    # Generate multiple frames
    frames = await generator.generate_animated_frames(
        title="视频标题",
        text="视频内容文本",
        frame_count=10,
        total_duration=5.0
    )

    # Create video
    from pixelle_video.services.video import VideoService
    video_service = VideoService()
    video_path = video_service.create_video_from_frames(
        frames=frames,
        audio="narration.mp3",
        output="output.mp4",
        fps=2
    )
```

### 2. 在 Pipeline 中使用
```python
# 自动检测和处理
result = await pixelle_video.generate_video(
    text="内容文本",
    frame_template="1080x1920/static_excerpt_animated.html",
    # 系统会自动检测动画并使用多帧渲染
)
```

## 支持的动画模板

当前支持以下动画模板：

1. **static_excerpt_animated.html** - 文字逐行出现 + 署名淡入
2. **image_simple_black_animated.html** - 黑色背景动画
3. **image_film_animated.html** - 胶片风格动画
4. **image_elegant_animated.html** - 优雅动画效果

## 技术要点

### 1. 动画检测准确性
- 检测 `@keyframes` 规则
- 检测 `animation:` 属性（排除 `animation-` 前缀）
- 使用正则表达式 `\banimation\s*:` 确保精确匹配

### 2. 帧时间控制
- 使用 `page.wait_for_timeout(ms)` 精确控制时间点
- 帧均匀分布：`time_point = i * (total_duration / frame_count)`

### 3. 帧命名规范
- 使用 `%04d` 格式：`frame_0000.png`, `frame_0001.png`, ...
- 支持 FFmpeg 的序列模式匹配

## 后续优化方向

1. **性能优化**
   - 并行渲染多个帧
   - 使用 GPU 加速渲染
   - 缓存动画中间状态

2. **功能扩展**
   - 支持自定义动画时长配置
   - 支持动画循环模式
   - 支持动画暂停和恢复

3. **错误处理**
   - 动画超时回退单帧
   - 帧渲染失败重试
   - 资源清理机制

## 相关文档

- [HTML 模板开发指南](../docs/template-development.md)
- [CSS 动画最佳实践](../docs/css-animations.md)
- [FFmpeg 视频处理文档](../docs/video-processing.md)