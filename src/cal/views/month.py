"""Month view showing calendar grid."""

from datetime import date

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical
from textual.message import Message

from ..widgets.calendar_grid import CalendarGrid
from ..widgets.historical_event import HistoricalEventWidget


class MonthView(Widget):
    """Month calendar view."""

    class DateSelected(Message):
        """Message when a date is selected in month view."""

        def __init__(self, selected_date: date) -> None:
            self.date = selected_date
            super().__init__()

    def __init__(self, storage=None, holiday_provider=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.storage = storage
        self.holiday_provider = holiday_provider

    def compose(self) -> ComposeResult:
        with Vertical(id="month-view-container"):
            yield Static(id="month-title")
            yield CalendarGrid(
                storage=self.storage,
                holiday_provider=self.holiday_provider,
                id="calendar",
            )
            yield HistoricalEventWidget(id="historical-event")

    def on_mount(self) -> None:
        self._update_title()

    @property
    def calendar(self) -> CalendarGrid:
        return self.query_one("#calendar", CalendarGrid)

    @property
    def selected_date(self) -> date:
        return self.calendar.selected_date

    def _update_title(self) -> None:
        title = self.query_one("#month-title", Static)
        month_name = self.calendar.current_month.strftime("%B %Y")
        title.update(f"  {month_name}")

    def on_calendar_grid_month_changed(self, message: CalendarGrid.MonthChanged) -> None:
        self._update_title()

    def on_calendar_grid_date_selected(self, message: CalendarGrid.DateSelected) -> None:
        self.post_message(self.DateSelected(message.date))

    def next_month(self) -> None:
        self.calendar.next_month()

    def prev_month(self) -> None:
        self.calendar.prev_month()

    def goto_today(self) -> None:
        self.calendar.goto_today()

    def move_selection(self, days: int) -> None:
        self.calendar.move_selection(days)

    def refresh_events(self) -> None:
        self.calendar.refresh_events()
