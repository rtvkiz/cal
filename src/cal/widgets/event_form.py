"""Event form modal for adding/editing events."""

from datetime import date, time

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button, Label
from textual.containers import Vertical, Horizontal
from textual.message import Message

from ..models import Event


class EventForm(ModalScreen):
    """Modal form for creating or editing events."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    class Saved(Message):
        """Message sent when event is saved."""

        def __init__(self, event: Event, is_new: bool) -> None:
            self.event = event
            self.is_new = is_new
            super().__init__()

    class Cancelled(Message):
        """Message sent when form is cancelled."""

        pass

    def __init__(
        self,
        event: Event | None = None,
        default_date: date | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.event = event
        self.is_new = event is None
        self.default_date = default_date or date.today()

    def compose(self) -> ComposeResult:
        title = "Add Event" if self.is_new else "Edit Event"

        with Vertical(id="event-form-container"):
            yield Static(f"  {title}", id="form-title")

            yield Label("Title:")
            yield Input(
                value=self.event.title if self.event else "",
                placeholder="Event title",
                id="title-input",
            )

            yield Label("Date (YYYY-MM-DD):")
            default_date = self.event.date if self.event else self.default_date
            yield Input(
                value=default_date.isoformat(),
                placeholder="2026-01-05",
                id="date-input",
            )

            yield Label("Time (HH:MM, optional):")
            default_time = ""
            if self.event and self.event.time:
                default_time = self.event.time.strftime("%H:%M")
            yield Input(
                value=default_time,
                placeholder="14:00",
                id="time-input",
            )

            yield Label("Description:")
            yield Input(
                value=self.event.description if self.event else "",
                placeholder="Optional description",
                id="desc-input",
            )

            with Horizontal(id="form-buttons"):
                yield Button("Save", variant="primary", id="save-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def _save(self) -> None:
        title = self.query_one("#title-input", Input).value.strip()
        date_str = self.query_one("#date-input", Input).value.strip()
        time_str = self.query_one("#time-input", Input).value.strip()
        desc = self.query_one("#desc-input", Input).value.strip()

        if not title:
            self.notify("Title is required", severity="error")
            return

        try:
            event_date = date.fromisoformat(date_str)
        except ValueError:
            self.notify("Invalid date format. Use YYYY-MM-DD", severity="error")
            return

        event_time = None
        if time_str:
            # Normalize to HH:MM format
            if len(time_str) == 4 and ":" not in time_str:
                time_str = f"{time_str[:2]}:{time_str[2:]}"
            if len(time_str) == 5 and ":" in time_str:
                time_str += ":00"  # Add seconds for fromisoformat
            try:
                event_time = time.fromisoformat(time_str)
            except ValueError:
                self.notify("Invalid time format. Use HH:MM", severity="error")
                return

        if self.event:
            self.event.title = title
            self.event.date = event_date
            self.event.time = event_time
            self.event.description = desc
            event = self.event
        else:
            event = Event(
                title=title,
                date=event_date,
                time=event_time,
                description=desc,
            )

        self.dismiss(event)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ConfirmDialog(ModalScreen):
    """Confirmation dialog."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes (y)", variant="error", id="yes-btn")
                yield Button("No (n)", variant="default", id="no-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.action_confirm()
        else:
            self.action_cancel()

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
