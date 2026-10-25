# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
HTML-based Frame Generator Service

Renders HTML templates to frame images using Playwright for headless browser rendering.

Linux Environment Requirements:
    - fontconfig package must be installed
    - Basic fonts (e.g., fonts-liberation, fonts-noto) recommended
    
    Ubuntu/Debian: sudo apt-get install -y fontconfig fonts-liberation fonts-noto-cjk
    CentOS/RHEL: sudo yum install -y fontconfig liberation-fonts google-noto-cjk-fonts
    
    Playwright browser install: playwright install --with-deps chromium
"""

import asyncio
import os
import re
import tempfile
import uuid
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

from pixelle_video.utils.template_util import parse_template_size


class HTMLFrameGenerator:
    """
    HTML-based frame generator
    
    Renders HTML templates to frame images with variable substitution.
    Uses Playwright for reliable headless browser rendering.
    
    Usage:
        >>> generator = HTMLFrameGenerator("templates/modern.html")
        >>> frame_path = await generator.generate_frame(
        ...     topic="Why reading matters",
        ...     text="Reading builds new neural pathways...",
        ...     image="/path/to/image.png",
        ...     ext={"content_title": "Sample Title", "content_author": "Author Name"}
        ... )
    """
    
    _browser = None
    _playwright = None
    _browser_loop = None

    def __init__(self, template_path: str):
        """
        Initialize HTML frame generator
        
        Args:
            template_path: Path to HTML template file (e.g., "templates/1080x1920/default.html")
        """
        self.template_path = template_path
        self.template = self._load_template(template_path)
        
        # Parse video size from template path
        self.width, self.height = parse_template_size(template_path)
        
        self._check_linux_dependencies()
        logger.debug(f"Loaded HTML template: {template_path} (size: {self.width}x{self.height})")
    
    
    def _check_linux_dependencies(self):
        """Check Linux system dependencies and warn if missing"""
        if os.name != 'posix':
            return
        
        try:
            import subprocess
            
            result = subprocess.run(
                ['fc-list'], 
                capture_output=True, 
                timeout=2
            )
            
            if result.returncode != 0:
                logger.warning(
                    "fontconfig not found or not working properly. "
                    "Install with: sudo apt-get install -y fontconfig fonts-liberation fonts-noto-cjk"
                )
            elif not result.stdout:
                logger.warning(
                    "No fonts detected by fontconfig. "
                    "Install fonts with: sudo apt-get install -y fonts-liberation fonts-noto-cjk"
                )
            else:
                logger.debug(f"Fontconfig detected {len(result.stdout.splitlines())} fonts")
                
        except FileNotFoundError:
            logger.warning(
                "fontconfig (fc-list) not found on system. "
                "Install with: sudo apt-get install -y fontconfig"
            )
        except Exception as e:
            logger.debug(f"Could not check fontconfig status: {e}")
    
    def _load_template(self, template_path: str) -> str:
        """Load HTML template from file"""
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.debug(f"Template loaded: {len(content)} chars")
        return content
    
    def _parse_media_size_from_meta(self) -> tuple[Optional[int], Optional[int]]:
        """
        Parse media size from meta tags in template
        
        Looks for meta tags:
        - <meta name="template:media-width" content="1024">
        - <meta name="template:media-height" content="1024">
        
        Returns:
            Tuple of (width, height) or (None, None) if not found
        """
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(self.template, 'html.parser')
            
            width_meta = soup.find('meta', attrs={'name': 'template:media-width'})
            height_meta = soup.find('meta', attrs={'name': 'template:media-height'})
            
            if width_meta and height_meta:
                width = int(width_meta.get('content', 0))
                height = int(height_meta.get('content', 0))
                
                if width > 0 and height > 0:
                    logger.debug(f"Found media size in meta tags: {width}x{height}")
                    return width, height
            
            return None, None
            
        except Exception as e:
            logger.warning(f"Failed to parse media size from meta tags: {e}")
            return None, None
    
    def get_media_size(self) -> tuple[int, int]:
        """
        Get media size for image/video generation

        Returns media size specified in template meta tags.

        Returns:
            Tuple of (width, height)
        """
        media_width, media_height = self._parse_media_size_from_meta()

        if media_width and media_height:
            return media_width, media_height

        logger.warning(f"No media size meta tags found in template {self.template_path}, using fallback 1024x1024")
        return 1024, 1024

    def has_animations(self) -> bool:
        """
        Check if template contains CSS animations

        Detects animation-related CSS:
        - @keyframes rules
        - animation properties

        Returns:
            True if template contains animations, False otherwise

        Example:
            >>> generator = HTMLFrameGenerator("animated_template.html")
            >>> if generator.has_animations():
            ...     frames = await generator.generate_animated_frames(...)
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
    
    def parse_template_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Parse custom parameters from HTML template
        
        Supports syntax: {{param:type=default}}
        - {{param}} -> text type, no default
        - {{param=value}} -> text type, with default
        - {{param:type}} -> specified type, no default
        - {{param:type=value}} -> specified type, with default
        
        Supported types: text, number, color, bool
        
        Returns:
            Dictionary of custom parameters with their configurations:
            {
                'param_name': {
                    'type': 'text' | 'number' | 'color' | 'bool',
                    'default': Any,
                    'label': str  # same as param_name
                }
            }
        """
        PRESET_PARAMS = {'title', 'text', 'image', 'index'}
        
        PARAM_PATTERN = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)(?::([a-z]+))?(?:=([^}]+))?\}\}'
        
        params = {}
        
        for match in re.finditer(PARAM_PATTERN, self.template):
            param_name = match.group(1)
            param_type = match.group(2) or 'text'
            default_value = match.group(3)
            
            if param_name in PRESET_PARAMS:
                continue
            
            if param_name in params:
                continue
            
            if param_type not in {'text', 'number', 'color', 'bool'}:
                logger.warning(f"Unknown parameter type '{param_type}' for '{param_name}', defaulting to 'text'")
                param_type = 'text'
            
            parsed_default = self._parse_default_value(param_type, default_value)
            
            params[param_name] = {
                'type': param_type,
                'default': parsed_default,
                'label': param_name,
            }
        
        if params:
            logger.debug(f"Parsed {len(params)} custom parameter(s) from template: {list(params.keys())}")
        
        return params
    
    def _parse_default_value(self, param_type: str, value_str: Optional[str]) -> Any:
        """
        Parse default value based on parameter type
        
        Args:
            param_type: Type of parameter (text, number, color, bool)
            value_str: String value to parse (can be None)
        
        Returns:
            Parsed value with appropriate type
        """
        if value_str is None:
            return {
                'text': '',
                'number': 0,
                'color': '#000000',
                'bool': False,
            }.get(param_type, '')
        
        if param_type == 'number':
            try:
                if '.' in value_str:
                    return float(value_str)
                else:
                    return int(value_str)
            except ValueError:
                logger.warning(f"Invalid number value '{value_str}', using 0")
                return 0
        
        elif param_type == 'bool':
            return value_str.lower() in {'true', '1', 'yes', 'on'}
        
        elif param_type == 'color':
            if value_str.startswith('#'):
                return value_str
            else:
                return f'#{value_str}'
        
        else:  # text
            return value_str
    
    def _replace_parameters(self, html: str, values: Dict[str, Any]) -> str:
        """
        Replace parameter placeholders with actual values
        
        Supports DSL syntax: {{param:type=default}}
        - If value provided in values dict, use it
        - Otherwise, use default value from placeholder
        - If no default, use empty string
        
        Args:
            html: HTML template content
            values: Dictionary of parameter values
        
        Returns:
            HTML with placeholders replaced
        """
        PARAM_PATTERN = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)(?::([a-z]+))?(?:=([^}]+))?\}\}'
        
        def replacer(match):
            param_name = match.group(1)
            param_type = match.group(2) or 'text'
            default_value_str = match.group(3)
            
            if param_name in values:
                value = values[param_name]
                if isinstance(value, bool):
                    return 'true' if value else 'false'
                return str(value) if value is not None else ''
            
            elif default_value_str:
                return default_value_str
            
            else:
                return ''
        
        return re.sub(PARAM_PATTERN, replacer, html)

    @classmethod
    async def _ensure_browser(cls):
        """Lazily initialize a shared Playwright browser instance"""
        current_loop = asyncio.get_running_loop()
        browser_usable = (
            cls._browser is not None
            and cls._browser_loop is current_loop
            and cls._browser.is_connected()
        )

        if not browser_usable:
            if cls._browser is not None and cls._browser_loop is not current_loop:
                logger.warning(
                    "Detected cross-loop Playwright browser reuse attempt; "
                    "recreating browser for current event loop"
                )

            cls._browser = None
            cls._playwright = None
            from playwright.async_api import async_playwright
            cls._playwright = await async_playwright().start()
            cls._browser = await cls._playwright.chromium.launch(
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                ]
            )
            cls._browser_loop = current_loop
            logger.debug("Initialized Playwright Chromium browser")
        return cls._browser

    @classmethod
    def _discard_browser_references(cls):
        """Drop stale Playwright objects that belong to another event loop."""
        cls._browser = None
        cls._playwright = None
        cls._browser_loop_id = None

    @classmethod
    async def _reset_browser(cls):
        """Best-effort reset for stale or broken Playwright connections."""
        if cls._browser:
            try:
                if cls._browser.is_connected():
                    await asyncio.wait_for(cls._browser.close(), timeout=5)
            except Exception as e:
                logger.debug(f"Ignoring error while closing stale browser: {e}")
            finally:
                cls._browser = None

        if cls._playwright:
            try:
                await asyncio.wait_for(cls._playwright.stop(), timeout=5)
            except Exception as e:
                logger.debug(f"Ignoring error while stopping stale Playwright: {e}")
            finally:
                cls._playwright = None
                cls._browser_loop_id = None

    @classmethod
    async def close_browser(cls):
        """Shutdown the shared browser instance (call on app teardown)"""
        if cls._browser:
            await cls._browser.close()
            cls._browser = None
            cls._browser_loop = None
        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None
            logger.debug("Playwright browser closed")

    async def generate_frame(
        self,
        title: str,
        text: str,
        image: str,
        ext: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate frame from HTML template

        Video size is automatically determined from template path during initialization.

        Args:
            title: Video title
            text: Narration text for this frame
            image: Path to AI-generated image (supports relative path, absolute path, or HTTP URL)
            ext: Additional data (content_title, content_author, etc.)
            output_path: Custom output path (auto-generated if None)

        Returns:
            Path to generated frame image
        """
        if image and not image.startswith(('http://', 'https://', 'data:', 'file://')):
            image_path = Path(image)
            if not image_path.is_absolute():
                image_path = Path.cwd() / image

            if not image_path.exists():
                logger.warning(f"Image file not found: {image_path}")
            else:
                image = image_path.as_uri()
                logger.debug(f"Converted image path to: {image}")

        context = {
            "title": title,
            "text": text,
            "image": image,
        }

        if ext:
            context.update(ext)

        html = self._replace_parameters(self.template, context)

        if output_path is None:
            from pixelle_video.utils.os_util import get_output_path
            output_filename = f"frame_{uuid.uuid4().hex[:16]}.png"
            output_path = get_output_path(output_filename)
        else:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.debug(f"Rendering HTML template to {output_path} (size: {self.width}x{self.height})")
        tmp_html_path = None
        page = None
        try:
            try:
                browser = await self._ensure_browser()
                page = await browser.new_page(
                    viewport={'width': self.width, 'height': self.height},
                    device_scale_factor=1,
                )
            except Exception as e:
                logger.warning(f"Playwright browser connection failed, restarting once: {e}")
                await self._reset_browser()
                browser = await self._ensure_browser()
                page = await browser.new_page(
                    viewport={'width': self.width, 'height': self.height},
                    device_scale_factor=1,
                )

            try:
                # Write HTML to a temp file and navigate via file:// URL so that
                # local file:// image references are loaded under the same origin.
                fd, tmp_html_path = tempfile.mkstemp(suffix='.html', prefix='pv_frame_')
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(html)

                await page.goto(Path(tmp_html_path).as_uri(), wait_until='networkidle')
                await page.screenshot(path=output_path, type='png', omit_background=True)
            finally:
                if page:
                    await page.close()
                if tmp_html_path and os.path.exists(tmp_html_path):
                    os.unlink(tmp_html_path)

            logger.info(f"Frame generated: {output_path}")
            return output_path

        except Exception as e:
            logger.exception("Failed to render HTML template")
            raise RuntimeError(
                f"HTML rendering failed: {type(e).__name__}: {e}"
            ) from e

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
            title: Video title
            text: Narration text for this frame
            image: Path to AI-generated image
            ext: Additional data (content_title, content_author, etc.)
            output_dir: Directory to save frames (auto-generated if None)
            frame_count: Number of frames to generate (default: 10)
            total_duration: Total animation duration in seconds (default: 5.0)

        Returns:
            List of paths to generated frame images

        Example:
            >>> frames = await generator.generate_animated_frames(
            ...     title="My Title",
            ...     text="Some text",
            ...     image="image.png",
            ...     frame_count=10,
            ...     total_duration=5.0
            ... )
            >>> # Returns: ['frame_0.png', 'frame_1.png', ..., 'frame_9.png']
        """
        if image and not image.startswith(('http://', 'https://', 'data:', 'file://')):
            image_path = Path(image)
            if not image_path.is_absolute():
                image_path = Path.cwd() / image

            if not image_path.exists():
                logger.warning(f"Image file not found: {image_path}")
            else:
                image = image_path.as_uri()
                logger.debug(f"Converted image path to: {image}")

        context = {
            "title": title,
            "text": text,
            "image": image,
        }

        if ext:
            context.update(ext)

        html = self._replace_parameters(self.template, context)

        # Create output directory
        if output_dir is None:
            from pixelle_video.utils.os_util import get_output_path
            output_dir = get_output_path(f"animated_frames_{uuid.uuid4().hex[:16]}")

        os.makedirs(output_dir, exist_ok=True)

        logger.info(
            f"Rendering animated template to {frame_count} frames "
            f"(duration: {total_duration}s, size: {self.width}x{self.height})"
        )

        tmp_html_path = None
        page = None
        frame_paths = []

        try:
            # Initialize browser
            try:
                browser = await self._ensure_browser()
                page = await browser.new_page(
                    viewport={'width': self.width, 'height': self.height},
                    device_scale_factor=1,
                )
            except Exception as e:
                logger.warning(f"Playwright browser connection failed, restarting once: {e}")
                await self._reset_browser()
                browser = await self._ensure_browser()
                page = await browser.new_page(
                    viewport={'width': self.width, 'height': self.height},
                    device_scale_factor=1,
                )

            # Write HTML to temp file
            fd, tmp_html_path = tempfile.mkstemp(suffix='.html', prefix='pv_animated_')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html)

            # Navigate to HTML
            await page.goto(Path(tmp_html_path).as_uri(), wait_until='networkidle')

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

            logger.success(f"Animated frames generated: {len(frame_paths)} frames in {output_dir}")
            return frame_paths

        except Exception as e:
            logger.exception("Failed to render animated HTML template")
            raise RuntimeError(
                f"Animated HTML rendering failed: {type(e).__name__}: {e}"
            ) from e
        finally:
            if page:
                await page.close()
            if tmp_html_path and os.path.exists(tmp_html_path):
                os.unlink(tmp_html_path)
