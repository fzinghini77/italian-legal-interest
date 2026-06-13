"""
legal_interest.py — Italian statutory legal interest calculator (art. 1284 c.c.).

Legal interest accrues on a sum of money at the statutory rate in force, pro rata
to the number of days elapsed. Because the rate changes from year to year, a
period that spans several years must be split: each calendar segment is charged
at that year's rate.

Standard model (the one used by tuttosemplice.com):

    interest_segment = principal * rate_year / 100 * days_in_segment / days_basis

where `days_basis` is 365 (the convention used in the Gazzetta-style calculation
and by most Italian practitioners) or, optionally, the actual length of the year
(365/366) for the "anno civile" method.

The total interest is the sum of all yearly segments between the two dates.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List

from rates import rate_for_year


@dataclass
class InterestSegment:
    year: int
    rate_pct: float
    days: int
    interest: float

    def __str__(self) -> str:
        return (f"  {self.year}: {self.days:>3} days @ {self.rate_pct:>5.2f}% "
                f"= {self.interest:>12.2f} €")


@dataclass
class InterestResult:
    principal: float
    start: date
    end: date
    total_days: int
    interest: float
    total: float                       # principal + interest
    segments: List[InterestSegment] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            "LegalInterestResult(",
            f"  principal   = {self.principal:>14.2f} €",
            f"  period      = {self.start.isoformat()} -> {self.end.isoformat()} "
            f"({self.total_days} days)",
            "  breakdown:",
        ]
        lines += [str(s) for s in self.segments]
        lines += [
            f"  interest    = {self.interest:>14.2f} €",
            f"  total       = {self.total:>14.2f} €",
            ")",
        ]
        return "\n".join(lines)


def _days_in_year(year: int) -> int:
    return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365


class LegalInterestCalculator:
    """
    Compute Italian legal interest (interessi legali) over an arbitrary period,
    automatically applying the correct statutory rate for each year crossed.

    Parameters
    ----------
    use_actual_year_length : bool
        If False (default) every yearly segment is divided by 365, matching the
        convention used by tuttosemplice.com and most practitioners.
        If True, leap years are divided by 366 ("anno civile" method).
    inclusive_end : bool
        If True (default) both the start and the end day are counted, so a full
        calendar year (1 Jan -> 31 Dec) is 365 days and 10,000 € at 2.5 % yields
        exactly 250 €. Set False to exclude the end day (dies ad quem excluded).
    """

    def __init__(self, use_actual_year_length: bool = False,
                 inclusive_end: bool = True):
        self.use_actual_year_length = use_actual_year_length
        self.inclusive_end = inclusive_end

    def calculate(self, principal: float, start: date, end: date) -> InterestResult:
        if end < start:
            raise ValueError("end date must not be before start date")

        last_day = end + timedelta(days=1) if self.inclusive_end else end
        segments: List[InterestSegment] = []
        total_interest = 0.0
        total_days = 0

        for year in range(start.year, last_day.year + 1):
            seg_start = max(start, date(year, 1, 1))
            seg_end = min(last_day, date(year + 1, 1, 1))   # exclusive
            days = (seg_end - seg_start).days
            if days <= 0:
                continue
            rate = rate_for_year(year)
            basis = _days_in_year(year) if self.use_actual_year_length else 365
            interest = principal * rate / 100.0 * days / basis
            segments.append(InterestSegment(year, rate, days, round(interest, 6)))
            total_interest += interest
            total_days += days

        total_interest = round(total_interest, 2)
        return InterestResult(
            principal=principal,
            start=start,
            end=end,
            total_days=total_days,
            interest=total_interest,
            total=round(principal + total_interest, 2),
            segments=segments,
        )
