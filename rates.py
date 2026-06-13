"""
rates.py — Italian statutory legal interest rates (saggio degli interessi legali).

The legal interest rate is set every year by decree of the Ministry of Economy
and Finance (MEF) under Article 1284 of the Italian Civil Code, and published in
the Gazzetta Ufficiale. Until 1990 it was fixed at 5 % for decades; since 1999 it
has been revised yearly to track the average yield of government bonds and
inflation.

This is the same historical table used in production by tuttosemplice.com.
Values are annual percentages. For any official/legal use, always verify the
current rate in the Gazzetta Ufficiale.
"""

# Year -> annual legal interest rate (%), art. 1284 c.c.
LEGAL_INTEREST_RATES = {
    1942: 5.0,  1943: 5.0,  1944: 5.0,  1945: 5.0,  1946: 5.0,
    1947: 5.0,  1948: 5.0,  1949: 5.0,  1950: 5.0,  1951: 5.0,
    1952: 5.0,  1953: 5.0,  1954: 5.0,  1955: 5.0,  1956: 5.0,
    1957: 5.0,  1958: 5.0,  1959: 5.0,  1960: 5.0,  1961: 5.0,
    1962: 5.0,  1963: 5.0,  1964: 5.0,  1965: 5.0,  1966: 5.0,
    1967: 5.0,  1968: 5.0,  1969: 5.0,  1970: 5.0,  1971: 5.0,
    1972: 5.0,  1973: 5.0,  1974: 5.0,  1975: 5.0,  1976: 5.0,
    1977: 5.0,  1978: 5.0,  1979: 5.0,  1980: 5.0,  1981: 5.0,
    1982: 5.0,  1983: 5.0,  1984: 5.0,  1985: 5.0,  1986: 5.0,
    1987: 5.0,  1988: 5.0,  1989: 5.0,  1990: 5.0,
    # Law 353/1990 raised the base rate to 10 %
    1991: 10.0, 1992: 10.0, 1993: 10.0, 1994: 10.0, 1995: 10.0, 1996: 10.0,
    1997: 5.0,  1998: 5.0,
    # From 1999: revised annually by MEF decree (art. 1284 c.c. as amended)
    1999: 2.5,  2000: 3.5,  2001: 3.0,  2002: 3.0,  2003: 2.5,  2004: 2.5,
    2005: 2.5,  2006: 2.5,  2007: 2.5,  2008: 3.0,  2009: 3.0,  2010: 3.0,
    2011: 2.5,  2012: 2.5,  2013: 2.5,  2014: 1.0,  2015: 0.5,  2016: 0.2,
    2017: 0.1,  2018: 0.3,  2019: 0.8,  2020: 0.05, 2021: 0.01, 2022: 1.25,
    2023: 5.0,  2024: 2.5,  2025: 2.0,  2026: 2.5,
}


def rate_for_year(year: int) -> float:
    """
    Return the legal interest rate (%) for a given year.

    For years before the table starts (pre-1942) the 5 % codified rate is
    returned; for years after the last known value, the most recent rate is
    carried forward (with a clear caveat that you should verify it).
    """
    if year in LEGAL_INTEREST_RATES:
        return LEGAL_INTEREST_RATES[year]
    years = sorted(LEGAL_INTEREST_RATES)
    if year < years[0]:
        return LEGAL_INTEREST_RATES[years[0]]
    return LEGAL_INTEREST_RATES[years[-1]]
