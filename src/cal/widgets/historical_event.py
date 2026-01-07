"""Widget to display historical 'On This Day' events."""

from datetime import date

from textual.widgets import Static

from ..historical_events import HistoricalEventsProvider


class HistoricalEventWidget(Static):
    """Displays a historical event for today's date."""

    def __init__(
        self,
        provider: HistoricalEventsProvider | None = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.provider = provider or HistoricalEventsProvider()

    def on_mount(self) -> None:
        """Start loading event in background."""
        self.update("📜 Loading historical event...")
        self.run_worker(self._fetch_event, exclusive=True, thread=True)

    def _fetch_event(self) -> str:
        """Fetch event in background thread."""
        return self.provider.get_event_for_display(date.today())

    def on_worker_state_changed(self, event) -> None:
        """Handle worker completion."""
        if event.worker.name == "_fetch_event" and event.worker.is_finished:
            if event.worker.result:
                self.update(f"📜 {event.worker.result}")
