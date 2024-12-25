# Advanced Crypto Trading Bot (Offline Edition)

This project is still under development.

![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Fixes](#fixes)
- [Exclusions](#exclusions)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Components](#components)
  - [Indicators](#indicators)
  - [Machine Learning Model](#machine-learning-model)
  - [Strategy Configuration](#strategy-configuration)
  - [Backtesting](#backtesting)
- [Logging](#logging)
- [Customization](#customization)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Overview

The **Advanced Crypto Trading Bot (Offline Edition)** is a comprehensive Python-based tool designed for simulating and analyzing cryptocurrency trading strategies without the need for live data feeds or real-time order execution. Leveraging technical indicators, machine learning models, and sophisticated backtesting mechanisms, this bot provides valuable insights into potential trading strategies' performance over historical data.

## Features

- **Technical Indicators**:
  - **Relative Volatility Index (RelVolIdx)**
  - **Bollinger Bands**
  - **Relative Strength Index (RSI)**
  - **Moving Average Convergence Divergence (MACD)**

- **Machine Learning**:
  - **Ensemble Model** combining Random Forest and Logistic Regression classifiers.
  - **Multi-Timeframe Analysis** using Daily and 4-Hour (4H) data.

- **Trading Strategy Enhancements**:
  - **Partial Profits**: Taking partial exits to secure profits.
  - **Trailing Stops**: Dynamically adjusting stop-loss levels based on price movements.
  - **Pyramiding**: Increasing position size based on certain conditions.
  - **Risk Management**:
    - **Optional Non-Compounding Approach** for fixed risk per trade.
    - **Dynamic Position Sizing** based on volatility and ML confidence.

- **Backtesting**:
  - **Offline Backtest** supporting one exit per bar.
  - **Diversification** across multiple cryptocurrency pairs.
  - **Transaction Costs**: Incorporates fees and slippage in simulations.

- **Logging**:
  - Comprehensive logging of bot activities and performance metrics.

## Fixes

1. **Single Exit per Bar**: Ensures only one partial or full exit occurs within each time interval, preventing over-trading.
2. **Optional Non-Compounding Risk Approach**: Allows users to choose between compounding and fixed risk strategies, providing flexibility in risk management.

## Exclusions

- **Live Data Feed**: The bot operates on historical data and does not support real-time data streaming.
- **Order Execution**: No integration with cryptocurrency exchanges for executing trades.

## Installation

### Prerequisites

- **Python 3.8 or higher**

### Clone the Repository

```bash
git clone https://github.com/yourusername/advanced-crypto-trading-bot.git
cd advanced-crypto-trading-bot
```

### Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

*If a `requirements.txt` is not provided, install the necessary packages manually:*

```bash
pip install numpy pandas scikit-learn ta
```

## Usage

The bot is designed to run as a standalone script. It processes historical data for specified cryptocurrency symbols, applies technical indicators, trains a machine learning model, and performs backtesting based on the configured strategy.

### Running the Bot

```bash
python run.py
```

*Ensure that you have the necessary data files or modify the data fetching logic as needed.*

## Configuration

The trading strategy can be customized via the `StrategyConfig` class. Key parameters include:

- **initial_capital**: Starting capital for backtesting (e.g., `$10,000`).
- **risk_per_trade**: Percentage of capital to risk per trade (e.g., `1%`).
- **trailing_stop_mult**: Multiplier for trailing stop-loss calculations.
- **partial_profit_mult**: Multiplier for taking partial profits.
- **partial_profit_fraction**: Fraction of the position to exit when taking partial profits.
- **max_drawdown**: Maximum allowable drawdown before risk parameters are adjusted.
- **enable_pyramiding**: Toggle for enabling pyramiding.
- **pyramid_increment_rvol**: Increment factor for pyramiding based on volatility.
- **pyramid_max_layers**: Maximum number of pyramiding layers.
- **ensemble_threshold**: Threshold for ensemble model signal confirmation.
- **fee_pct**: Transaction fee percentage per trade.
- **slippage_pct**: Slippage percentage per trade.
- **compounding**: Toggle for compounding vs. fixed risk approach.
- **fixed_risk_amount**: Fixed amount to risk per trade when compounding is disabled.

*Example Configuration:*

```python
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
    compounding=False,  # Disable compounding for fixed risk
    fixed_risk_amount=100  # Fixed risk per trade
)
```

## Components

### Indicators

The bot calculates several technical indicators to inform trading decisions:

- **Relative Volatility Index (RelVolIdx)**: Measures volatility relative to price movements.
- **Bollinger Bands**: Identifies overbought or oversold conditions.
- **Relative Strength Index (RSI)**: Measures the speed and change of price movements.
- **MACD**: Shows the relationship between two moving averages of prices.

*Indicators are added to the DataFrame in the `add_indicators` function.*

### Machine Learning Model

An ensemble machine learning model combines **Random Forest** and **Logistic Regression** classifiers to predict market directions based on historical data.

- **Preparation**: The dataset is prepared by labeling future returns as bullish (`1`), bearish (`-1`), or neutral (`0`) based on a threshold (e.g., ±5%).
- **Training**: The model is trained on historical data with a test split (e.g., 80% training, 20% testing).
- **Prediction**: Generates predictions and confidence scores used in trading signals.

### Strategy Configuration

The `StrategyConfig` class encapsulates all configurable parameters related to the trading strategy, including risk management, trailing stops, pyramiding, and transaction costs.

### Backtesting

The `backtest_advanced` function simulates trading over historical data, applying the configured strategy. Key aspects include:

- **Position Management**: Handles opening and closing positions based on signals.
- **Risk Control**: Implements stop-loss and take-profit mechanisms.
- **Pyramiding**: Adds to positions under favorable conditions.
- **Transaction Costs**: Accounts for fees and slippage in PnL calculations.

## Logging

All bot activities, including model training performance and backtesting results, are logged to `cryptobot.log`. The logging configuration is set up at the beginning of the script using Python's `logging` module.

## Customization

- **Data Providers**: Modify the `providers` module to integrate different data sources or formats.
- **Indicators**: Add or adjust technical indicators as needed.
- **Machine Learning**: Experiment with different models or ensemble techniques to improve prediction accuracy.
- **Strategy Rules**: Tailor the trading strategy by adjusting risk parameters, signal thresholds, and exit conditions.

## Limitations

- **Offline Edition**: This bot does not support live trading, real-time data feeds, or order execution.
- **Data Dependency**: Requires accurate and comprehensive historical data for effective backtesting.
- **Model Generalization**: Machine learning models may overfit to historical data and may not perform well in unseen market conditions.

## Copyright

This project is developed by uriencedric.

---

*Disclaimer: This trading bot is intended for educational and simulation purposes only. Trading cryptocurrencies involves significant risk and may result in financial loss. Use this tool at your own risk.*