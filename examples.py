"""
examples.py — Usage examples for the Italian legal interest & revaluation library.

Run:  python examples.py
"""

from datetime import date

from legal_interest import LegalInterestCalculator
from revaluation import IstatRevaluation

# ──────────────────────────────────────────────────────────────
# Example 1 — Legal interest on a credit within a single year
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("Example 1: Legal interest on 10,000 € — full year 2026")
print("=" * 60)

calc = LegalInterestCalculator()
res = calc.calculate(10_000, date(2026, 1, 1), date(2026, 12, 31))
print(res)

# ──────────────────────────────────────────────────────────────
# Example 2 — A period that spans several years (rates change)
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("Example 2: 25,000 € from 01/06/2021 to 30/09/2024")
print("           (crosses the 0.01% / 1.25% / 5% / 2.5% rates)")
print("=" * 60)

res2 = calc.calculate(25_000, date(2021, 6, 1), date(2024, 9, 30))
print(res2)

# ──────────────────────────────────────────────────────────────
# Example 3 — The 2023 spike: highest legal rate since 1999
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("Example 3: 1,000 € for the whole of 2023 (rate = 5.00%)")
print("=" * 60)

res3 = calc.calculate(1_000, date(2023, 1, 1), date(2023, 12, 31))
print(res3)

# ──────────────────────────────────────────────────────────────
# Example 4 — ISTAT FOI monetary revaluation
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("Example 4: Revalue 1,000 € from 2015 to 2024 (ISTAT FOI)")
print("=" * 60)

rev = IstatRevaluation()                      # uses embedded annual snapshot
print(rev.revalue(1_000, 2015, 2024))

# ──────────────────────────────────────────────────────────────
# Example 5 — Combined: revaluation + legal interest
# (the classic "rivalutazione e interessi" calculation)
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("Example 5: 5,000 € owed since 2020 — revalued to 2025,")
print("           then legal interest on the revalued sum")
print("=" * 60)

revalued = rev.revalue(5_000, 2020, 2025)
print(revalued)
interest = calc.calculate(revalued.revalued, date(2020, 1, 1), date(2025, 12, 31))
print(interest)
print(f"\n  Grand total (revalued capital + interest): "
      f"{revalued.revalued + interest.interest:,.2f} €")

# ──────────────────────────────────────────────────────────────
# Example 6 — Live FOI series from ISTAT (optional, needs network)
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("Example 6: Live monthly FOI from ISTAT")
print("=" * 60)
try:
    from revaluation import IstatFoiLoader
    series = IstatFoiLoader().load()
    rev_live = IstatRevaluation(series)
    print(rev_live.revalue(1_000, "2015-01", "2024-12"))
except Exception as e:
    print(f"  (Skipped — ISTAT API unavailable: {e})")
