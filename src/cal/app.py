"""Main calendar TUI application."""

from datetime import date
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Static, Footer, Header
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

from .storage import EventStorage
from .config import Config
from .holidays_provider import HolidayProvider
from .models import Event
from .views.month import MonthView
from .views.day import DayView
from .views.agenda import AgendaView
from .widgets.event_form import EventForm, ConfirmDialog


class CalendarApp(App):
    """Terminal calendar application."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "view_month", "Month"),
        Binding("2", "view_day", "Day"),
        Binding("3", "view_agenda", "Agenda"),
        Binding("a", "add_event", "Add"),
        Binding("e", "edit_event", "Edit"),
        Binding("x", "delete_event", "Delete"),
        Binding("n", "next_month", "Next"),
        Binding("p", "prev_month", "Prev"),
        Binding("t", "goto_today", "Today"),
        Binding("left", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("enter", "select_day", "Select", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.storage = EventStorage()
        self.config = Config()
        self.holiday_provider = HolidayProvider(self.config)
        self._current_view = "month"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main-container"):
            with Horizontal(id="view-tabs"):
                yield Static("1: Month", id="tab-month", classes="tab active")
                yield Static("2: Day", id="tab-day", classes="tab")
                yield Static("3: Agenda", id="tab-agenda", classes="tab")
            with Vertical(id="views-container"):
                yield MonthView(
                    storage=self.storage,
                    holiday_provider=self.holiday_provider,
                    id="month-view",
                )
                yield DayView(
                    storage=self.storage,
                    holiday_provider=self.holiday_provider,
                    id="day-view",
                )
                yield AgendaView(storage=self.storage, id="agenda-view")
        yield Footer()

    def on_mount(self) -> None:
        self._show_view("month")

    def _show_view(self, view_name: str) -> None:
        """Switch to the specified view."""
        self._current_view = view_name

        month_view = self.query_one("#month-view", MonthView)
        day_view = self.query_one("#day-view", DayView)
        agenda_view = self.query_one("#agenda-view", AgendaView)

        month_view.display = view_name == "month"
        day_view.display = view_name == "day"
        agenda_view.display = view_name == "agenda"

        for tab in self.query(".tab"):
            tab.remove_class("active")

        tab_id = f"tab-{view_name}"
        self.query_one(f"#{tab_id}").add_class("active")

        if view_name == "day":
            day_view.set_date(month_view.selected_date)

    def _refresh_all_views(self) -> None:
        """Refresh all views after event changes."""
        self.query_one("#month-view", MonthView).refresh_events()
        self.query_one("#day-view", DayView).refresh_events()
        self.query_one("#agenda-view", AgendaView).refresh_events()

    def action_view_month(self) -> None:
        self._show_view("month")

    def action_view_day(self) -> None:
        self._show_view("day")

    def action_view_agenda(self) -> None:
        self._show_view("agenda")

    def action_next_month(self) -> None:
        if self._current_view == "month":
            self.query_one("#month-view", MonthView).next_month()

    def action_prev_month(self) -> None:
        if self._current_view == "month":
            self.query_one("#month-view", MonthView).prev_month()

    def action_goto_today(self) -> None:
        if self._current_view == "month":
            self.query_one("#month-view", MonthView).goto_today()

    def action_move_left(self) -> None:
        if self._current_view == "month":
            self.query_one("#month-view", MonthView).move_selection(-1)

    def action_move_right(self) -> None:
        if self._current_view == "month":
            self.query_one("#month-view", MonthView).move_selection(1)

    def action_move_up(self) -> None:
        if self._current_view == "month":
            self.query_one("#month-view", MonthView).move_selection(-7)

    def action_move_down(self) -> None:
        if self._current_view == "month":
            self.query_one("#month-view", MonthView).move_selection(7)

    def action_select_day(self) -> None:
        if self._current_view == "month":
            self._show_view("day")

    def action_add_event(self) -> None:
        default_date = date.today()
        if self._current_view == "month":
            default_date = self.query_one("#month-view", MonthView).selected_date
        elif self._current_view == "day":
            default_date = self.query_one("#day-view", DayView).current_date

        def on_save(event: Event | None) -> None:
            if event:
                self.storage.add(event)
                self._refresh_all_views()
                self.notify(f"Added: {event.title}")

        self.push_screen(EventForm(default_date=default_date), on_save)

    def action_edit_event(self) -> None:
        event = self._get_selected_event()
        if not event:
            self.notify("No event selected", severity="warning")
            return

        def on_save(updated_event: Event | None) -> None:
            if updated_event:
                self.storage.update(updated_event)
                self._refresh_all_views()
                self.notify(f"Updated: {updated_event.title}")

        self.push_screen(EventForm(event=event), on_save)

    def action_delete_event(self) -> None:
        event = self._get_selected_event()
        if not event:
            self.notify("No event selected", severity="warning")
            return

        def on_confirm(confirmed: bool) -> None:
            if confirmed:
                self.storage.delete(event.id)
                self._refresh_all_views()
                self.notify(f"Deleted: {event.title}")

        self.push_screen(
            ConfirmDialog(f"Delete '{event.title}'?"),
            on_confirm,
        )

    def _get_selected_event(self) -> Event | None:
        """Get the currently selected event based on current view."""
        if self._current_view == "day":
            return self.query_one("#day-view", DayView).selected_event
        elif self._current_view == "agenda":
            return self.query_one("#agenda-view", AgendaView).selected_event
        return None

    def on_month_view_date_selected(self, message: MonthView.DateSelected) -> None:
        self.query_one("#day-view", DayView).set_date(message.date)


def main() -> None:
    """Entry point for the calendar application."""
    app = CalendarApp()
    app.run()


if __name__ == "__main__":
    main()
