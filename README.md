# DokuTV 24/7 Streaming Engine (Clean Architecture)

DokuTV_EN is a 24/7 continuous live streaming system that searches for high-quality Creative Commons & Public Domain documentaries on YouTube, generates a continuous 30-day schedule, and streams RTMP live to Twitch using FFmpeg.

## Architecture Overview

This codebase is built 100% according to Robert C. Martin's **Clean Architecture** principles and the Dependency Rule (dependencies point strictly inward):

```
DokuTV/
├── dokutv/                      # Main Clean Architecture Package
│   ├── domain/                  # Layer 1: Entities (Pure Business Objects)
│   │   ├── models.py            # Video, PlaySlot, ChannelSchedule
│   │   └── __init__.py
│   │
│   ├── application/             # Layer 2: Application Use Cases & Ports
│   │   ├── ports.py             # Abstract Protocols (DIP interfaces)
│   │   ├── use_cases.py         # DiscoverContent, PlanSchedule, StreamCurrentSlot
│   │   └── __init__.py
│   │
│   ├── adapters/                # Layer 3: Interface Adapters (Gateways)
│   │   ├── youtube_collector.py # Implements ContentCollectorPort
│   │   ├── schedule_repository.py# Implements ScheduleRepositoryPort
│   │   ├── ffmpeg_streamer.py   # Implements StreamerPort
│   │   ├── twitch_bot.py        # Implements TwitchPort
│   │   └── __init__.py
│   │
│   ├── infrastructure/          # Layer 4: Frameworks & Drivers
│   │   ├── env_config.py        # Dotenv & Environment variable loader
│   │   └── __init__.py
│   │
│   ├── engine.py                # Composition Root & Dependency Injection
│   └── __init__.py
│
├── main.py                      # Clean Entry Point
├── tests/                       # Automated Unit Test Suite
├── data/                        # Playlist & Schedule JSON cache
└── clean-architecture-skills/   # Native Antigravity Agent Skills
```

## Getting Started

### 1. Requirements
- Python 3.9+
- `ffmpeg` installed on system (or `pip install imageio-ffmpeg yt-dlp`)

### 2. Configuration
Copy `.env.example` to `.env` and set your credentials:
```env
YOUTUBE_API_KEY=AIzaSy...
TWITCH_STREAM_KEY=live_...
TWITCH_CLIENT_ID=...
TWITCH_CLIENT_SECRET=...
```

### 3. Run Streaming Engine
```bash
python main.py
```

### 4. Run Test Suite
```bash
python -m unittest discover tests
```
