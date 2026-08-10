import logging
import time
from typing import Dict, Any, Optional

from dokutv.domain.models import Video, PlayHistoryEntry
from dokutv.domain.topics import get_random_topic
from dokutv.application.use_cases import (
    StreamSingleVideoUseCase,
)
from dokutv.adapters import (
    YouTubeCollectorAdapter,
    FFmpegStreamerAdapter,
    TwitchHelixAdapter,
    JsonHistoryStoreAdapter,
)
from dokutv.infrastructure.app_config import AppConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DokuTVEngine")

class DokuTVEngine:
    def __init__(
        self,
        channel_name: str = "DokuTV_EN",
        dry_run: bool = False,
        history_file_path: Optional[str] = None,
    ):
        self.config = AppConfig.from_env(
            channel_name=channel_name,
            dry_run=dry_run,
            history_file_path=history_file_path,
        )
        self.channel_name = self.config.channel_name
        self.dry_run = self.config.dry_run

        # 1. Instantiate Adapters (Layer 3)
        self.collector_adapter = YouTubeCollectorAdapter()
        self.streamer_adapter = FFmpegStreamerAdapter()
        self.twitch_adapter = TwitchHelixAdapter(channel_name=self.channel_name)
        self.history_adapter = JsonHistoryStoreAdapter(file_path=self.config.history_file_path)

        # 2. Inject Adapters into Use Case (Layer 2)
        self.stream_single_video_use_case = StreamSingleVideoUseCase(
            collector_port=self.collector_adapter,
            streamer_port=self.streamer_adapter,
            twitch_port=self.twitch_adapter,
            history_port=self.history_adapter,
        )

        self.is_running = False
        self.current_video: Optional[Video] = None
        self.failed_video_ids: set = set()

    def run_continuous_stream(self, topic: Optional[str] = None, duration_limit: Optional[int] = None) -> None:
        """Run endless streaming loop: start continuous stream -> stream videos seamlessly -> repeat."""
        self.is_running = True
        last_video_id: Optional[str] = None
        next_pre_fetched_video: Optional[Video] = None

        logger.info("Starting DokuTV Engine (Continuous 24/7 Live Stream Loop)...")

        # Start single persistent RTMP connection to Twitch
        self.streamer_adapter.start_persistent_stream()

        try:
            while self.is_running:
                selected_topic = topic or get_random_topic()
                
                exclude_ids = set(self.failed_video_ids)
                if last_video_id:
                    exclude_ids.add(last_video_id)

                logger.info(f"--- New Stream Cycle | Topic: '{selected_topic}' (Exclude IDs count: {len(exclude_ids)}) ---")

                video, pre_fetched = self.stream_single_video_use_case.execute(
                    query=selected_topic,
                    exclude_ids=exclude_ids,
                    duration_limit=duration_limit,
                    current_video=next_pre_fetched_video,
                )

                if video:
                    self.current_video = video
                    last_video_id = video.id
                    next_pre_fetched_video = pre_fetched
                    logger.info(f"Video '{video.title}' finished streaming seamlessly. Proceeding to next video...")
                else:
                    logger.warning("Could not stream selected video. Retrying next candidate...")
                    next_pre_fetched_video = None
                    time.sleep(1)

        except Exception as e:
            logger.error(f"DokuTVEngine encountered error in main loop: {e}")
        finally:
            self.is_running = False
            self.streamer_adapter.stop_persistent_stream()
            logger.info("DokuTVEngine continuous loop stopped.")

    def get_history(self) -> list:
        """Retrieve recorded video play history."""
        return self.history_adapter.get_history()

    def get_status(self) -> Dict[str, Any]:
        return {
            "channel_name": self.channel_name,
            "is_running": self.is_running,
            "dry_run": self.dry_run,
            "current_video": self.current_video.__dict__ if self.current_video else None,
            "streamer_key_set": bool(self.streamer_adapter.stream_key),
            "persistent_stream_active": bool(self.streamer_adapter.persistent_process),
            "history_count": len(self.get_history()),
        }

    def stop(self) -> None:
        logger.info("Stopping DokuTVEngine operations.")
        self.is_running = False
        self.streamer_adapter.stop_persistent_stream()

