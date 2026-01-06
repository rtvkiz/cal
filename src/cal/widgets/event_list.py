"""Event list widget for displaying events."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, ListItem, ListView
from textual.message import Message

from ..models import Event


class EventItem(ListItem):
    """A single event item in the list."""

    def __init__(self, event: Event, show_date: bool = False) -> None:
        super().__init__()
        self.event = event
        self.show_date = show_date

    def compose(self) -> ComposeResult:
        time_str = self.event.display_time
        if self.show_date:
            date_str = self.event.date.strftime("%a %d %b")
            yield Static(f"{date_str}  {time_str}  {self.event.title}", classes="event-title")
        else:
            yield Static(f"{time_str}  {self.event.title}", classes="event-title")

        if self.event.description:
            desc = self.event.description
            if len(desc) > 50:
                desc = desc[:47] + "..."
            yield Static(f"  {desc}", classes="event-desc")


class EventList(Widget):
    """Widget for displaying a list of events."""

    class EventSelected(Message):
        """Message when an event is selected."""

        def __init__(self, event: Event) -> None:
            self.event = event
            super().__init__()

    def __init__(self, events: list[Event] | None = None, show_date: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._events = events or []
        self.show_date = show_date

    def compose(self) -> ComposeResult:
        yield ListView(id="event-listview")

    def on_mount(self) -> None:
        self._rebuild_list()

    def _rebuild_list(self) -> None:
        listview = self.query_one("#event-listview", ListView)
        listview.clear()

        if not self._events:
            listview.mount(ListItem(Static("No events")))
            return

        for event in self._events:
            listview.mount(EventItem(event, show_date=self.show_date))

    def set_events(self, events: list[Event]) -> None:
        """Update the displayed events."""
        self._events = events
        self._rebuild_list()

    def on_list_view_selected(self, message: ListView.Selected) -> None:
        if isinstance(message.item, EventItem):
            self.post_message(self.EventSelected(message.item.event))

    @property
    def selected_event(self) -> Event | None:
        """Get the currently selected event."""
        listview = self.query_one("#event-listview", ListView)
        if listview.highlighted_child and isinstance(listview.highlighted_child, EventItem):
            return listview.highlighted_child.event
        return None
