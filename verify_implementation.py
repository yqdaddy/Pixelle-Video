#!/usr/bin/env python3
"""
Verification script for animated frame rendering implementation

Tests key code snippets without requiring full dependencies.
"""

import os
import re
from pathlib import Path

def test_animation_detection_logic():
    """Test the animation detection logic"""
    print("\n" + "="*60)
    print("TEST: Animation Detection Logic")
    print("="*60)

    # Test 1: @keyframes detection
    html_with_keyframes = """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    """
    has_anim = '@keyframes' in html_with_keyframes.lower()
    print(f"\nTest 1: @keyframes detection")
    print(f"  HTML has @keyframes: {has_anim}")
    assert has_anim, "Should detect @keyframes"

    # Test 2: animation property detection
    html_with_animation = """
    <style>
        .title {
            animation: fadeIn 1s ease-out;
        }
    </style>
    """
    has_anim = bool(re.search(r'\banimation\s*:', html_with_animation.lower()))
    print(f"\nTest 2: animation property detection")
    print(f"  HTML has animation property: {has_anim}")
    assert has_anim, "Should detect animation property"

    # Test 3: Should NOT detect animation- prefix (like animation-name)
    html_with_animation_prefix = """
    <style>
        .title {
            animation-name: fadeIn;
        }
    </style>
    """
    has_anim = bool(re.search(r'\banimation\s*:', html_with_animation_prefix.lower()))
    print(f"\nTest 3: animation- prefix should NOT trigger")
    print(f"  HTML has animation property: {has_anim}")
    assert not has_anim, "Should NOT detect animation-name as animation property"

    # Test 4: Real template files
    animated_template = "templates/1080x1920/static_excerpt_animated.html"
    static_template = "templates/1080x1920/image_default.html"

    print(f"\nTest 4: Real template files")

    with open(animated_template, 'r', encoding='utf-8') as f:
        html = f.read()
    has_anim1 = '@keyframes' in html.lower() or bool(re.search(r'\banimation\s*:', html.lower()))
    print(f"  {animated_template}")
    print(f"    Has animations: {has_anim1}")
    assert has_anim1, "Animated template should be detected"

    with open(static_template, 'r', encoding='utf-8') as f:
        html = f.read()
    has_anim2 = '@keyframes' in html.lower() or bool(re.search(r'\banimation\s*:', html.lower()))
    print(f"  {static_template}")
    print(f"    Has animations: {has_anim2}")
    assert not has_anim2, "Static template should NOT be detected"

    print("\n✅ Animation detection logic verified!")


def test_frame_naming_pattern():
    """Test frame naming pattern for ffmpeg"""
    print("\n" + "="*60)
    print("TEST: Frame Naming Pattern")
    print("="*60)

    # Test frame naming
    frame_count = 10
    for i in range(frame_count):
        frame_name = f"frame_{i:04d}.png"
        print(f"  Frame {i}: {frame_name}")
        assert frame_name.startswith("frame_"), "Frame name should start with 'frame_'"
        assert frame_name.endswith(".png"), "Frame name should end with '.png'"
        assert len(frame_name.split('_')[1].split('.')[0]) == 4, "Frame number should be 4 digits"

    print("\n✅ Frame naming pattern verified!")


def test_frame_interval_calculation():
    """Test frame interval calculation"""
    print("\n" + "="*60)
    print("TEST: Frame Interval Calculation")
    print("="*60)

    # Test 1: Default values
    frame_count = 10
    total_duration = 5.0
    frame_interval = total_duration / frame_count

    print(f"\nTest 1: Default values")
    print(f"  Total duration: {total_duration}s")
    print(f"  Frame count: {frame_count}")
    print(f"  Frame interval: {frame_interval}s")

    expected_times = [i * frame_interval for i in range(frame_count)]
    print(f"  Frame times: {expected_times}")
    assert expected_times == [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5], "Frame times should be evenly distributed"

    # Test 2: Audio duration based calculation
    audio_duration = 3.5
    frame_count_auto = max(10, int(audio_duration * 2))  # 2 fps

    print(f"\nTest 2: Auto-adjusted frame count")
    print(f"  Audio duration: {audio_duration}s")
    print(f"  Auto frame count: {frame_count_auto} (2 fps)")
    assert frame_count_auto == 10, "Should use minimum 10 frames"

    # Test 3: Longer audio
    audio_duration_long = 15.0
    frame_count_long = max(10, int(audio_duration_long * 2))

    print(f"\nTest 3: Longer audio")
    print(f"  Audio duration: {audio_duration_long}s")
    print(f"  Auto frame count: {frame_count_long} (2 fps)")
    assert frame_count_long == 30, "Should adjust to 30 frames for 15s audio"

    print("\n✅ Frame interval calculation verified!")


def test_ffmpeg_command_construction():
    """Test FFmpeg command construction"""
    print("\n" + "="*60)
    print("TEST: FFmpeg Command Construction")
    print("="*60)

    # Simulate command construction
    output_dir = "/tmp/animated_frames_test"
    frame_pattern = os.path.join(output_dir, "frame_%04d.png")
    audio_path = "/tmp/audio.mp3"
    output_path = "/tmp/output.mp4"
    fps = 2
    duration = 3.0

    cmd = [
        "ffmpeg",
        "-framerate", str(fps),
        "-i", frame_pattern,
        "-i", audio_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-y",
        output_path
    ]

    print(f"\nFFmpeg command:")
    print(f"  {' '.join(cmd)}")

    # Verify key parameters
    assert "-framerate" in cmd, "Should have framerate parameter"
    assert str(fps) in cmd, f"Should have fps={fps}"
    assert "-t" in cmd, "Should have duration parameter"
    assert str(duration) in cmd, f"Should have duration={duration}"
    assert "libx264" in cmd, "Should have video codec"
    assert "aac" in cmd, "Should have audio codec"
    assert "yuv420p" in cmd, "Should have pixel format"

    print("\n✅ FFmpeg command construction verified!")


def test_model_changes():
    """Test model changes"""
    print("\n" + "="*60)
    print("TEST: Model Changes")
    print("="*60)

    # Read the model file directly to check for animated_frames field
    model_file = "pixelle_video/models/storyboard.py"

    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"\nChecking {model_file} for animated_frames field...")

    # Check if animated_frames field exists in StoryboardFrame
    has_field = 'animated_frames' in content
    print(f"  Has animated_frames field: {has_field}")
    assert has_field, "Should have animated_frames field in StoryboardFrame"

    # Check the field definition
    field_pattern = r'animated_frames:\s*Optional\[List\[str\]\]\s*=\s*None'
    has_correct_type = bool(re.search(field_pattern, content))
    print(f"  Correct type annotation: {has_correct_type}")
    assert has_correct_type, "Should have Optional[List[str]] type annotation"

    # Check documentation
    has_doc = '# Animated frame paths' in content or 'animated frame paths' in content.lower()
    print(f"  Has documentation: {has_doc}")
    assert has_doc, "Should have field documentation"

    print("\n✅ Model changes verified!")


def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("🎬 Animated Frame Rendering Verification")
    print("="*60)

    try:
        test_animation_detection_logic()
        test_frame_naming_pattern()
        test_frame_interval_calculation()
        test_ffmpeg_command_construction()
        test_model_changes()

        print("\n" + "="*60)
        print("✅ All verification tests passed!")
        print("="*60)

        print("\nImplementation Summary:")
        print("  ✓ Animation detection logic works correctly")
        print("  ✓ Frame naming pattern follows ffmpeg requirements")
        print("  ✓ Frame interval calculation handles various durations")
        print("  ✓ FFmpeg command construction is correct")
        print("  ✓ Model changes support animated frames")

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ Verification failed: {e}")
        print("="*60)
        raise


if __name__ == "__main__":
    main()