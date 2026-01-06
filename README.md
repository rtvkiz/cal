# cal

A terminal calendar app with events and holidays.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

## Features

- **Month view** - Navigate months with keyboard
- **Day view** - See all events for a specific day
- **Agenda view** - Upcoming events for next 30 days
- **Events** - Create, edit, delete events with optional times
- **Holidays** - Shows holidays for your country (configurable)

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/cal.git
cd cal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e .
```

## Usage

```bash
cal
```

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `1` | Month view |
| `2` | Day view |
| `3` | Agenda view |
| `a` | Add event |
| `e` | Edit selected event |
| `x` | Delete selected event |
| `n` | Next month |
| `p` | Previous month |
| `t` | Go to today |
| `Arrow keys` | Navigate calendar |
| `Enter` | Select day |
| `Escape` | Cancel |

### Adding an event

1. Press `a` to open the event form
2. Enter title (required)
3. Enter date in `YYYY-MM-DD` format
4. Enter time in `HH:MM` format (optional)
5. Add description (optional)
6. Press Save or Enter

## Configuration

Config is stored at `~/.cal/config.json`:

```json
{
  "country": "US",
  "subdivision": null,
  "show_holidays": true
}
```

- `country` - Two-letter country code for holidays (US, GB, DE, etc.)
- `subdivision` - State/province code (optional)
- `show_holidays` - Show/hide holidays

## Data storage

Events are saved to `~/.cal/events.json`.

## Requirements

- Python 3.10+
- textual
- python-dateutil
- holidays

## License

MIT
