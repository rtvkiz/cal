"""Holiday data provider using the holidays library."""

from datetime import date
from typing import Optional

import holidays

from .config import Config


class HolidayProvider:
    """Provides holiday data for configured country/region."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize with configuration."""
        self.config = config or Config()
        self._holidays_cache: dict[int, holidays.HolidayBase] = {}

    def _get_holidays_for_year(self, year: int) -> holidays.HolidayBase:
        """Get or create holidays instance for a year."""
        if year not in self._holidays_cache:
            try:
                country = self.config.country
                subdiv = self.config.subdivision
                self._holidays_cache[year] = holidays.country_holidays(
                    country,
                    subdiv=subdiv,
                    years=year,
                )
            except (KeyError, NotImplementedError):
                # Fallback to US if country not supported
                self._holidays_cache[year] = holidays.country_holidays(
                    "US",
                    years=year,
                )
        return self._holidays_cache[year]

    def is_holiday(self, target_date: date) -> bool:
        """Check if a date is a holiday."""
        if not self.config.show_holidays:
            return False
        holiday_cal = self._get_holidays_for_year(target_date.year)
        return target_date in holiday_cal

    def get_holiday_name(self, target_date: date) -> Optional[str]:
        """Get the holiday name for a date, or None if not a holiday."""
        if not self.config.show_holidays:
            return None
        holiday_cal = self._get_holidays_for_year(target_date.year)
        return holiday_cal.get(target_date)

    def get_holidays_in_month(self, year: int, month: int) -> dict[date, str]:
        """Get all holidays in a specific month."""
        if not self.config.show_holidays:
            return {}

        holiday_cal = self._get_holidays_for_year(year)
        result = {}
        for holiday_date, name in holiday_cal.items():
            if holiday_date.year == year and holiday_date.month == month:
                result[holiday_date] = name
        return result

    def clear_cache(self) -> None:
        """Clear the holidays cache (call after config changes)."""
        self._holidays_cache.clear()

    @staticmethod
    def get_supported_countries() -> list[str]:
        """Get list of supported country codes."""
        return sorted(holidays.list_supported_countries().keys())

    @staticmethod
    def get_subdivisions(country: str) -> list[str]:
        """Get list of subdivisions for a country."""
        try:
            return sorted(holidays.list_supported_countries().get(country, []))
        except (KeyError, TypeError):
            return []
