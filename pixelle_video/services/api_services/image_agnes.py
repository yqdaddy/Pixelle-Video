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
Agnes AI Image Generation Client

API 规范:
- 端点: POST {base_url}/images/generations
- 认证: Authorization: Bearer {api_key}
- 请求体: { model, prompt, size, ratio, image[]?, extra_body }
- 响应: { data: [{ url }] }
"""

import os
import logging
import time
import uuid
import base64
from typing import Optional, List, Dict, Any

import httpx

try:
    from .image_processor import ImageProcessor
except ImportError:
    from image_processor import ImageProcessor


class AgnesImageClient:
    """Agnes AI 图像生成客户端"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.agnes-ai.cn/v1",
        local_proxy: Optional[str] = None,
        timeout: int = 60
    ):
        """
        初始化 Agnes 图像客户端

        Args:
            api_key: Agnes API Key
            base_url: API 基础 URL
            local_proxy: 本地代理地址（可选）
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.local_proxy = local_proxy
        self.timeout = timeout
        self.image_processor = ImageProcessor(local_proxy=local_proxy)

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _get_proxies(self) -> Optional[str]:
        """获取代理配置"""
        if not self.local_proxy:
            return None
        return self.local_proxy

    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as f:
            image_data = f.read()
        # 根据文件扩展名确定 MIME 类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        mime_type = mime_types.get(ext, "image/png")
        return f"data:{mime_type};base64,{base64.b64encode(image_data).decode('utf-8')}"

    def generate_image(
        self,
        prompt: str,
        model: str = "agnes-image-2.5-flash",
        save_dir: str = "./output",
        session_id: str = "default",
        size: str = "2K",
        ratio: str = "16:9",
        image_paths: Optional[List[str]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        生成图像并下载到本地

        Args:
            prompt: 图像生成提示词
            model: 模型名称，默认 "agnes-image-2.5-flash"
            save_dir: 保存目录
            session_id: 会话 ID（用于文件命名）
            size: 图像尺寸，如 "2K", "1K"
            ratio: 图像比例，如 "16:9", "1:1", "9:16"
            image_paths: 参考图片路径列表（用于图生图）
            extra_body: 额外的请求参数

        Returns:
            本地文件路径列表
        """
        # 构建请求体
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "ratio": ratio,
        }

        # 添加参考图片（图生图模式）
        if image_paths:
            encoded_images = []
            for path in image_paths:
                if os.path.exists(path):
                    encoded_images.append(self._encode_image_to_base64(path))
            if encoded_images:
                payload["image"] = encoded_images

        # 添加额外参数
        if extra_body:
            payload["extra_body"] = extra_body

        # 发送请求
        url = f"{self.base_url}/images/generations"
        logging.info(f"Agnes API request: {url}")
        logging.debug(f"Payload: model={model}, size={size}, ratio={ratio}, images={len(image_paths) if image_paths else 0}")

        try:
            proxy = self._get_proxies()
            with httpx.Client(proxy=proxy, timeout=self.timeout) as client:
                response = client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload
                )

            if response.status_code != 200:
                error_msg = f"Agnes API error: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise RuntimeError(error_msg)

            result = response.json()

        except httpx.TimeoutException:
            error_msg = f"Agnes API request timed out after {self.timeout}s"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Agnes API request failed: {e}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

        # 解析响应
        data = result.get("data", [])
        if not data:
            error_msg = f"Agnes API returned no data: {result}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

        # 提取图片 URL
        image_urls = []
        for item in data:
            url = item.get("url")
            if url:
                image_urls.append(url)

        if not image_urls:
            error_msg = f"No image URLs found in response: {result}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

        logging.info(f"Agnes generated {len(image_urls)} image(s)")

        # 下载图片到本地
        os.makedirs(save_dir, exist_ok=True)
        local_files = []
        for i, img_url in enumerate(image_urls):
            file_name = f"agnes_{session_id}_{int(time.time())}_{i}_{uuid.uuid4().hex[:6]}.png"
            file_path = os.path.join(save_dir, file_name)
            if self.image_processor.download_image(img_url, file_path):
                local_files.append(file_path)
            else:
                logging.warning(f"Failed to download image from {img_url}")

        if not local_files:
            raise RuntimeError("Failed to download any images from Agnes API")

        return local_files


if __name__ == "__main__":
    import sys

    # 测试代码
    print("=== Agnes 图像生成客户端测试 ===")

    api_key = os.getenv("AGNES_API_KEY", "")
    base_url = os.getenv("AGNES_BASE_URL", "https://api.agnes-ai.cn/v1")

    if not api_key:
        print("AGNES_API_KEY 环境变量未设置，跳过测试")
        sys.exit(0)

    print(f"API Key: {api_key[:6]}***{api_key[-4:]}")
    print(f"Base URL: {base_url}")

    client = AgnesImageClient(api_key=api_key, base_url=base_url)

    # 文生图测试
    print("\n=== 文生图测试 ===")
    prompt = "一只橘猫躺在阳光下的窗台上，水彩画风格"
    save_dir = "output/image/test_agnes"
    os.makedirs(save_dir, exist_ok=True)

    t0 = time.time()
    try:
        paths = client.generate_image(
            prompt=prompt,
            model="agnes-image-2.5-flash",
            save_dir=save_dir,
            session_id="test",
            size="1K",
            ratio="1:1"
        )
        elapsed = time.time() - t0
        if paths:
            print(f"✓ 生成 {len(paths)} 张图片 ({elapsed:.1f}s): {paths}")
        else:
            print(f"✗ 返回空列表 ({elapsed:.1f}s)")
    except Exception as e:
        print(f"✗ 失败: {e}")
        sys.exit(1)