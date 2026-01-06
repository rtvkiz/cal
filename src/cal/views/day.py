"""Day view showing events for a specific date."""

from datetime import date

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical
from textual.message import Message

from ..models import Event
from ..widgets.event_list import EventList


class DayView(Widget):
    """Day detail view showing events for selected date."""

    class EventSelected(Message):
        """Message when an event is selected."""

        def __init__(self, event: Event) -> None:
            self.event = event
            super().__init__()

    def __init__(self, storage=None, holiday_provider=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.storage = storage
        self.holiday_provider = holiday_provider
        self._current_date = date.today()

    def compose(self) -> ComposeResult:
        with Vertical(id="day-view-container"):
            yield Static(id="day-title")
            yield Static(id="holiday-banner")
            yield EventList(id="day-events")

    def on_mount(self) -> None:
        self._update_display()

    def set_date(self, target_date: date) -> None:
        """Set the date to display."""
        self._current_date = target_date
        self._update_display()

    @property
    def current_date(self) -> date:
        return self._current_date

    def _update_display(self) -> None:
        title = self.query_one("#day-title", Static)
        date_str = self._current_date.strftime("%A, %B %d, %Y")
        title.update(f"  {date_str}")

        # Update holiday banner
        holiday_banner = self.query_one("#holiday-banner", Static)
        holiday_name = None
        if self.holiday_provider:
            holiday_name = self.holiday_provider.get_holiday_name(self._current_date)

        if holiday_name:
            holiday_banner.update(f"  {holiday_name}")
            holiday_banner.display = True
        else:
            holiday_banner.update("")
            holiday_banner.display = False

        events = []
        if self.storage:
            events = self.storage.get_by_date(self._current_date)

        event_list = self.query_one("#day-events", EventList)
        event_list.set_events(events)

    def refresh_events(self) -> None:
        """Refresh the event list."""
        self._update_display()

    def on_event_list_event_selected(self, message: EventList.EventSelected) -> None:
        self.post_message(self.EventSelected(message.event))

    @property
    def selected_event(self) -> Event | None:
        """Get currently selected event."""
        event_list = self.query_one("#day-events", EventList)
        return event_list.selected_event
