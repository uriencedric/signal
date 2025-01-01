import argparse
import traceback

import yaml

from config import TITLE
from lib.tools import *
from misc.utils import print_title
from providers import fetch

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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process some cryptocurrency symbols.")

    parser.add_argument(
        '--config',
        type=None,
        required=True,
        help='the path to your config file'
    )

    args = parser.parse_args()
    return args


def load_config(config_path):
    """LOad a yaml config file

    Args:
        config_path (_type_): _description_

    Returns:
        (dict): our file represented as a dict
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    print_title(TITLE)
    args = parse_arguments()
    config_data = load_config(args.config)

    strategy_config = config_data.get("strategy_config", {})
    symbols = config_data["runtime"]["symbols"].split(",")
    days_back = config_data["runtime"]["days_back"]
    timeframe_suffix = config_data["runtime"]["timeframe_suffix"]
    _provider = config_data["runtime"]["provider"]
    ml_test_size = config_data["runtime"]["ml_test_size"]
    timeframe_daily = config_data["runtime"]["timeframe_daily"]
    timeframe_hourly = config_data["runtime"]["timeframe_hourly"]

    config = StrategyConfig(
        initial_capital=strategy_config.get("initial_capital", 1000),
        risk_per_trade=strategy_config.get("risk_per_trade", 0.01),
        trailing_stop_mult=strategy_config.get("trailing_stop_mult", 1.5),
        partial_profit_mult=strategy_config.get("partial_profit_mult", 1.0),
        partial_profit_fraction=strategy_config.get("partial_profit_fraction", 0.5),
        max_drawdown=strategy_config.get("max_drawdown", 0.2),
        enable_pyramiding=strategy_config.get("enable_pyramiding", True),
        # pyramid_increment_rvol=strategy_config.get("pyramid_increment_rvol", 1.0),
        pyramid_max_layers=strategy_config.get("pyramid_max_layers", 2),
        ensemble_threshold=strategy_config.get("ensemble_threshold", 2),
        fee_pct=strategy_config.get("fee_pct", 0.1),
        slippage_pct=strategy_config.get("slippage_pct", 0.05),
        compounding=strategy_config.get("compounding", False),
        fixed_risk_amount=strategy_config.get("fixed_risk_amount", 100)
    )

    for symbol in symbols:
        try:
            provider = fetch.get_provider(provider=_provider)
            df_daily = fetch.load_data(provider(symbol, timeframe_daily))
            add_indicators(df_daily)
            # df noise reduction
            df_daily.dropna(inplace=True)
            df_daily = df_daily.drop('upper_shadow', axis=1)
            df_daily = df_daily.drop('lower_shadow', axis=1)
            df_daily = df_daily.drop('body', axis=1)
            # Prepare ML dataset
            X_res, y_res, features = prepare_ml_dataset(df_daily, shift_days=days_back)

            # Train ML model
            ensemble_model = train_ensemble_model(X_res, y_res, test_size=ml_test_size)

            # Train Anomaly Detector
            anomaly_model, df_daily = train_anomaly_detector(df_daily, features)

            # Perform Backtest
            backtest_results = backtest_advanced(df_daily, ensemble_model, config)
            logger.info(f"Final Capital after Backtest: {backtest_results['final_capital']:.2f}")
            logger.info(f"Total Trades: {backtest_results['trades_count']}")

            print_monthly_suggestion(config, ensemble_model, symbol, df_daily, days_back)

        except Exception as e:
            logger.error(f"Main execution error: {e}")
            print(traceback.format_exc())
