"""Calendar grid widget for month view."""

from datetime import date, timedelta
import calendar

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Grid
from textual.reactive import reactive
from textual.message import Message


class DayCell(Static):
    """A single day cell in the calendar grid."""

    class Selected(Message):
        """Message sent when a day is selected."""

        def __init__(self, date: date) -> None:
            self.date = date
            super().__init__()

    def __init__(
        self,
        day: int,
        cell_date: date | None,
        is_today: bool = False,
        is_selected: bool = False,
        has_events: bool = False,
        is_other_month: bool = False,
        is_holiday: bool = False,
    ) -> None:
        super().__init__()
        self.day = day
        self.cell_date = cell_date
        self.is_today = is_today
        self.is_selected = is_selected
        self.has_events = has_events
        self.is_other_month = is_other_month
        self.is_holiday = is_holiday

    def compose(self) -> ComposeResult:
        if self.day == 0:
            yield Static("")
        else:
            indicator = " *" if self.has_events else "  "
            yield Static(f"{self.day:2}{indicator}")

    def on_mount(self) -> None:
        self._update_classes()

    def _update_classes(self) -> None:
        self.remove_class("today", "selected", "has-events", "other-month", "holiday")
        if self.is_today:
            self.add_class("today")
        if self.is_selected:
            self.add_class("selected")
        if self.has_events:
            self.add_class("has-events")
        if self.is_other_month:
            self.add_class("other-month")
        if self.is_holiday:
            self.add_class("holiday")

    def on_click(self) -> None:
        if self.cell_date:
            self.post_message(self.Selected(self.cell_date))


class CalendarGrid(Widget):
    """Monthly calendar grid widget."""

    selected_date: reactive[date] = reactive(date.today)
    current_month: reactive[date] = reactive(date.today().replace(day=1))

    class DateSelected(Message):
        """Message sent when a date is selected."""

        def __init__(self, selected_date: date) -> None:
            self.date = selected_date
            super().__init__()

    class MonthChanged(Message):
        """Message sent when the displayed month changes."""

        def __init__(self, month: date) -> None:
            self.month = month
            super().__init__()

    def __init__(self, storage=None, holiday_provider=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.storage = storage
        self.holiday_provider = holiday_provider
        self._cells: list[DayCell] = []

    def compose(self) -> ComposeResult:
        yield Grid(id="weekday-header")
        yield Grid(id="calendar-grid")

    def on_mount(self) -> None:
        self._build_weekday_header()
        self._rebuild_grid()

    def _build_weekday_header(self) -> None:
        """Build the weekday header row."""
        header = self.query_one("#weekday-header", Grid)
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            header.mount(Static(f"{day:^4}", classes="weekday-cell"))

    def watch_current_month(self, old_month: date, new_month: date) -> None:
        if old_month != new_month:
            self._rebuild_grid()
            self.post_message(self.MonthChanged(new_month))

    def watch_selected_date(self, old_date: date, new_date: date) -> None:
        if old_date != new_date:
            self._update_selection()
            self.post_message(self.DateSelected(new_date))

    def _rebuild_grid(self) -> None:
        """Rebuild the calendar grid for current month."""
        grid = self.query_one("#calendar-grid", Grid)
        grid.remove_children()
        self._cells = []

        today = date.today()
        year = self.current_month.year
        month = self.current_month.month

        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(year, month)

        for week in weeks:
            for day_date in week:
                is_other_month = day_date.month != month
                day_num = day_date.day if not is_other_month else 0

                has_events = False
                if self.storage and not is_other_month:
                    has_events = self.storage.has_events(day_date)

                is_holiday = False
                if self.holiday_provider and not is_other_month:
                    is_holiday = self.holiday_provider.is_holiday(day_date)

                cell = DayCell(
                    day=day_num,
                    cell_date=day_date if not is_other_month else None,
                    is_today=day_date == today and not is_other_month,
                    is_selected=day_date == self.selected_date and not is_other_month,
                    has_events=has_events,
                    is_other_month=is_other_month,
                    is_holiday=is_holiday,
                )
                self._cells.append(cell)
                grid.mount(cell)

    def _update_selection(self) -> None:
        """Update selection highlight without rebuilding grid."""
        for cell in self._cells:
            if cell.cell_date:
                cell.is_selected = cell.cell_date == self.selected_date
                cell._update_classes()

    def on_day_cell_selected(self, message: DayCell.Selected) -> None:
        self.selected_date = message.date

    def next_month(self) -> None:
        """Navigate to next month."""
        year = self.current_month.year
        month = self.current_month.month + 1
        if month > 12:
            month = 1
            year += 1
        self.current_month = date(year, month, 1)

    def prev_month(self) -> None:
        """Navigate to previous month."""
        year = self.current_month.year
        month = self.current_month.month - 1
        if month < 1:
            month = 12
            year -= 1
        self.current_month = date(year, month, 1)

    def goto_today(self) -> None:
        """Navigate to today's date."""
        today = date.today()
        self.current_month = today.replace(day=1)
        self.selected_date = today

    def move_selection(self, days: int) -> None:
        """Move selection by specified number of days."""
        new_date = self.selected_date + timedelta(days=days)
        if new_date.month != self.current_month.month:
            self.current_month = new_date.replace(day=1)
        self.selected_date = new_date

    def refresh_events(self) -> None:
        """Refresh event indicators."""
        self._rebuild_grid()
