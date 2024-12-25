import logging
import traceback
import warnings
from config import ALLOWED_SYMBOLS
from lib.tools import *
from providers import fetch
import argparse


# ===== Setup Logger =====
logging.basicConfig(
    filename='cryptobot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
warnings.filterwarnings("ignore")


def validate_symbols(symbols_str):
    """
    Validates that each symbol in the comma-separated string is allowed.
    Returns a list of symbols if valid, otherwise raises an argparse error.
    """
    # Split the input string by commas and remove any surrounding whitespace
    symbols = [symbol.strip().upper() for symbol in symbols_str.split(',')]

    # Check if all symbols are in the allowed list
    invalid_symbols = [s for s in symbols if s not in ALLOWED_SYMBOLS]
    if invalid_symbols:
        message = (f"Invalid symbol(s): {', '.join(invalid_symbols)}. "
                   f"Allowed symbols are: {', '.join(ALLOWED_SYMBOLS)}.")
        raise argparse.ArgumentTypeError(message)

    return symbols


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process some cryptocurrency symbols.")

    parser.add_argument(
        '--symbols',
        type=validate_symbols,
        required=True,
        help='Comma-separated list of symbols. Allowed symbols are BTCUSDT, ETHUSDT, SOLUSDT.'
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    print(color_text("""
============================================================================
                Advanced Crypto Trading Bot (Offline Edition)                                             
============================================================================    
          """))
    print()
    args = parse_arguments()
    symbols = args.symbols

    for symbol in symbols:
        try:
            provider = fetch.get_provider("crypto_dd")
            df_daily = fetch.load_data(provider("%s" % symbol, "d"))
            add_indicators(df_daily)

            df_4h_data = provider(symbol, "1h")
            df_4h = fetch.load_data(df_4h_data, "4h")
            add_indicators(df_4h)

            df_daily, df_4h = align_start_date(df_daily, df_4h)
            df_merged = merge_timeframes(df_daily, df_4h, suffix_4h='_4h')

            df_ml, features = prepare_ml_dataset(df_merged)
            model_ensemble = train_ensemble_model(
                df_ml, features, test_size=0.2)

            # 3) Strategy config
            # Turn off compounding if you want to keep final capital realistic
            config = StrategyConfig(
                initial_capital=10000,
                risk_per_trade=0.01,
                trailing_stop_mult=1.5,
                partial_profit_mult=1.0,
                partial_profit_fraction=0.5,
                max_drawdown=0.2,
                enable_pyramiding=True,
                pyramid_increment_rvol=1.0,
                pyramid_max_layers=2,
                ensemble_threshold=2,
                fee_pct=0.1,
                slippage_pct=0.05,
                compounding=False,  # <<< TURN OFF COMPOUNDING
                fixed_risk_amount=100  # e.g. $100 risk each trade
            )

            final_cap, trades_pnl = backtest_advanced(
                df_merged, model_ensemble, config)
            logger.info(
                f"Final capital: {final_cap:.2f}, trades: {len(trades_pnl)}")

            print_monthly_suggestion(symbol, df_merged, 30)

        except Exception as e:
            logger.error(f"Main execution error: {e}")
            print(traceback.format_exc())
