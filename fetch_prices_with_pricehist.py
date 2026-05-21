#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
# ]
# ///

import datetime
import io
import subprocess
import sys
from dataclasses import dataclass

import pandas as pd

TODAY = datetime.date.today().strftime("%Y-%m-%d")

@dataclass
class TickerConfig:
    ticker: str
    commodity: str
    start: str
    end: str
    fetch: bool = True



TICKERS_CONFIG = [
    # FX
    TickerConfig(
        ticker="GBPEUR=X",
        commodity="GBP",
        start="2024-01-01",
        end=TODAY,
    ),
    TickerConfig(
        ticker="USDEUR=X",
        commodity="USD",
        start="2026-03-01",
        end=TODAY,
    ),
    # Amundi Nasdaq-100 Daily (2x) Leveraged UCITS ETF Acc
    TickerConfig(
        ticker="LQQ.PA",
        commodity="LQQ",
        start="2024-01-01",
        end="2026-05-10",
    ),
    # VG Venture Global
    TickerConfig(
        ticker="VG",
        commodity="VG",
        start="2026-03-01",
        end=TODAY,
    ),
    # iShares MSCI World Swap PEA UCITS ETF (WPEA.PA)
    TickerConfig(
        ticker="WPEA.PA",
        commodity="WPEA",
        start="2026-03-01",
        end="2026-05-10",
    ),
]

SOURCE = "yahoo"


def get_prices(
    ticker: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:

    cmd = [
        "pricehist",
        "fetch",
        SOURCE,
        ticker,
        "-t",
        "close",
        "-s",
        start_date,
        "-e",
        end_date,
        "-o",
        "json",
    ]

    try:
        result = subprocess.run(
            cmd, shell=False, capture_output=True, text=True, check=True
        )
        df = pd.read_json(io.StringIO(result.stdout))
    except (subprocess.CalledProcessError, ValueError):
        print(f"; Error processing date for {ticker}", file=sys.stderr)
        return pd.DataFrame()  # Return empty DataFrame on error

    if df.empty:
        return pd.DataFrame()  # Return empty DataFrame if no data

    # Parse
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year

    # Downsample to the last trading session of each month
    df_resampled= df.set_index("date").resample("ME").last().dropna().reset_index()


    return df_resampled


def main():

    for config in TICKERS_CONFIG:
        if not config.fetch:
            print(f"; Skipping {config.ticker} as fetch is set to False")
            continue

        commodity = config.commodity

        df = get_prices(
            config.ticker,
            config.start,
            config.end,
        )

        for year, df_year in df.groupby("year"):
            filename = f"P{commodity}{str(year)[-2:]}.journal"

            year_directives = (
                "P"
                + " "
                + df_year["date"].astype(str)
                + " "
                + commodity
                + " "
                + df_year["amount"].map("{:.2f}".format)
                + " "
                + df_year["quote"].astype(str)
            )
            year_directives = year_directives.tolist()

            filepath = f"./{str(year)}/{filename}"
            with open(filepath, "w") as f:
                f.write("\n".join(year_directives) + "\n")

            print(f"Saved {len(year_directives)} price entries to {filepath} for {config.ticker}")


if __name__ == "__main__":
    main()
