import pandas as pd

import yfinance as yf

# Map Yahoo tickers to (hledger commodity, quote currency, precision, use_adj_close)
TICKER_SPEC = {
    "GBPEUR=X": {  # FX
        "commodity": "GBP", "quote": "EUR", "precision": 6, "use_adj": False
    },  # FX
    "LQQ.PA": {  # ETF on Euronext
        "commodity": "LQQ", "quote": "EUR", "precision": 2, "use_adj": True
    },
}

def fetch_prices(
        ticker: str,
        start_date: str,
        end_date: str,
        output_file: str
):
    hcommo = TICKER_SPEC[ticker]["commodity"]
    quote = TICKER_SPEC[ticker]["quote"]
    # Fetch historical data from Yahoo Finance
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval="1mo",
        auto_adjust=False
    )

    if data.empty:
        raise ValueError(
            f"No data for {ticker} in range {start_date}..{end_date}"
        )

    # Extract end-of-month prices
    prices = data["Close"].resample("ME").last().dropna()

    # prices = data["Close"].resample("MS").last().dropna()

    # Format as hledger price directives
    price_lines = []
    for date, price in prices[ticker].items():
        directive = f"P {date.strftime('%Y-%m-%d')} {hcommo} {quote} {price:.2f}"
        price_lines.append(directive)

    # Write to file
    with open(output_file, "w") as f:
        f.write("\n".join(price_lines) + "\n")

    print(f"Saved {len(price_lines)} price entries to {output_file}")


# ticker = "GBPEUR=X"
start_date = "2024-01-01"
end_date = "2026-12-31"

for ticker in TICKER_SPEC:
    commo = TICKER_SPEC[ticker]["commodity"]
    output_file = f"P{commo}.journal"
    fetch_prices(ticker, start_date, end_date, output_file)
