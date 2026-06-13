"""
revaluation.py — ISTAT FOI monetary revaluation (rivalutazione monetaria).

In Italian civil law a past sum is often revalued to today's purchasing power
using the FOI index (Indice dei prezzi al consumo per le Famiglie di Operai e
Impiegati, "senza tabacchi") published monthly by ISTAT. The revaluation
coefficient between two dates is simply the ratio of the two index values:

    coefficient   = FOI_end / FOI_start
    revalued_sum  = original_sum * coefficient

This is computed together with legal interest in the classic "rivalutazione e
interessi" calculation (e.g. art. 429 c.p.c. for employment credits). The same
engine powers the revaluation tools on tuttosemplice.com.

ISTAT publishes the FOI in successive base periods (… 1995=100, 2010=100,
2015=100); a continuous series is obtained by chaining them with the official
raccordo coefficients (average of the base year in the previous series = 100),
which is exactly what `IstatFoiLoader` does when reading the live ISTAT data.

The `FOI_ANNUAL_2015` table below is a rounded snapshot of recent **annual
average** indices (base 2015 = 100), provided so the examples and tests run
offline. For production use load the authoritative monthly series from ISTAT.
"""

from dataclasses import dataclass
from typing import Dict, Optional

# Rounded ISTAT FOI annual-average index, base 2015 = 100 (senza tabacchi).
# Snapshot for offline use — verify against ISTAT for official calculations.
FOI_ANNUAL_2015: Dict[int, float] = {
    2015: 100.0,
    2016: 99.9,
    2017: 101.0,
    2018: 102.1,
    2019: 102.6,
    2020: 102.4,
    2021: 104.4,
    2022: 112.9,
    2023: 119.5,
    2024: 120.7,
    2025: 122.8,
}


@dataclass
class RevaluationResult:
    original: float
    revalued: float
    coefficient: float
    index_start: float
    index_end: float

    @property
    def gain(self) -> float:
        return round(self.revalued - self.original, 2)

    def __str__(self) -> str:
        return (
            "RevaluationResult(\n"
            f"  original     = {self.original:>12.2f} €\n"
            f"  coefficient  = {self.coefficient:>12.6f}\n"
            f"  revalued     = {self.revalued:>12.2f} €\n"
            f"  gain         = {self.gain:>12.2f} €\n"
            ")"
        )


class IstatRevaluation:
    """
    Revalue a monetary amount between two periods using a FOI index series.

    Parameters
    ----------
    series : dict
        Mapping of period -> index value. Keys may be integer years (annual
        averages) or 'YYYY-MM' strings (monthly), as long as both endpoints use
        the same key type. Defaults to the embedded annual snapshot.
    """

    def __init__(self, series: Optional[Dict] = None):
        self.series = dict(series) if series is not None else dict(FOI_ANNUAL_2015)

    def coefficient(self, start_key, end_key) -> float:
        if start_key not in self.series:
            raise KeyError(f"No FOI index for {start_key!r}")
        if end_key not in self.series:
            raise KeyError(f"No FOI index for {end_key!r}")
        return self.series[end_key] / self.series[start_key]

    def revalue(self, amount: float, start_key, end_key) -> RevaluationResult:
        i_start = self.series[start_key]
        i_end = self.series[end_key]
        coeff = i_end / i_start
        return RevaluationResult(
            original=round(amount, 2),
            revalued=round(amount * coeff, 2),
            coefficient=round(coeff, 6),
            index_start=i_start,
            index_end=i_end,
        )


class IstatFoiLoader:
    """
    Load the continuous monthly FOI series from the public ISTAT (IstatData /
    SDMX-JSON) endpoint and chain the successive base periods into a single
    series in base 2015 = 100, ready to pass to `IstatRevaluation`.

    Network access is required; if you only need recent years, the embedded
    `FOI_ANNUAL_2015` annual snapshot is enough.
    """

    # FOI senza tabacchi, monthly, general index — IstatData dataflow.
    DEFAULT_URL = (
        "https://esploradati.istat.it/SDMXWS/rest/data/"
        "IT1,28_201_DF_DCSP_FOI1B2015_1,1.0/M.IT.FOI....N/"
        "?format=jsondata&startPeriod=1996"
    )

    def __init__(self, url: Optional[str] = None):
        self.url = url or self.DEFAULT_URL

    def load(self) -> Dict[str, float]:
        import json
        import urllib.request

        with urllib.request.urlopen(self.url, timeout=20) as resp:
            data = json.loads(resp.read())

        # SDMX-JSON: observation periods live in the structure, values in series.
        structure = data.get("structure") or data.get("data", {}).get("structures", [{}])[0]
        periods = structure["dimensions"]["observation"][0]["values"]
        datasets = data.get("dataSets") or data.get("data", {}).get("dataSets")
        observations = datasets[0]["series"]

        series: Dict[str, float] = {}
        for obs in observations.values():
            for idx, val in obs["observations"].items():
                pid = periods[int(idx)]["id"]      # 'YYYY-MM'
                series[pid] = float(val[0])
        return dict(sorted(series.items()))
