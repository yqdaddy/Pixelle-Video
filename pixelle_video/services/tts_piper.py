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
Piper TTS - 离线语音合成

使用 Piper TTS 引擎进行本地语音合成。
完全离线，无需网络，支持中文。
"""

import asyncio
import os
import subprocess
import uuid
from pathlib import Path
from typing import Optional, List

from loguru import logger

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    PiperVoice = None


# Piper 可用声音
PIPER_VOICES = {
    "zh_CN": {
        "huayan-medium": {
            "name": "zh_CN-huayan-medium",
            "description": "Chinese Mandarin female voice",
            "display_name": "女声-普通话（花音）",
            "model_file": "zh_CN-huayan-medium.onnx",
        },
    },
    "en_US": {
        "lessac-medium": {
            "name": "en_US-lessac-medium",
            "description": "American English female voice",
            "display_name": "Female-English（Lessac）",
            "model_file": "en_US-lessac-medium.onnx",
        },
    },
}


class PiperTTSClient:
    """Piper TTS 客户端"""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Piper TTS client

        Args:
            model_path: Path to Piper model file (.onnx)
                       If None, uses default model from config

        Raises:
            ImportError: If piper-tts is not installed
            FileNotFoundError: If model file does not exist
        """
        if not self.is_available():
            raise ImportError(
                "piper-tts is not installed. "
                "Install with: pip install piper-tts"
            )

        self.model_path = model_path
        self._voice = None

    @staticmethod
    def is_available() -> bool:
        """Check if Piper TTS is available

        Returns:
            True if piper-tts is installed
        """
        return PIPER_AVAILABLE

    def _load_voice(self) -> PiperVoice:
        """Load Piper voice model (lazy loading)

        Returns:
            PiperVoice instance

        Raises:
            FileNotFoundError: If model file does not exist
        """
        if self._voice is None:
            if not self.model_path:
                raise ValueError("Model path not configured")

            model_path = Path(self.model_path)
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Piper model not found: {model_path}\n"
                    "Download from: https://huggingface.co/rhasspy/piper-voices"
                )

            logger.info(f"Loading Piper model: {model_path}")
            self._voice = PiperVoice.load(str(model_path))

        return self._voice

    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        output_path: Optional[str] = None,
        speed: float = 1.0,
    ) -> str:
        """
        Synthesize speech from text using Piper TTS

        Args:
            text: Text to synthesize
            voice: Voice name (ignored for now, uses loaded model)
            output_path: Output file path (.mp3 or .wav)
                        If None, auto-generates in output/ directory
            speed: Speech rate (not supported by Piper, kept for API compatibility)

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

        logger.info(f"🎙️  Using Piper TTS: model={Path(self.model_path).stem}")

        try:
            # Load voice
            voice_instance = self._load_voice()

            # Piper outputs WAV format
            # Use temporary WAV file, then convert to MP3
            temp_wav = output_path.with_suffix(".wav")

            # Synthesize to WAV using correct Piper API
            logger.debug(f"Synthesizing text to WAV: {temp_wav}")
            import wave
            chunks = list(voice_instance.synthesize(text))
            if chunks:
                with wave.open(str(temp_wav), 'wb') as wav_file:
                    first_chunk = chunks[0]
                    wav_file.setframerate(first_chunk.sample_rate)
                    wav_file.setsampwidth(first_chunk.sample_width)
                    wav_file.setnchannels(first_chunk.sample_channels)
                    for chunk in chunks:
                        wav_file.writeframes(chunk.audio_int16_bytes)

            # Check if WAV was created
            if not temp_wav.exists():
                raise RuntimeError("WAV file was not created")

            # Convert to MP3 using ffmpeg
            if output_path.suffix.lower() == ".wav":
                # Keep as WAV, just rename
                temp_wav.rename(output_path)
            else:
                # Convert to MP3 using ffmpeg
                convert_cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file
                    "-i", str(temp_wav),
                    "-acodec", "libmp3lame",  # MP3 codec
                    "-q:a", "2",  # Quality (2 = high quality)
                    str(output_path)
                ]

                logger.debug(f"Converting audio: {' '.join(convert_cmd)}")

                convert_result = subprocess.run(
                    convert_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Clean up temporary WAV
                temp_wav.unlink()

                if convert_result.returncode != 0:
                    error_msg = convert_result.stderr or "Unknown conversion error"
                    logger.error(f"ffmpeg conversion failed: {error_msg}")
                    raise RuntimeError(f"Audio conversion failed: {error_msg}")

            logger.info(f"✅ Generated audio: {output_path}")
            return str(output_path)

        except subprocess.TimeoutExpired:
            logger.error("Audio conversion timeout")
            raise RuntimeError("Audio conversion timeout")
        except FileNotFoundError as e:
            if "ffmpeg" in str(e):
                logger.error("ffmpeg not found, required for audio conversion")
                raise RuntimeError(
                    "ffmpeg not found. Install with: brew install ffmpeg"
                )
            raise
        except Exception as e:
            logger.error(f"Piper TTS synthesis error: {e}")
            raise

    async def synthesize_async(
        self,
        text: str,
        voice: Optional[str] = None,
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
        List available Piper voices

        Returns:
            List of voice info dicts
        """
        if not PIPER_AVAILABLE:
            return []

        voices = []
        for lang_code, lang_voices in PIPER_VOICES.items():
            for voice_key, voice_info in lang_voices.items():
                voices.append({
                    "name": voice_info["name"],
                    "language": lang_code,
                    "description": voice_info["description"],
                    "display_name": voice_info["display_name"],
                    "model_file": voice_info["model_file"],
                })

        return voices


# Singleton instance
_default_client = None


def get_piper_tts_client(model_path: Optional[str] = None) -> PiperTTSClient:
    """
    Get or create default Piper TTS client

    Uses singleton pattern with model path configuration.

    Args:
        model_path: Path to Piper model file (.onnx)

    Returns:
        PiperTTSClient instance

    Raises:
        ImportError: If piper-tts is not installed
        FileNotFoundError: If model file does not exist
    """
    global _default_client

    # If client exists but model_path changed, recreate
    if _default_client is not None and model_path != _default_client.model_path:
        _default_client = None

    if _default_client is None:
        _default_client = PiperTTSClient(model_path=model_path)

    return _default_client