"""
Infrastructure Layer - Environment Variable Loader.
Manages reading .env files using python-dotenv with fallback resolution.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class EnvironmentLoader:
    """Service for loading environment variables into os.environ."""

    def __init__(self, default_file: str = ".env", fallback_file: str = ".env.example"):
        self.default_file = Path(default_file)
        self.fallback_file = Path(fallback_file)

    def load(self, env_file: Optional[Path] = None, override: bool = True) -> bool:
        """Load environment variables from given path, default .env, or fallback file."""
        target_file = env_file or self.default_file

        if target_file.exists():
            load_dotenv(target_file, override=override)
            logger.info(f"Loaded environment variables from '{target_file}'.")
            return True

        if self.fallback_file.exists():
            load_dotenv(self.fallback_file, override=override)
            logger.info(f"Loaded fallback environment variables from '{self.fallback_file}'.")
            return True

        logger.debug("No .env or .env.example file found. Relying on system environment variables.")
        return False


_DEFAULT_LOADER = EnvironmentLoader()


def load_env(env_file: Optional[Path] = None, override: bool = True) -> None:
    """Helper function to load environment variables into os.environ."""
    _DEFAULT_LOADER.load(env_file=env_file, override=override)
