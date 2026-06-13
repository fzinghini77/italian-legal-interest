# italian-legal-interest

**Python implementation of Italian statutory legal interest (interessi legali, art. 1284 c.c.) and ISTAT FOI monetary revaluation (rivalutazione monetaria).**

This library implements the same model used by [tuttosemplice.com](https://www.tuttosemplice.com) to calculate legal interest and monetary revaluation on past-due sums — the two computations that, combined, make up the classic Italian *"rivalutazione e interessi"* calculation (e.g. employment credits under art. 429 c.p.c., overdue debts, judicial restitutions, ravvedimento operoso).

## Background

### Legal interest — art. 1284 of the Italian Civil Code

The statutory legal interest rate is fixed every year by decree of the Ministry of Economy and Finance (MEF) and published in the *Gazzetta Ufficiale*. It stayed at **5 %** for decades, jumped to 10 % in 1991–1996, and since 1999 has been revised annually to track government-bond yields and inflation — swinging from **0.01 % (2021)** to **5 % (2023)** in just two years.

Interest accrues pro rata to the days elapsed, so any period that crosses a year boundary must be **split year by year**, each segment charged at that year's rate:

```
interest_segment = principal × rate_year / 100 × days_in_segment / 365
total_interest   = Σ interest_segment
```

The full historical rates table (1942 → 2026) is in [`rates.py`](rates.py).

### Monetary revaluation — ISTAT FOI index

To restore the purchasing power of an old sum, Italian courts use the **FOI** index (*prezzi al consumo per le Famiglie di Operai e Impiegati, senza tabacchi*) published monthly by ISTAT. The revaluation coefficient between two dates is just the ratio of the two index values:

```
coefficient  = FOI_end / FOI_start
revalued_sum = original_sum × coefficient
```

ISTAT publishes the FOI in successive base periods (1995=100, 2010=100, 2015=100); a continuous series is obtained by chaining them with the official *raccordo* coefficients. [`IstatFoiLoader`](revaluation.py) does this automatically from the live ISTAT data.

## Installation

```bash
pip install -r requirements.txt   # no third-party dependencies — stdlib only
```

## Quick start

```python
from datetime import date
from legal_interest import LegalInterestCalculator

calc = LegalInterestCalculator()

# 25,000 € from 01/06/2021 to 30/09/2024 — automatically applies
# the 0.01% / 1.25% / 5% / 2.5% rates of each year crossed
result = calc.calculate(25_000, date(2021, 6, 1), date(2024, 9, 30))
print(result)
```

```
LegalInterestResult(
  principal   =       25000.00 €
  period      = 2021-06-01 -> 2024-09-30 (1218 days)
  breakdown:
  2021: 214 days @  0.01% =         1.47 €
  2022: 365 days @  1.25% =       312.50 €
  2023: 365 days @  5.00% =      1250.00 €
  2024: 274 days @  2.50% =       469.18 €
  interest    =        2033.14 €
  total       =       27033.14 €
)
```

### Monetary revaluation

```python
from revaluation import IstatRevaluation

rev = IstatRevaluation()                       # embedded annual FOI snapshot
print(rev.revalue(1_000, 2015, 2024))          # 1,000 € in 2015 -> ? in 2024
```

```
RevaluationResult(
  original     =      1000.00 €
  coefficient  =     1.207000
  revalued     =      1207.00 €
  gain         =       207.00 €
)
```

### Live FOI series from ISTAT

```python
from revaluation import IstatFoiLoader, IstatRevaluation

series = IstatFoiLoader().load()               # continuous monthly FOI, base 2015=100
rev = IstatRevaluation(series)
print(rev.revalue(1_000, "2015-01", "2024-12"))
```

## Conventions

- **Day count** — by default both the start and the end day are counted, so a full calendar year (1 Jan → 31 Dec) is 365 days and 10,000 € at 2.5 % yields exactly 250 €. This matches the convention used by tuttosemplice.com. Pass `inclusive_end=False` to exclude the end day.
- **Year basis** — segments are divided by 365 by default; pass `use_actual_year_length=True` for the *anno civile* method (leap years divided by 366).

## Files

```
italian-legal-interest/
├── rates.py            # Historical legal interest rates 1942–2026 (art. 1284 c.c.)
├── legal_interest.py   # LegalInterestCalculator — multi-year, day-proportional
├── revaluation.py      # ISTAT FOI monetary revaluation + live ISTAT loader
├── examples.py         # Worked examples (legal interest, revaluation, combined)
├── requirements.txt
└── README.md
```

## Disclaimer

The historical rates and FOI figures are provided for information purposes. For any official or legal use, always verify the current legal interest rate in the *Gazzetta Ufficiale* and the FOI index on the ISTAT website, or consult a qualified professional.

## License

MIT — free to use, modify and redistribute.

---

*This model powers the free legal-interest and monetary-revaluation tools at [tuttosemplice.com/strumenti](https://www.tuttosemplice.com/strumenti/) — practical Italian financial calculators with 10 M+ annual readers.*
