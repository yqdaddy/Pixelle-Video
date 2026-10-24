"""
Agnes AI Video 生成客户端 (V2.0)
基于 Agnes API 的文生视频 (text2video) / 图生视频 (image2video) 功能
支持模型: agnes-video-2.5-flash, agnes-video-2.5-pro
"""

import os
import time
import base64
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Agnes API 默认地址
AGNES_DEFAULT_BASE_URL = "https://api.agnes.ai"


class AgnesVideoClient:
    """
    Agnes AI 视频生成客户端
    使用 Bearer Token 鉴权，支持文生视频和图生视频

    API 流程:
      1. POST /videos 创建任务，返回 video_id
      2. GET /agnesapi?video_id=xxx&model_name=xxx 轮询状态
      3. 任务成功后返回远端视频 URL
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        local_proxy: Optional[str] = None,
        timeout: int = 300,
        poll_interval: int = 5,
        max_polls: int = 120,
    ) -> None:
        """
        初始化 Agnes 视频客户端

        Args:
            api_key: Agnes API Key
            base_url: Agnes API 基础 URL
            local_proxy: 本地代理地址
            timeout: HTTP 请求超时时间（秒）
            poll_interval: 轮询间隔（秒）
            max_polls: 最大轮询次数
        """
        self.api_key = api_key or os.getenv("AGNES_API_KEY", "")
        self.base_url = (base_url or os.getenv("AGNES_BASE_URL", "")).rstrip("/") or AGNES_DEFAULT_BASE_URL
        self.local_proxy = local_proxy
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_polls = max_polls

        if not self.api_key:
            logger.warning("AgnesVideoClient: AGNES_API_KEY 未设置，请检查配置")

    def _headers(self) -> dict:
        """构建带 Bearer Token 鉴权的请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _get_proxies(self) -> Optional[str]:
        """获取代理配置"""
        if not self.local_proxy:
            return None
        return self.local_proxy

    def _encode_image(self, image_path: str) -> str:
        """
        将本地图片编码为 Base64 Data URL

        Args:
            image_path: 本地图片路径

        Returns:
            Data URL 格式的 Base64 字符串 (data:image/xxx;base64,...)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"输入图片不存在: {image_path}")

        with open(image_path, "rb") as f:
            img_data = f.read()

        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        mime = mime_map.get(ext, "image/jpeg")

        return f"data:{mime};base64,{base64.b64encode(img_data).decode('utf-8')}"

    def _create_task(
        self,
        prompt: str,
        model: str,
        duration: int,
        aspect_ratio: str,
        mode: str,
        image_path: Optional[str] = None,
    ) -> str:
        """
        创建视频生成任务

        Args:
            prompt: 视频描述提示词
            model: 模型名称 (agnes-video-2.5-flash / agnes-video-2.5-pro)
            duration: 视频时长（秒）
            aspect_ratio: 视频比例 (16:9, 9:16, 1:1 等)
            mode: 生成模式 (text / keyframe / reference)
            image_path: 输入图片路径（图生视频时必填）

        Returns:
            video_id: 任务 ID
        """
        url = f"{self.base_url}/videos"

        # 构建请求体
        body = {
            "prompt": prompt,
            "model_name": model,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
        }

        # 图生视频时添加图片
        if image_path and mode in ("keyframe", "reference"):
            body["image"] = self._encode_image(image_path)

        logger.info(
            f"AgnesVideoClient: 创建任务 model={model}, mode={mode}, "
            f"duration={duration}s, aspect_ratio={aspect_ratio}"
        )

        with httpx.Client(timeout=self.timeout, proxy=self.local_proxy) as client:
            resp = client.post(url, headers=self._headers(), json=body)

            if not resp.is_success:
                logger.error(f"Agnes 创建任务失败: HTTP {resp.status_code}, {resp.text}")
                resp.raise_for_status()

            data = resp.json()

        # 解析返回的 video_id
        video_id = data.get("video_id") or data.get("data", {}).get("video_id") or data.get("id")
        if not video_id:
            raise RuntimeError(f"Agnes API 未返回 video_id: {data}")

        logger.info(f"AgnesVideoClient: 任务已创建 video_id={video_id}")
        return video_id

    def _poll_status(self, video_id: str, model: str) -> dict:
        """
        轮询任务状态

        Args:
            video_id: 任务 ID
            model: 模型名称

        Returns:
            状态字典: {status, progress, url}
            - status: pending / processing / completed / failed
            - progress: 进度百分比 (0-100)
            - url: 远端视频 URL (仅 completed 时有值)
        """
        url = f"{self.base_url}/agnesapi"
        params = {
            "video_id": video_id,
            "model_name": model,
        }

        with httpx.Client(timeout=30, proxy=self.local_proxy) as client:
            resp = client.get(url, headers=self._headers(), params=params)
            resp.raise_for_status()
            data = resp.json()

        # 解析状态字段
        # API 可能返回的字段: status / state / task_status
        raw_status = data.get("status") or data.get("state") or data.get("task_status", "unknown")

        # 统一状态映射
        status_map = {
            "pending": "pending",
            "queued": "pending",
            "processing": "processing",
            "running": "processing",
            "in_progress": "processing",
            "completed": "completed",
            "succeed": "completed",
            "succeeded": "completed",
            "success": "completed",
            "failed": "failed",
            "error": "failed",
        }
        status = status_map.get(raw_status.lower(), raw_status.lower())

        # 进度
        progress = data.get("progress") or data.get("percentage") or 0
        if isinstance(progress, str):
            progress = int(progress.replace("%", ""))

        # 视频 URL
        video_url = (
            data.get("url")
            or data.get("video_url")
            or data.get("result", {}).get("url")
            or data.get("data", {}).get("url")
            or ""
        )

        return {
            "status": status,
            "progress": progress,
            "url": video_url,
            "raw_response": data,
        }

    def _poll_until_done(self, video_id: str, model: str) -> str:
        """
        轮询任务直到完成

        Args:
            video_id: 任务 ID
            model: 模型名称

        Returns:
            video_url: 远端视频 URL

        Raises:
            RuntimeError: 任务失败
            TimeoutError: 超过最大轮询次数
        """
        for attempt in range(self.max_polls):
            result = self._poll_status(video_id, model)
            status = result["status"]
            progress = result["progress"]

            if status == "completed":
                video_url = result["url"]
                if not video_url:
                    raise RuntimeError(f"Agnes 任务完成但未返回视频 URL (video_id={video_id})")
                logger.info(f"AgnesVideoClient: 任务完成 video_id={video_id}, url={video_url[:50]}...")
                return video_url

            elif status == "failed":
                error_msg = result["raw_response"].get("error") or result["raw_response"].get("message") or "未知错误"
                raise RuntimeError(f"Agnes 视频生成失败: {error_msg} (video_id={video_id})")

            else:
                # pending / processing
                logger.debug(
                    f"AgnesVideoClient: 任务进行中 video_id={video_id}, "
                    f"status={status}, progress={progress}%, attempt={attempt + 1}/{self.max_polls}"
                )
                time.sleep(self.poll_interval)

        raise TimeoutError(
            f"Agnes 视频生成超时 (video_id={video_id}, 已等待 {self.max_polls * self.poll_interval}s)"
        )

    def _download_video(self, video_url: str, save_path: str) -> None:
        """
        下载视频到本地

        Args:
            video_url: 远端视频 URL
            save_path: 本地保存路径
        """
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        with httpx.Client(timeout=600, proxy=self.local_proxy) as client:
            with client.stream("GET", video_url) as resp:
                resp.raise_for_status()
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

        logger.info(f"AgnesVideoClient: 视频已保存: {save_path}")

    def generate_video(
        self,
        prompt: str,
        save_path: str,
        model: str = "agnes-video-2.5-flash",
        image_path: Optional[str] = None,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        mode: str = "text",
    ) -> str:
        """
        异步生成视频: 提交任务 -> 轮询 -> 下载

        Args:
            prompt: 视频描述提示词
            save_path: 输出视频保存路径
            model: 模型名称 (agnes-video-2.5-flash / agnes-video-2.5-pro)
            image_path: 输入图片本地路径（图生视频时必填）
            duration: 视频时长（秒）
            aspect_ratio: 视频比例 (16:9, 9:16, 1:1 等)
            mode: 生成模式
                - text: 纯文本生成视频
                - keyframe: 首帧图生视频
                - reference: 参考图风格生成

        Returns:
            video_url: 远端视频 URL

        Raises:
            FileNotFoundError: 输入图片不存在
            RuntimeError: 生成或下载失败
            TimeoutError: 轮询超时
        """
        # 验证参数
        if not prompt and not image_path:
            raise ValueError("prompt 和 image_path 不能同时为空")

        if mode in ("keyframe", "reference") and not image_path:
            raise ValueError(f"mode={mode} 时必须提供 image_path")

        # 1. 创建任务
        video_id = self._create_task(
            prompt=prompt,
            model=model,
            duration=duration,
            aspect_ratio=aspect_ratio,
            mode=mode,
            image_path=image_path,
        )

        # 2. 轮询等待
        video_url = self._poll_until_done(video_id, model)

        # 3. 下载视频
        self._download_video(video_url, save_path)

        return video_url


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # ── 测试参数（按需修改） ──
    PROMPT = "A serene lake at sunset with gentle ripples reflecting golden light"
    OUTPUT_PATH = "code/result/video/test_avail/agnes_test_output.mp4"
    MODEL = "agnes-video-2.5-flash"
    DURATION = 5
    ASPECT_RATIO = "16:9"
    MODE = "text"  # text / keyframe / reference
    IMAGE_PATH = None  # 图生视频时设置路径

    print("=== Agnes AI Video 生成测试 ===")
    api_key = os.getenv("AGNES_API_KEY")

    if not api_key:
        print("AGNES_API_KEY 未设置，请检查环境变量")
        sys.exit(1)

    print(f"  API Key   : {api_key[:6]}***{api_key[-4:]}")
    print(f"  Base URL  : {AGNES_DEFAULT_BASE_URL}")
    print(f"  模型      : {MODEL}")
    print(f"  时长      : {DURATION}s")
    print(f"  比例      : {ASPECT_RATIO}")
    print(f"  模式      : {MODE}")
    print(f"  提示词    : {PROMPT[:60]}...")
    print(f"  输出路径  : {OUTPUT_PATH}")
    print("-" * 40)

    try:
        client = AgnesVideoClient(api_key=api_key)
        print("客户端初始化成功")

        start = time.time()
        video_url = client.generate_video(
            prompt=PROMPT,
            save_path=OUTPUT_PATH,
            model=MODEL,
            image_path=IMAGE_PATH,
            duration=DURATION,
            aspect_ratio=ASPECT_RATIO,
            mode=MODE,
        )
        elapsed = time.time() - start

        print(f"视频生成完成! 耗时 {elapsed:.1f}s")
        print(f"  远端 URL : {video_url}")
        print(f"  本地文件 : {os.path.abspath(OUTPUT_PATH)}")
        if os.path.exists(OUTPUT_PATH):
            print(f"  文件大小 : {os.path.getsize(OUTPUT_PATH) / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"失败: {e}")
        sys.exit(1)