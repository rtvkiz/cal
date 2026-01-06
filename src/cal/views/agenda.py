"""Agenda view showing upcoming events."""

from datetime import date

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical
from textual.message import Message

from ..models import Event
from ..widgets.event_list import EventList


class AgendaView(Widget):
    """Agenda view showing upcoming events."""

    class EventSelected(Message):
        """Message when an event is selected."""

        def __init__(self, event: Event) -> None:
            self.event = event
            super().__init__()

    def __init__(self, storage=None, days: int = 30, **kwargs) -> None:
        super().__init__(**kwargs)
        self.storage = storage
        self.days = days

    def compose(self) -> ComposeResult:
        with Vertical(id="agenda-view-container"):
            yield Static(f"  Upcoming Events (Next {self.days} days)", id="agenda-title")
            yield EventList(show_date=True, id="agenda-events")

    def on_mount(self) -> None:
        self._update_display()

    def _update_display(self) -> None:
        events = []
        if self.storage:
            events = self.storage.get_upcoming(date.today(), self.days)

        event_list = self.query_one("#agenda-events", EventList)
        event_list.set_events(events)

    def refresh_events(self) -> None:
        """Refresh the event list."""
        self._update_display()

    def on_event_list_event_selected(self, message: EventList.EventSelected) -> None:
        self.post_message(self.EventSelected(message.event))

    @property
    def selected_event(self) -> Event | None:
        """Get currently selected event."""
        event_list = self.query_one("#agenda-events", EventList)
        return event_list.selected_event
