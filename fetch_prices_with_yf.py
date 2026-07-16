#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "yfinance",
# ]
# ///


import datetime
from dataclasses import dataclass

import pandas as pd
from pandas.tseries.offsets import MonthBegin, MonthEnd

import yfinance as yf

TODAY = datetime.date.today().strftime("%Y-%m-%d")

@dataclass
class TickerConfig:
    ticker: str
    commodity: str
    quote: str
    start: str
    end: str
    fetch: bool = True

TICKERS_CONFIG = [
    TickerConfig(
        ticker="GBPEUR=X",
        commodity="GBP",
        quote="EUR",
        start="2024-01-01",
        end=TODAY,
    ),
    TickerConfig(
        ticker="USDEUR=X",
        commodity="USD",
        quote="EUR",
        start="2026-03-01",
        end=TODAY
    ),
    TickerConfig(
        ticker="LQQ.PA",
        commodity="LQQ",
        quote="EUR",
        start="2024-01-01",
        end="2026-05-10",
    ),
    TickerConfig(
        ticker="VG",
        commodity="VG",
        quote="USD",
        start="2026-03-01",
        end=TODAY,
    ),
    TickerConfig(
        ticker="WPEA.PA",
        commodity="WPEA",
        quote="EUR",
        start="2026-03-01",
        end="2026-05-10",
    ),
    TickerConfig(
        ticker="SPCX",
        commodity="SPCX",
        quote="USD",
        start="2026-06-01",
        end=TODAY,
    )
]


def fetch_prices(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    start_date_ts = pd.to_datetime(start_date) - MonthBegin() + MonthEnd()
    start_date = start_date_ts.strftime("%Y-%m-%d")

    data = yf.download(
        ticker, start=start_date, end=end_date, interval="1mo", auto_adjust=False
    )
    data = data.resample("ME").last()

    if data.empty:
        raise ValueError(f"No data for {ticker} in range {start_date}...{end_date}")


    prices = data["Close"].reset_index()
    prices["year"] = prices["Date"].dt.year

    return prices


def main():
    for config in TICKERS_CONFIG:
        ticker = config.ticker
        commodity = config.commodity
        quote = config.quote
        start_date = config.start
        end_date = config.end
        
        prices = fetch_prices(ticker, start_date, end_date)

        for year, df_year in prices.groupby("year"):
            filename = f"P{commodity}{str(year)[-2:]}.journal"

            year_directives = (
                "P"
                + " "
                + df_year["Date"].dt.strftime("%Y-%m-%d")
                + " "
                + commodity
                + " "
                + df_year[ticker].map("{:.2f}".format)
                + " "
                + quote
            )
            year_directives = year_directives.tolist()

            filepath = f"./{str(year)}/{filename}"
            with open(filepath, "w") as f:
                f.write("\n".join(year_directives) + "\n")

            print(f"Saved {len(year_directives)} price entries to {filepath} for {config.ticker}")


if __name__ == "__main__":
    main()
