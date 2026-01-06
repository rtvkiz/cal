"""Event data model."""

from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional
import uuid


@dataclass
class Event:
    """Calendar event."""

    title: str
    date: date
    time: Optional[time] = None
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        """Validate event data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Event title cannot be empty")
        self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()

    def to_dict(self) -> dict:
        """Convert event to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date.isoformat(),
            "time": self.time.isoformat() if self.time else None,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """Create event from dictionary."""
        required = ["id", "title", "date"]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return cls(
            id=data["id"],
            title=data["title"],
            date=date.fromisoformat(data["date"]),
            time=time.fromisoformat(data["time"]) if data.get("time") else None,
            description=data.get("description", ""),
        )

    @property
    def display_time(self) -> str:
        """Get formatted time string for display."""
        if self.time:
            return self.time.strftime("%H:%M")
        return "All day"

    @property
    def sort_key(self) -> tuple:
        """Key for sorting events by date and time."""
        return (self.date, self.time or time(0, 0))
