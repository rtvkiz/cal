"""Historical events provider using Wikipedia's On This Day API."""

import random
from datetime import date
from typing import Optional
import urllib.request
import json


class HistoricalEventsProvider:
    """Provides historical 'On This Day' events from Wikipedia."""

    API_URL = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/{month}/{day}"

    def __init__(self):
        self._cache: dict[tuple[int, int], list[dict]] = {}

    def _fetch_events(self, month: int, day: int) -> list[dict]:
        """Fetch events from Wikipedia API."""
        if (month, day) in self._cache:
            return self._cache[(month, day)]

        try:
            url = self.API_URL.format(month=month, day=day)
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "CalendarTUI/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                events = data.get("events", [])
                self._cache[(month, day)] = events
                return events
        except Exception:
            return []

    def get_random_event(self, target_date: date) -> Optional[str]:
        """Get a random historical event for the given date."""
        events = self._fetch_events(target_date.month, target_date.day)
        if not events:
            return None

        event = random.choice(events)
        year = event.get("year", "")
        text = event.get("text", "")
        if year and text:
            return f"{year}: {text}"
        return text or None

    def get_event_for_display(self, target_date: date) -> str:
        """Get a formatted event string for display."""
        event = self.get_random_event(target_date)
        if event:
            return f"On this day: {event}"
        return "On this day: No historical events found"
