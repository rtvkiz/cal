"""User configuration management for calendar app."""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Config:
    """Manages user configuration settings."""

    def __init__(self, path: Optional[Path] = None):
        """Initialize config with file path."""
        if path is None:
            path = Path.home() / ".cal" / "config.json"
        self.path = path
        self._config: dict = {}
        self._load()

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "country": "US",
            "subdivision": None,
            "show_holidays": True,
        }

    def _load(self) -> None:
        """Load configuration from JSON file."""
        if not self.path.exists():
            self._config = self._default_config()
            self._save()
            return

        try:
            with open(self.path, "r") as f:
                self._config = json.load(f)
            # Merge with defaults for any missing keys
            for key, value in self._default_config().items():
                if key not in self._config:
                    self._config[key] = value
        except json.JSONDecodeError as e:
            logger.warning(f"Config file corrupted, using defaults: {e}")
            self._config = self._default_config()

    def _save(self) -> None:
        """Save configuration to JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self._config, f, indent=2)

    @property
    def country(self) -> str:
        """Get configured country code."""
        return self._config.get("country", "US")

    @country.setter
    def country(self, value: str) -> None:
        """Set country code."""
        self._config["country"] = value
        self._save()

    @property
    def subdivision(self) -> Optional[str]:
        """Get configured subdivision/state code."""
        return self._config.get("subdivision")

    @subdivision.setter
    def subdivision(self, value: Optional[str]) -> None:
        """Set subdivision/state code."""
        self._config["subdivision"] = value
        self._save()

    @property
    def show_holidays(self) -> bool:
        """Get whether to show holidays."""
        return self._config.get("show_holidays", True)

    @show_holidays.setter
    def show_holidays(self, value: bool) -> None:
        """Set whether to show holidays."""
        self._config["show_holidays"] = value
        self._save()
