# 关键代码片段

## 1. 动画检测 (frame_html.py)

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
        logger.debug(f"Template {self.template_path} contains @keyframes animations")
        return True

    # Check for animation property (excludes 'animation-' in meta tags)
    # Look for 'animation:' property (not 'animation-')
    if re.search(r'\banimation\s*:', html_content):
        logger.debug(f"Template {self.template_path} contains animation properties")
        return True

    logger.debug(f"Template {self.template_path} has no animations")
    return False
```

---

## 2. 多帧生成 (frame_html.py)

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
    """
    # ... 参数处理 ...

    # Capture frames at evenly spaced intervals
    frame_interval = total_duration / frame_count

    for i in range(frame_count):
        # Calculate time point for this frame
        time_point = i * frame_interval

        # Wait until the animation reaches this time point
        if time_point > 0:
            await page.wait_for_timeout(int(time_point * 1000))

        # Capture frame
        frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
        await page.screenshot(path=frame_path, type='png', omit_background=True)
        frame_paths.append(frame_path)

        logger.debug(f"  Frame {i+1}/{frame_count} captured at {time_point:.2f}s: {frame_path}")

    return frame_paths
```

---

## 3. 帧合成视频 (video.py)

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
    """
    self._ensure_ffmpeg()

    if not frames:
        raise ValueError("Frames list cannot be empty")

    logger.info(f"Creating video from {len(frames)} frames (fps={fps})")

    # Get audio duration to match video duration
    audio_duration = _probe_media_duration(audio)
    logger.debug(f"Audio duration: {audio_duration:.3f}s")

    # Get the directory and pattern from first frame
    first_frame_dir = os.path.dirname(frames[0])
    frame_pattern = os.path.join(first_frame_dir, "frame_%04d.png")

    logger.debug(f"Using frame pattern: {frame_pattern}")

    # Input frames with specified framerate
    input_frames = ffmpeg.input(
        frame_pattern,
        framerate=fps,
        pattern_type='sequence'
    )
    input_audio = ffmpeg.input(audio)

    # Combine frames and audio
    (
        ffmpeg
        .output(
            input_frames,
            input_audio,
            output,
            t=audio_duration,  # Force video duration to match audio
            vcodec='libx264',
            acodec='aac',
            pix_fmt='yuv420p',
            audio_bitrate='192k',
            preset='medium',
            crf=23,
            **{'b:v': '2M'}
        )
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )

    logger.success(f"Video created from frames: {output} (duration: {audio_duration:.3f}s)")
    return output
```

---

## 4. Pipeline 集成 - 帧合成 (frame_processor.py)

```python
async def _compose_frame_html(
    self,
    frame: StoryboardFrame,
    storyboard: 'Storyboard',
    config: StoryboardConfig,
    output_path: str
) -> str:
    """
    Compose frame using HTML template

    Supports both static and animated templates:
    - Static templates: Generate single frame image
    - Animated templates: Generate multiple frames for animation
    """
    from pixelle_video.services.frame_html import HTMLFrameGenerator
    from pixelle_video.utils.template_util import resolve_template_path

    # Resolve template path
    template_path = resolve_template_path(config.frame_template)

    # Generate frame using HTML
    generator = HTMLFrameGenerator(template_path)

    # Use video_path for video media, image_path for images
    media_path = frame.video_path if frame.media_type == "video" else frame.image_path
    logger.debug(f"Generating frame with media: '{media_path}' (type: {frame.media_type})")

    # Check if template has animations
    has_animations = generator.has_animations()

    if has_animations:
        logger.info(f"  → Detected animated template, generating multiple frames")

        # Determine frame count and duration based on audio duration
        frame_count = 10  # Default frame count
        total_duration = 5.0  # Default duration

        # Use audio duration if available
        if frame.duration:
            total_duration = frame.duration
            # Adjust frame count based on duration (2 fps for smooth animation)
            frame_count = max(10, int(total_duration * 2))

        logger.debug(f"  → Generating {frame_count} frames over {total_duration:.2f}s")

        # Generate frames
        import os
        output_dir = os.path.join(os.path.dirname(output_path), f"animated_frames_{frame.index}")
        frame_paths = await generator.generate_animated_frames(
            title=storyboard.title,
            text=frame.narration,
            image=media_path,
            ext=ext,
            output_dir=output_dir,
            frame_count=frame_count,
            total_duration=total_duration
        )

        # Store frame paths in frame object for video generation
        frame.animated_frames = frame_paths
        logger.debug(f"  ✓ Generated {len(frame_paths)} animated frames in {output_dir}")

        # Return first frame path for compatibility
        return frame_paths[0]
    else:
        # Static template: generate single frame
        composed_path = await generator.generate_frame(
            title=storyboard.title,
            text=frame.narration,
            image=media_path,
            ext=ext,
            output_path=output_path
        )

        return composed_path
```

---

## 5. Pipeline 集成 - 视频生成 (frame_processor.py)

```python
async def _step_create_video_segment(
    self,
    frame: StoryboardFrame,
    config: StoryboardConfig
):
    """Step 4: Create video segment from media + audio"""
    logger.debug(f"  4/4: Creating video segment for frame {frame.index}...")

    # Generate output path using task_id
    from pixelle_video.utils.os_util import get_task_frame_path
    output_path = get_task_frame_path(config.task_id, frame.index, "segment")

    from pixelle_video.services.video import VideoService
    video_service = VideoService()

    # Check if we have animated frames
    has_animated_frames = hasattr(frame, 'animated_frames') and frame.animated_frames

    # Branch based on media type and animation
    if frame.media_type == "video":
        # Video workflow: overlay HTML template on video, then add audio
        logger.debug(f"  → Using video-based composition with HTML overlay")

        # Step 1: Overlay transparent HTML image on video
        temp_video_with_overlay = get_task_frame_path(config.task_id, frame.index, "video") + "_overlay.mp4"

        video_service.overlay_image_on_video(
            video=frame.video_path,
            overlay_image=frame.composed_image_path,
            output=temp_video_with_overlay,
            scale_mode="contain"
        )

        # Step 2: Add narration audio
        segment_path = video_service.merge_audio_video(
            video=temp_video_with_overlay,
            audio=frame.audio_path,
            output=output_path,
            replace_audio=True,
            audio_volume=1.0
        )

        # Clean up temp file
        import os
        if os.path.exists(temp_video_with_overlay):
            os.unlink(temp_video_with_overlay)

    elif has_animated_frames:
        # Animated template: Create video from multiple frames
        logger.debug(f"  → Using animated frames composition ({len(frame.animated_frames)} frames)")

        segment_path = video_service.create_video_from_frames(
            frames=frame.animated_frames,
            audio=frame.audio_path,
            output=output_path,
            fps=2  # 2 fps for smooth animation
        )

    elif frame.media_type == "image" or frame.media_type is None:
        # Image workflow: Use composed image directly
        logger.debug(f"  → Using image-based composition")

        segment_path = video_service.create_video_from_image(
            image=frame.composed_image_path,
            audio=frame.audio_path,
            output=output_path,
            fps=config.video_fps
        )

    else:
        raise ValueError(f"Unknown media type: {frame.media_type}")

    frame.video_segment_path = segment_path

    logger.debug(f"  ✓ Video segment created: {segment_path}")
```

---

## 6. 模型字段 (storyboard.py)

```python
@dataclass
class StoryboardFrame:
    """Single storyboard frame"""
    index: int                                 # Frame index (0-based)
    narration: str                             # Narration text
    image_prompt: str                          # Image generation prompt

    # Generated resource paths
    audio_path: Optional[str] = None           # Audio file path
    media_type: Optional[str] = None           # Media type: "image" or "video"
    image_path: Optional[str] = None           # Original image path
    video_path: Optional[str] = None           # Original video path
    composed_image_path: Optional[str] = None  # Composed image path
    animated_frames: Optional[List[str]] = None  # Animated frame paths (NEW!)
    video_segment_path: Optional[str] = None   # Final video segment path

    # Metadata
    duration: float = 0.0                      # Frame duration
    created_at: Optional[datetime] = None
```

---

## 7. 使用示例

### 独立使用
```python
from pixelle_video.services.frame_html import HTMLFrameGenerator
from pixelle_video.services.video import VideoService

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
    video_service = VideoService()
    video_path = video_service.create_video_from_frames(
        frames=frames,
        audio="narration.mp3",
        output="output.mp4",
        fps=2
    )
```

### 在 Pipeline 中自动使用
```python
# 系统自动检测动画并使用多帧渲染
result = await pixelle_video.generate_video(
    text="内容文本",
    frame_template="1080x1920/static_excerpt_animated.html"
)
```

---

## 8. FFmpeg 命令示例

### 帧合成视频
```bash
ffmpeg \
  -framerate 2 \
  -i frame_%04d.png \
  -i audio.mp3 \
  -t 5.0 \
  -c:v libx264 \
  -c:a aac \
  -pix_fmt yuv420p \
  -preset medium \
  -crf 23 \
  -b:v 2M \
  -y output.mp4
```

**参数说明：**
- `-framerate 2`: 帧率 2 fps
- `-i frame_%04d.png`: 输入帧序列（0000-9999）
- `-i audio.mp3`: 输入音频
- `-t 5.0`: 视频时长 5 秒
- `-c:v libx264`: H.264 视频编码
- `-c:a aac`: AAC 音频编码
- `-pix_fmt yuv420p`: 像素格式
- `-preset medium`: 编码预设
- `-crf 23`: 质量参数
- `-b:v 2M`: 视频比特率 2Mbps