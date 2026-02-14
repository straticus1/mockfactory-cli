"""Configuration management for MockFactory CLI."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Config(BaseModel):
    """MockFactory CLI configuration."""

    api_url: str = Field(default="https://mockfactory.io")
    timeout: int = Field(default=30, ge=1, le=300)
    session_id: Optional[str] = None

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get the configuration directory path."""
        config_dir = Path.home() / ".mockfactory"
        config_dir.mkdir(exist_ok=True)
        return config_dir

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the configuration file path."""
        return cls.get_config_dir() / "config.json"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
        config_path = cls.get_config_path()
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, ValueError):
                # If config is corrupted, return default
                return cls()
        return cls()

    def save(self) -> None:
        """Save configuration to file."""
        config_path = self.get_config_path()
        with open(config_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)

    def get_token_path(self) -> Path:
        """Get the token file path."""
        return self.get_config_dir() / "token"

    def get_token(self) -> Optional[str]:
        """Get the stored authentication token."""
        token_path = self.get_token_path()
        if token_path.exists():
            try:
                return token_path.read_text().strip()
            except Exception:
                return None
        return None

    def save_token(self, token: str) -> None:
        """Save authentication token securely."""
        token_path = self.get_token_path()
        token_path.write_text(token)
        # Set file permissions to read/write for owner only
        token_path.chmod(0o600)

    def delete_token(self) -> None:
        """Delete the stored authentication token."""
        token_path = self.get_token_path()
        if token_path.exists():
            token_path.unlink()
