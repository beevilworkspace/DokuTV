"""
Infrastructure Layer - Environment Variable & Framework Configuration.
Re-exports load_env from env_loader for backward compatibility.
"""

from dokutv.infrastructure.env_loader import load_env, EnvironmentLoader

__all__ = ["load_env", "EnvironmentLoader"]
