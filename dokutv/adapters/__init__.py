"""
Interface Adapters Package
"""

from dokutv.adapters.youtube_collector import (
    YouTubeCollectorAdapter,
    YouTubeCollectorConfig,
    FallbackPlaylistStore,
    YouTubeApiClient,
)
from dokutv.adapters.ffmpeg_streamer import FFmpegStreamerAdapter
from dokutv.adapters.twitch_bot import (
    TwitchHelixAdapter,
    TwitchHelixConfig,
    TwitchTitleFormatter,
    TwitchHelixClient,
)
from dokutv.adapters.twitch_auth import (
    TwitchAuthManager,
    TwitchTokens,
    TwitchAuthConfig,
    TwitchTokenStore,
    TwitchOAuthClient,
    OAuthCallbackServer,
    BrowserLauncher,
)
from dokutv.adapters.history_store import JsonHistoryStoreAdapter
from dokutv.adapters.web_dashboard import WebDashboardAdapter
from dokutv.adapters.streaming import (
    StreamingConfig,
    StreamingTarget,
    TwitchTarget,
    CustomRtmpTarget,
    FFmpegBinaryLocator,
    CookieProvider,
    YoutubeUrlResolver,
    FFmpegCommandBuilder,
    PersistentStreamSession,
    StreamResult,
    ResolvedStream,
)

__all__ = [
    "YouTubeCollectorAdapter",
    "YouTubeCollectorConfig",
    "FallbackPlaylistStore",
    "YouTubeApiClient",
    "FFmpegStreamerAdapter",
    "TwitchHelixAdapter",
    "TwitchHelixConfig",
    "TwitchTitleFormatter",
    "TwitchHelixClient",
    "TwitchAuthManager",
    "TwitchTokens",
    "TwitchAuthConfig",
    "TwitchTokenStore",
    "TwitchOAuthClient",
    "OAuthCallbackServer",
    "BrowserLauncher",
    "JsonHistoryStoreAdapter",
    "WebDashboardAdapter",
    "StreamingConfig",
    "StreamingTarget",
    "TwitchTarget",
    "CustomRtmpTarget",
    "FFmpegBinaryLocator",
    "CookieProvider",
    "YoutubeUrlResolver",
    "FFmpegCommandBuilder",
    "PersistentStreamSession",
    "StreamResult",
    "ResolvedStream",
]


