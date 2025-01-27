import argparse
import traceback

import ccxt
import yaml

from lib.future import analyze_market_sentiment, plot_data
from lib.tools import *
from misc.utils import print_title, load_config

# ===== Setup Logger =====
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
warnings.filterwarnings("ignore")

TITLE = """
============================================================================
                Advanced Crypto Trading Bot (Offline Edition)                                             
============================================================================    
"""


def rewrite_symbol_for_future(symbol):
    if symbol.endswith("BTC/USDT"):
        return symbol.replace("/", "").replace("-", "").replace("BTCUSDT", "XBTUSDTM")
    return symbol.replace("/", "").replace("-", "").replace("USDT", "USDTM")

if __name__ == "__main__":
    print_title(TITLE)
    config_data = load_config("config.yaml")

    strategy_config = config_data.get("strategy_config", {})
    symbols = config_data["runtime"]["symbols"].split(",")
    days_back = config_data["runtime"]["days_back"]
    threshold = config_data["runtime"]["threshold"]
    timeframe_suffix = config_data["runtime"]["timeframe_suffix"]
    ml_test_size = config_data["runtime"]["ml_test_size"]
    timeframe_daily = config_data["runtime"]["timeframe_daily"]
    timeframe_hourly = config_data["runtime"]["timeframe_hourly"]
    
    if days_back > threshold :
        raise ValueError("days_back should be less than 30")

    config = StrategyConfig(
        initial_capital=strategy_config.get("initial_capital", 1000),
        risk_per_trade=strategy_config.get("risk_per_trade", 0.01),
        trailing_stop_mult=strategy_config.get("trailing_stop_mult", 1.5),
        partial_profit_mult=strategy_config.get("partial_profit_mult", 1.0),
        partial_profit_fraction=strategy_config.get("partial_profit_fraction", 0.5),
        max_drawdown=strategy_config.get("max_drawdown", 0.2),
        enable_pyramiding=strategy_config.get("enable_pyramiding", True),
        pyramid_increment_atr=strategy_config.get("pyramid_increment_atr", 1.0),
        pyramid_max_layers=strategy_config.get("pyramid_max_layers", 2),
        ensemble_threshold=strategy_config.get("ensemble_threshold", 2),
        fee_pct=strategy_config.get("fee_pct", 0.1),
        slippage_pct=strategy_config.get("slippage_pct", 0.05),
        compounding=strategy_config.get("compounding", False),
        fixed_risk_amount=strategy_config.get("fixed_risk_amount", 100)
    )

    for symbol in symbols:
        try:
            
            _symbol = rewrite_symbol_for_future(symbol)
            
            analyze_market_sentiment(_symbol)
            plot_data(symbol)
            
            exchange = ccxt.binance()
            # Fetch OHLCV data for BTC/USDT
            timeframe = '1d'  # 1-day interval
            limit = 1000       # Number of data points to fetch
            all_data = []
            # Initialize starting point for historical data
            start_time = exchange.parse8601('2020-01-01T00:00:00Z')
            while True:
                data = exchange.fetch_ohlcv(symbol, timeframe, since=start_time, limit=limit)
                if not data:
                    break
                all_data.extend(data)
                start_time = data[-1][0] + 1  # Move to the next timestamp
                # Break the loop if you have enough data or hit the desired date range
                if len(data) < limit:
                    break
            # Convert to DataFrame
            df_daily = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df_daily['timestamp'] = pd.to_datetime(df_daily['timestamp'], unit='ms')
            df_daily = df_daily.sort_values(by="timestamp")
            df_daily.rename(columns={
                'timestamp': 'Date',
                'symbol': 'Symbol',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            df_daily = df_daily.set_index('Date')
            # Convert timestamp to datetime

            add_indicators(df_daily)
            # df noise reduction
            df_daily.dropna(inplace=True)
            # Prepare ML dataset
            X_res, y_res, features = prepare_ml_dataset(df_daily, shift_days=days_back)

            # Train ML model
            ensemble_model, acc, report = train_ensemble_model(X_res, y_res, test_size=ml_test_size)

            # Train Anomaly Detector
            anomaly_model, df_daily = train_anomaly_detector(df_daily, features)

            # Perform Backtest
            capital, trades_pnl = backtest_advanced(df_daily, ensemble_model, config)
            logger.info(f"Final Capital after Backtest: {capital:.2f}")
            logger.info(f"Total Trades: {len(trades_pnl)}")

            print_monthly_suggestion(config, symbol, df_daily, acc, report, days_back)
            print()
            
        except Exception as e:
            logger.error(f"Main execution error: {e}")
            print(traceback.format_exc())
