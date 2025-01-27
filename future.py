import requests
import csv
import os
import time
from datetime import datetime
import logging

# Optional: If you'd like to visualize the data
import matplotlib.pyplot as plt
import pandas as pd

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

API_BASE_URL = "https://api-futures.kucoin.com"
CSV_FILENAME = "kucoin_sentiment_data.csv"

def get_funding_rate(symbol):
    """Fetch the current funding rate for a specific futures symbol."""
    endpoint = f"{API_BASE_URL}/api/v1/funding-rate"
    try:
        response = requests.get(endpoint, params={"symbol": symbol}, timeout=5)
        response.raise_for_status()
        data = response.json().get("data", {})
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching funding rate for {symbol}: {e}")
        return None

def get_open_interest(symbol):
    """Fetch the current open interest for a specific futures symbol."""
    endpoint = f"{API_BASE_URL}/api/v1/openInterest"
    try:
        response = requests.get(endpoint, params={"symbol": symbol}, timeout=5)
        response.raise_for_status()
        data = response.json().get("data", {})
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching open interest for {symbol}: {e}")
        return None

def get_ticker_data(symbol):
    """Fetch the latest ticker data (price, volume, etc.) for a specific futures symbol."""
    endpoint = f"{API_BASE_URL}/api/v1/ticker"
    try:
        response = requests.get(endpoint, params={"symbol": symbol}, timeout=5)
        response.raise_for_status()
        data = response.json().get("data", {})
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching ticker data for {symbol}: {e}")
        return None

def analyze_market_sentiment(symbols):
    """
    Fetch funding rate, open interest, and ticker data for multiple symbols.
    Store the results in a CSV file for historical analysis.
    """
    # Create the CSV file with headers if it doesn't exist
    file_exists = os.path.isfile(CSV_FILENAME)
    if not file_exists:
        with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "timestamp",
                "symbol",
                "funding_rate",
                "open_interest",
                "open_interest_value",
                "price",
                "volume"
            ])

    # Process each symbol
    for symbol in symbols:
        logging.info(f"Fetching data for {symbol}...")

        funding_rate = get_funding_rate(symbol)
        open_interest = get_open_interest(symbol)
        ticker_data = get_ticker_data(symbol)

        if not (funding_rate and open_interest and ticker_data):
            logging.warning(f"Skipping CSV write for {symbol} because data is incomplete.")
            continue

        # Extract relevant data
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        fr = funding_rate.get("fundingRate")
        oi = open_interest.get("amount")
        oi_value = open_interest.get("value")
        price = ticker_data.get("price")
        volume = ticker_data.get("volValue")

        # Log sentiment to console
        if fr is not None:
            fr_float = float(fr)
            if fr_float > 0:
                sentiment = "Bullish (longs paying shorts)"
            elif fr_float < 0:
                sentiment = "Bearish (shorts paying longs)"
            else:
                sentiment = "Neutral"
        else:
            sentiment = "Unknown"

        logging.info(f" - Funding Rate: {fr} ({sentiment})")
        logging.info(f" - Open Interest: {oi} contracts, Value: {oi_value} USD")
        logging.info(f" - Price: {price} USD, 24H Volume: {volume} USD\n")

        # Write data to CSV
        with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                current_time,
                symbol,
                fr,
                oi,
                oi_value,
                price,
                volume
            ])

def plot_data(symbol):
    """Plot historical funding rate, open interest, and price from the CSV file for a given symbol."""
    if not os.path.isfile(CSV_FILENAME):
        logging.error("CSV file not found. No data to plot.")
        return

    # Read data from CSV into a Pandas DataFrame
    df = pd.read_csv(CSV_FILENAME, parse_dates=["timestamp"])

    # Filter data for the selected symbol
    df_symbol = df[df["symbol"] == symbol].copy()
    if df_symbol.empty:
        logging.warning(f"No data found for symbol: {symbol}")
        return

    # Convert numeric columns
    df_symbol["funding_rate"] = pd.to_numeric(df_symbol["funding_rate"], errors='coerce')
    df_symbol["open_interest"] = pd.to_numeric(df_symbol["open_interest"], errors='coerce')
    df_symbol["open_interest_value"] = pd.to_numeric(df_symbol["open_interest_value"], errors='coerce')
    df_symbol["price"] = pd.to_numeric(df_symbol["price"], errors='coerce')
    df_symbol["volume"] = pd.to_numeric(df_symbol["volume"], errors='coerce')

    # Sort by timestamp
    df_symbol.sort_values("timestamp", inplace=True)

    # Create subplots
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 8), sharex=True)
    fig.suptitle(f"KuCoin Futures Sentiment for {symbol}", fontsize=14)

    # 1) Funding Rate
    axes[0].plot(df_symbol["timestamp"], df_symbol["funding_rate"], color='blue', label='Funding Rate')
    axes[0].set_ylabel("Funding Rate")
    axes[0].legend(loc="upper left")
    axes[0].grid(True)

    # 2) Open Interest
    axes[1].plot(df_symbol["timestamp"], df_symbol["open_interest"], color='green', label='Open Interest')
    axes[1].set_ylabel("Open Interest (contracts)")
    axes[1].legend(loc="upper left")
    axes[1].grid(True)

    # 3) Price
    axes[2].plot(df_symbol["timestamp"], df_symbol["price"], color='red', label='Price')
    axes[2].set_xlabel("Time")
    axes[2].set_ylabel("Price (USD)")
    axes[2].legend(loc="upper left")
    axes[2].grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    # Example usage
    symbols_to_analyze = ["BTCUSDTM", "ETHUSDTM"]

    # 1) Fetch Data and Store in CSV
    analyze_market_sentiment(symbols_to_analyze)

    # 2) (Optional) Plot data for one of the symbols (uncomment to visualize)
    # plot_data("BTCUSDTM")

if __name__ == "__main__":
    main()
