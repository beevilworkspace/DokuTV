"""
Infrastructure Layer - Environment Variable & Framework Configuration.
"""

import os
from dotenv import load_dotenv

def load_env() -> None:
    """Framework / Infrastructure helper to load environment variables."""
    if os.path.exists(".env"):
        load_dotenv(".env", override=True)
    elif os.path.exists(".env.example"):
        load_dotenv(".env.example", override=True)

