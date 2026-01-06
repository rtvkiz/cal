"""JSON file storage for calendar events."""

import json
import logging
from pathlib import Path
from datetime import date
from typing import Optional

from .models import Event

logger = logging.getLogger(__name__)


class EventStorage:
    """Handles loading and saving events to JSON file."""

    def __init__(self, path: Optional[Path] = None):
        """Initialize storage with file path."""
        if path is None:
            path = Path.home() / ".cal" / "events.json"
        self.path = path
        self._events: dict[str, Event] = {}
        self._load()

    def _load(self) -> None:
        """Load events from JSON file."""
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._save()
            return

        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            for event_data in data.get("events", []):
                try:
                    event = Event.from_dict(event_data)
                    self._events[event.id] = event
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid event: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted events file, starting fresh: {e}")
            self._events = {}

    def _save(self) -> None:
        """Save events to JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"events": [e.to_dict() for e in self._events.values()]}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, event: Event) -> None:
        """Add a new event."""
        self._events[event.id] = event
        self._save()

    def update(self, event: Event) -> None:
        """Update an existing event."""
        if event.id in self._events:
            self._events[event.id] = event
            self._save()

    def delete(self, event_id: str) -> None:
        """Delete an event by ID."""
        if event_id in self._events:
            del self._events[event_id]
            self._save()

    def get(self, event_id: str) -> Optional[Event]:
        """Get an event by ID."""
        return self._events.get(event_id)

    def get_all(self) -> list[Event]:
        """Get all events sorted by date and time."""
        return sorted(self._events.values(), key=lambda e: e.sort_key)

    def get_by_date(self, target_date: date) -> list[Event]:
        """Get all events for a specific date."""
        events = [e for e in self._events.values() if e.date == target_date]
        return sorted(events, key=lambda e: e.sort_key)

    def get_upcoming(self, from_date: date, days: int = 30) -> list[Event]:
        """Get upcoming events within specified days."""
        from datetime import timedelta

        end_date = from_date + timedelta(days=days)
        events = [
            e for e in self._events.values() if from_date <= e.date <= end_date
        ]
        return sorted(events, key=lambda e: e.sort_key)

    def has_events(self, target_date: date) -> bool:
        """Check if a date has any events."""
        return any(e.date == target_date for e in self._events.values())
