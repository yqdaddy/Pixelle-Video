# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
macOS 系统 TTS - 使用 say 命令

仅支持 macOS，使用系统自带语音引擎。
完全离线，无需网络，支持中文。
"""

import asyncio
import os
import platform
import subprocess
import uuid
from pathlib import Path
from typing import Optional, List

from loguru import logger


# macOS 可用声音
MACOS_VOICES = {
    "zh_CN": {
        "ting-ting": {
            "name": "Ting-Ting",
            "description": "普通话女声",
            "display_name": "女声-普通话（婷婷）",
        },
    },
    "zh_HK": {
        "sin-ji": {
            "name": "Sin-ji",
            "description": "粤语女声",
            "display_name": "女声-粤语（善施）",
        },
    },
    "zh_TW": {
        "mei-jia": {
            "name": "Mei-Jia",
            "description": "台湾国语女声",
            "display_name": "女声-台湾国语（美佳）",
        },
    },
    "en_US": {
        "alex": {
            "name": "Alex",
            "description": "American English male",
            "display_name": "Male-English（Alex）",
        },
        "samantha": {
            "name": "Samantha",
            "description": "American English female",
            "display_name": "Female-English（Samantha）",
        },
        "victoria": {
            "name": "Victoria",
            "description": "American English female",
            "display_name": "Female-English（Victoria）",
        },
    },
    "en_GB": {
        "daniel": {
            "name": "Daniel",
            "description": "British English male",
            "display_name": "Male-British（Daniel）",
        },
    },
    "ja_JP": {
        "kyoko": {
            "name": "Kyoko",
            "description": "Japanese female",
            "display_name": "Female-Japanese（Kyoko）",
        },
    },
    "ko_KR": {
        "yuna": {
            "name": "Yuna",
            "description": "Korean female",
            "display_name": "Female-Korean（Yuna）",
        },
    },
}


class MacOSTTSClient:
    """macOS say 命令 TTS 客户端"""

    def __init__(self):
        """Initialize macOS TTS client

        Raises:
            RuntimeError: If not running on macOS
        """
        if not self.is_available():
            raise RuntimeError(
                "macOS TTS only available on macOS. "
                "Please use Edge TTS (inference_mode='local') or ComfyUI TTS."
            )

    @staticmethod
    def is_available() -> bool:
        """Check if macOS TTS is available

        Returns:
            True if running on macOS and 'say' command exists
        """
        return (
            platform.system() == "Darwin"
            and os.path.exists("/usr/bin/say")
        )

    def synthesize(
        self,
        text: str,
        voice: str = "Ting-Ting",
        output_path: Optional[str] = None,
        speed: float = 1.0,
    ) -> str:
        """
        Synthesize speech from text using macOS say command

        Args:
            text: Text to synthesize
            voice: Voice name (e.g., Ting-Ting, Sin-ji, Mei-Jia)
                   Default: Ting-Ting (Mandarin Chinese female)
            output_path: Output file path (.mp3 or .wav)
                        If None, auto-generates in output/ directory
            speed: Speech rate (not supported by say command, kept for API compatibility)

        Returns:
            Path to generated audio file

        Raises:
            ValueError: If text is empty
            RuntimeError: If synthesis fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Generate output path if not provided
        if not output_path:
            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = f"output/{uuid.uuid4().hex}.mp3"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"🎙️  Using macOS TTS: voice={voice}")

        try:
            # macOS 'say' command outputs AIFF format
            # We'll use a temporary AIFF file, then convert to target format
            temp_aiff = output_path.with_suffix(".aiff")

            # Build say command
            cmd = [
                "/usr/bin/say",
                "-v", voice,
                "-o", str(temp_aiff),
                text
            ]

            logger.debug(f"Running command: {' '.join(cmd)}")

            # Execute say command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 seconds timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                logger.error(f"say command failed: {error_msg}")
                raise RuntimeError(f"macOS TTS synthesis failed: {error_msg}")

            # Check if AIFF was created
            if not temp_aiff.exists():
                raise RuntimeError("AIFF file was not created")

            # Convert to target format using ffmpeg
            if output_path.suffix.lower() == ".aiff":
                # Keep as AIFF, just rename
                temp_aiff.rename(output_path)
            else:
                # Convert to MP3/WAV/etc using ffmpeg
                convert_cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file
                    "-i", str(temp_aiff),
                    str(output_path)
                ]

                logger.debug(f"Converting audio: {' '.join(convert_cmd)}")

                convert_result = subprocess.run(
                    convert_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Clean up temporary AIFF
                temp_aiff.unlink()

                if convert_result.returncode != 0:
                    error_msg = convert_result.stderr or "Unknown conversion error"
                    logger.error(f"ffmpeg conversion failed: {error_msg}")
                    raise RuntimeError(f"Audio conversion failed: {error_msg}")

            logger.info(f"✅ Generated audio: {output_path}")
            return str(output_path)

        except subprocess.TimeoutExpired:
            logger.error("macOS TTS synthesis timeout")
            raise RuntimeError("macOS TTS synthesis timeout")
        except FileNotFoundError as e:
            if "ffmpeg" in str(e):
                logger.error("ffmpeg not found, required for audio conversion")
                raise RuntimeError(
                    "ffmpeg not found. Install with: brew install ffmpeg"
                )
            raise
        except Exception as e:
            logger.error(f"macOS TTS synthesis error: {e}")
            raise

    async def synthesize_async(
        self,
        text: str,
        voice: str = "Ting-Ting",
        output_path: Optional[str] = None,
        speed: float = 1.0,
    ) -> str:
        """
        Async wrapper for synthesize

        Runs synthesis in a thread pool to avoid blocking.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.synthesize(
                text=text,
                voice=voice,
                output_path=output_path,
                speed=speed
            )
        )

    @staticmethod
    def list_voices() -> List[dict]:
        """
        List available voices on macOS

        Returns:
            List of voice info dicts with 'name', 'language', 'description'
        """
        if not MacOSTTSClient.is_available():
            return []

        try:
            # Run 'say -v ?' to list voices
            result = subprocess.run(
                ["/usr/bin/say", "-v", "?"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.warning("Failed to list voices")
                return []

            voices = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                # Parse voice info
                # Format: "Ting-Ting          zh_CN    # Chinese Mandarin"
                parts = line.split(maxsplit=2)
                if len(parts) >= 2:
                    voice_name = parts[0]
                    lang_code = parts[1]
                    description = parts[2].lstrip("# ") if len(parts) > 2 else ""

                    voices.append({
                        "name": voice_name,
                        "language": lang_code,
                        "description": description
                    })

            return voices

        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []


# Singleton instance for easy access
_default_client = None


def get_macos_tts_client() -> MacOSTTSClient:
    """
    Get or create default macOS TTS client

    Uses singleton pattern.

    Returns:
        MacOSTTSClient instance

    Raises:
        RuntimeError: If not running on macOS
    """
    global _default_client

    if _default_client is None:
        _default_client = MacOSTTSClient()

    return _default_client