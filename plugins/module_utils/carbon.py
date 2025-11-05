import sys
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

class Carbon(datetime):
    """
    A Python implementation of many of PHP Carbon's features,
    built on top of datetime and relativedelta.
    """

    # --- Constants (matching PHP Carbon formats) ---
    ATOM = '%Y-%m-%dT%H:%M:%S%z'
    COOKIE = '%A, %d-%b-%Y %H:%M:%S %Z'
    ISO8601 = '%Y-%m-%dT%H:%M:%S%z'
    ISO8601_Z = '%Y-%m-%dT%H:%M:%S%z' # Alias
    RFC822 = '%a, %d %b %y %H:%M:%S %z'
    RFC850 = '%A, %d-%b-%y %H:%M:%S %Z'
    RFC1036 = '%a, %d %b %y %H:%M:%S %z'
    RFC1123 = '%a, %d %b %Y %H:%M:%S %z'
    RFC2822 = '%a, %d %b %Y %H:%M:%S %z'
    RFC3339 = '%Y-%m-%dT%H:%M:%S%z'
    RFC3339_EXTENDED = '%Y-%m-%dT%H:%M:%S.%f%z'
    RSS = '%a, %d %b %Y %H:%M:%S %z'
    W3C = '%Y-%m-%dT%H:%M:%S%z'
    ASN1 = '%Y%m%d%H%M%SZ'

    # --- Helper Methods ---

    def _to_carbon(self, dt):
        """Internal helper to convert a datetime back to a Carbon instance."""
        if not isinstance(dt, datetime):
            return dt
        return self.__class__.from_datetime(dt)

    def _ensure_carbon(self, dt):
        """Internal helper to ensure an object is a Carbon instance for comparison."""
        if isinstance(dt, Carbon):
            return dt
        if isinstance(dt, datetime):
            return self.__class__.from_datetime(dt)
        try:
            # Basic parse attempt for strings
            return self.__class__.parse(str(dt))
        except Exception:
            raise TypeError(
                f"Cannot compare Carbon with type {type(dt)}. "
                "Must be datetime, Carbon, or a parsable string."
            )

    # --- Overridden Methods to Return Carbon ---

    def __add__(self, other):
        """Ensure additions with timedelta/relativedelta return Carbon."""
        if isinstance(other, (timedelta, relativedelta)):
            return self._to_carbon(super().__add__(other))
        return NotImplemented

    def __sub__(self, other):
        """Ensure subtractions with timedelta/relativedelta return Carbon."""
        if isinstance(other, (timedelta, relativedelta)):
            return self._to_carbon(super().__sub__(other))
        # Allow diffing between two datetimes
        if isinstance(other, datetime):
            return super().__sub__(other) # This returns a timedelta
        return NotImplemented

    def replace(self, *args, **kwargs):
        """Override replace to return a Carbon instance."""
        return self._to_carbon(super().replace(*args, **kwargs))

    def astimezone(self, tz=None):
        """Override astimezone to return a Carbon instance."""
        return self._to_carbon(super().astimezone(tz))

    # --- Rich Comparison Overrides ---

    def __eq__(self, other):
        if not isinstance(other, datetime):
            try: other = self._ensure_carbon(other)
            except TypeError: return NotImplemented
        return super().__eq__(other)

    def __ne__(self, other):
        if not isinstance(other, datetime):
            try: other = self._ensure_carbon(other)
            except TypeError: return NotImplemented
        return super().__ne__(other)

    def __lt__(self, other):
        if not isinstance(other, datetime):
            try: other = self._ensure_carbon(other)
            except TypeError: return NotImplemented
        return super().__lt__(other)

    def __le__(self, other):
        if not isinstance(other, datetime):
            try: other = self._ensure_carbon(other)
            except TypeError: return NotImplemented
        return super().__le__(other)

    def __gt__(self, other):
        if not isinstance(other, datetime):
            try: other = self._ensure_carbon(other)
            except TypeError: return NotImplemented
        return super().__gt__(other)

    def __ge__(self, other):
        if not isinstance(other, datetime):
            try: other = self._ensure_carbon(other)
            except TypeError: return NotImplemented
        return super().__ge__(other)

    # --- String Formatting ---

    def __str__(self):
        """Default string representation (YYYY-MM-DD HH:MM:SS)."""
        return self.to_date_time_string()

    def __repr__(self):
        """Official representation."""
        return f"<Carbon [{self.isoformat()}]>"

    def format(self, fmt):
        """Format the datetime using strftime."""
        return self.strftime(fmt)

    def to_date_string(self):
        """Format as YYYY-MM-DD."""
        return self.format('%Y-%m-%d')

    def to_time_string(self):
        """Format as HH:MM:SS."""
        return self.format('%H:%M:%S')

    def to_date_time_string(self):
        """Format as YYYY-MM-DD HH:MM:SS."""
        return self.format('%Y-%m-%d %H:%M:%S')

    def to_iso8601_string(self):
        """Format as ISO 8601 string."""
        return self.isoformat()
    
    def for_database(self):
        """Format as YYYY-MM-DD HH:MM:SS. Alias for to_date_time_string."""
        return self.to_date_time_string()

    # --- Instantiation (Class Methods) ---

    @classmethod
    def now(cls, tz=None):
        """Get the current time as a Carbon instance."""
        return cls.from_datetime(datetime.now(tz))

    @classmethod
    def utcnow(cls):
        """Get the current UTC time as a Carbon instance."""
        return cls.now(timezone.utc)

    @classmethod
    def today(cls, tz=None):
        """Get the start of today."""
        return cls.now(tz).start_of_day()

    @classmethod
    def tomorrow(cls, tz=None):
        """Get the start of tomorrow."""
        return cls.now(tz).add_days(1).start_of_day()

    @classmethod
    def yesterday(cls, tz=None):
        """Get the start of yesterday."""
        return cls.now(tz).sub_days(1).start_of_day()

    @classmethod
    def create(cls, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        """Create a new Carbon instance from specified components."""
        return cls(year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo)

    @classmethod
    def create_from_format(cls, fmt, time_str, tz=None):
        """Parse a string with a specific format, returning Carbon."""
        dt = datetime.strptime(time_str, fmt)
        if tz:
            dt = dt.replace(tzinfo=tz)
        return cls.from_datetime(dt)

    @classmethod
    def from_datetime(cls, dt):
        """Create a Carbon instance from an existing datetime object."""
        if isinstance(dt, cls):
            return dt
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                   dt.second, dt.microsecond, dt.tzinfo)

    @classmethod
    def from_timestamp(cls, timestamp, tz=None):
        """Create a Carbon instance from a UNIX timestamp."""
        dt = datetime.fromtimestamp(timestamp, tz)
        return cls.from_datetime(dt)

    @classmethod
    def parse(cls, time_str, tz=None):
        """
        Attempt to parse a datetime string.
        NOTE: This is heavily limited without dateutil.parser.
        It primarily supports ISO 8601 formats.
        """
        if isinstance(time_str, datetime):
            return cls.from_datetime(time_str)
            
        try:
            # datetime.fromisoformat() is quite strict.
            # It requires T separator and doesn't handle spaces.
            time_str_std = time_str.replace(' ', 'T')
            dt = datetime.fromisoformat(time_str_std)
            if tz and dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            elif tz and dt.tzinfo is not None:
                dt = dt.astimezone(tz)
            return cls.from_datetime(dt)
        except ValueError as e:
            raise ValueError(
                f"Could not parse '{time_str}' with basic ISO parser. "
                "For more flexible parsing, use `create_from_format()` "
                "or install `dateutil.parser`."
            ) from e

    # --- Additions ---

    def add(self, *args, **kwargs):
        """
        Add a timedelta or relativedelta.
        Accepts kwargs like years=1, months=2, days=3, etc.
        """
        if args and isinstance(args[0], timedelta):
            return self._to_carbon(super().__add__(args[0]))
        return self._to_carbon(super().__add__(relativedelta(**kwargs)))

    def add_years(self, value=1):
        return self.add(years=value)

    def add_months(self, value=1):
        return self.add(months=value)

    def add_weeks(self, value=1):
        return self.add(weeks=value)

    def add_days(self, value=1):
        return self.add(days=value)

    def add_hours(self, value=1):
        return self.add(hours=value)

    def add_minutes(self, value=1):
        return self.add(minutes=value)

    def add_seconds(self, value=1):
        return self.add(seconds=value)

    # --- Subtractions ---

    def sub(self, *args, **kwargs):
        """
        Subtract a timedelta or relativedelta.
        Accepts kwargs like years=1, months=2, days=3, etc.
        """
        if args and isinstance(args[0], timedelta):
            return self._to_carbon(super().__sub__(args[0]))
        return self._to_carbon(super().__sub__(relativedelta(**kwargs)))

    def sub_years(self, value=1):
        return self.sub(years=value)

    def sub_months(self, value=1):
        return self.sub(months=value)

    def sub_weeks(self, value=1):
        return self.sub(weeks=value)

    def sub_days(self, value=1):
        return self.sub(days=value)

    def sub_hours(self, value=1):
        return self.sub(hours=value)

    def sub_minutes(self, value=1):
        return self.sub(minutes=value)

    def sub_seconds(self, value=1):
        return self.sub(seconds=value)

    # --- Modifiers ("Start of" / "End of") ---

    def start_of_day(self):
        """Reset time to 00:00:00.000000."""
        return self.replace(hour=0, minute=0, second=0, microsecond=0)

    def end_of_day(self):
        """Set time to 23:59:59.999999."""
        return self.replace(hour=23, minute=59, second=59, microsecond=999999)

    def start_of_month(self):
        """Set to the first day of the month at 00:00:00."""
        return self.replace(day=1).start_of_day()

    def end_of_month(self):
        """Set to the last day of the month at 23:59:59."""
        # Add 1 month, go to start of that month, then subtract 1 day
        return self.replace(day=1).add_months(1).sub_days(1).end_of_day()

    def start_of_year(self):
        """Set to the first day of the year at 00:00:00."""
        return self.replace(month=1, day=1).start_of_day()

    def end_of_year(self):
        """Set to the last day of the year at 23:59:59."""
        return self.replace(month=12, day=31).end_of_day()

    def start_of_week(self, week_starts_at=0):
        """
        Set to the start of the week.
        :param week_starts_at: 0=Monday, 6=Sunday
        """
        days_to_subtract = self.weekday() - week_starts_at
        if days_to_subtract < 0:
            days_to_subtract += 7
        return self.sub_days(days_to_subtract).start_of_day()

    def end_of_week(self, week_starts_at=0):
        """
        Set to the end of the week.
        :param week_starts_at: 0=Monday, 6=Sunday
        """
        end_day = (week_starts_at - 1 + 7) % 7 # If starts at 0 (Mon), ends at 6 (Sun)
        days_to_add = end_day - self.weekday()
        if days_to_add < 0:
            days_to_add += 7
        return self.add_days(days_to_add).end_of_day()

    # --- Differences ---

    def diff(self, other=None, abs_val=True):
        """Get the relativedelta difference between this and another date."""
        if other is None:
            other = self.now(self.tzinfo)
        other = self._ensure_carbon(other)

        rd = relativedelta(self, other)
        
        if abs_val:
            # Create a new relativedelta with absolute values
            return relativedelta(
                years=abs(rd.years),
                months=abs(rd.months),
                days=abs(rd.days),
                hours=abs(rd.hours),
                minutes=abs(rd.minutes),
                seconds=abs(rd.seconds),
                microseconds=abs(rd.microseconds)
            )
        return rd

    def diff_in_years(self, other=None, abs_val=True):
        """Get the difference in (contextual) years."""
        return self.diff(other, abs_val).years

    def diff_in_months(self, other=None, abs_val=True):
        """Get the total difference in months."""
        if other is None:
            other = self.now(self.tzinfo)
        other = self._ensure_carbon(other)
        
        rd = relativedelta(self, other)
        total_months = rd.years * 12 + rd.months
        return abs(total_months) if abs_val else total_months

    def _get_total_seconds_diff(self, other=None):
        """Helper for total time diffs."""
        if other is None:
            other = self.now(self.tzinfo)
        other = self._ensure_carbon(other)
        
        # Use standard timedelta subtraction for a flat total
        td = self - other
        return td.total_seconds()

    def diff_in_days(self, other=None, abs_val=True):
        """Get the total difference in days."""
        total_seconds = self._get_total_seconds_diff(other)
        diff = total_seconds / 86400  # 60 * 60 * 24
        return abs(int(diff)) if abs_val else int(diff)

    def diff_in_hours(self, other=None, abs_val=True):
        """Get the total difference in hours."""
        total_seconds = self._get_total_seconds_diff(other)
        diff = total_seconds / 3600 # 60 * 60
        return abs(int(diff)) if abs_val else int(diff)

    def diff_in_minutes(self, other=None, abs_val=True):
        """Get the total difference in minutes."""
        total_seconds = self._get_total_seconds_diff(other)
        diff = total_seconds / 60
        return abs(int(diff)) if abs_val else int(diff)

    def diff_in_seconds(self, other=None, abs_val=True):
        """Get the total difference in seconds."""
        total_seconds = self._get_total_seconds_diff(other)
        return abs(int(total_seconds)) if abs_val else int(total_seconds)

    def diff_for_humans(self, other=None):
        """
        Get a human-readable difference.
        e.g., "5 months ago", "2 hours from now", "just now"
        """
        if other is None:
            other = self.now(self.tzinfo)
        other = self._ensure_carbon(other)

        is_future = self > other
        rd = relativedelta(self, other)

        # Find the largest unit
        if rd.years != 0:
            unit, value = 'year', abs(rd.years)
        elif rd.months != 0:
            unit, value = 'month', abs(rd.months)
        elif rd.days != 0:
            unit, value = 'day', abs(rd.days)
        elif rd.hours != 0:
            unit, value = 'hour', abs(rd.hours)
        elif rd.minutes != 0:
            unit, value = 'minute', abs(rd.minutes)
        elif rd.seconds != 0:
            unit, value = 'second', abs(rd.seconds)
        else:
            return "just now"

        # Pluralize
        s = 's' if value > 1 else ''
        unit_str = f"{value} {unit}{s}"

        # Add suffix
        return f"{unit_str} from now" if is_future else f"{unit_str} ago"

    # --- Comparisons ---

    def is_weekday(self):
        """Is the date a weekday?"""
        return self.weekday() < 5  # Monday=0, Sunday=6

    def is_weekend(self):
        """Is the date a weekend?"""
        return self.weekday() >= 5  # Saturday=5, Sunday=6

    def is_today(self):
        """Is the date today?"""
        return self.to_date_string() == self.today(self.tzinfo).to_date_string()

    def is_tomorrow(self):
        """Is the date tomorrow?"""
        return self.to_date_string() == self.tomorrow(self.tzinfo).to_date_string()

    def is_yesterday(self):
        """Is the date yesterday?"""
        return self.to_date_string() == self.yesterday(self.tzinfo).to_date_string()

    def is_past(self):
        """Is the date in the past?"""
        return self < self.now(self.tzinfo)

    def is_future(self):
        """Is the date in the future?"""
        return self > self.now(self.tzinfo)

    def is_leap_year(self):
        """Is it a leap year?"""
        year = self.year
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def is_same_day(self, other):
        """Check if the given date is the same day."""
        other = self._ensure_carbon(other)
        return self.to_date_string() == other.to_date_string()

    def is_same_month(self, other):
        """Check if the given date is the same month and year."""
        other = self._ensure_carbon(other)
        return self.year == other.year and self.month == other.month

    def is_same_year(self, other):
        """Check if the given date is the same year."""
        other = self._ensure_carbon(other)
        return self.year == other.year

    # --- Getters / Setters ---

    # Getters are inherited: .year, .month, .day, .hour, etc.
    # Python properties are more Pythonic, but 'set_' matches Carbon.

    def set_year(self, value):
        return self.replace(year=value)

    def set_month(self, value):
        return self.replace(month=value)

    def set_day(self, value):
        return self.replace(day=value)

    def set_hour(self, value):
        return self.replace(hour=value)

    def set_minute(self, value):
        return self.replace(minute=value)

    def set_second(self, value):
        return self.replace(second=value)

    def set_microsecond(self, value):
        return self.replace(microsecond=value)

    def set_timezone(self, tz):
        """
        Alias for astimezone.
        NOTE: Limited by constraints. Only 'UTC' string or tzinfo objects.
        """
        if isinstance(tz, str):
            if tz.upper() == 'UTC':
                tz_info = timezone.utc
            else:
                raise ValueError(
                    "String timezones other than 'UTC' require `pytz` or "
                    "`zoneinfo` (Python 3.9+), which are not in the "
                    "allowed imports. Please pass a valid tzinfo object."
                )
        elif isinstance(tz, timezone):
             tz_info = tz
        else:
            raise TypeError("Timezone must be a string or tzinfo object.")
            
        return self.astimezone(tz_info)