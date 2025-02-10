import logging
from src.utilities.enums import Signal
import pandas as pd


class StatisticsGatherer:
    """Class to track runtime statistics on the performance of the bot."""

    def __init__(self) -> None:
        self.signals = {}
        self.risk_management_thresholds = {}

    def increment_stop_loss(self, tickers: list[str]) -> None:
        for ticker in tickers:
            if ticker in self.risk_management_thresholds:
                self.risk_management_thresholds[ticker]["stop_loss"] += 1
            else:
                self.risk_management_thresholds[ticker] = {"stop_loss": 1}

    def increment_take_profit(self, tickers: list[str]) -> None:
        for ticker in tickers:
            if ticker in self.risk_management_thresholds:
                self.risk_management_thresholds[ticker]["take_profit"] += 1
            else:
                self.risk_management_thresholds[ticker] = {"take_profit": 1}

    def increment_signals(self, ticker_signals: dict[str, Signal]) -> None:
        for ticker, signal in ticker_signals.items():
            if ticker in self.signals:
                if signal in self.signals[ticker]:
                    self.signals[ticker][signal] += 1
                else:
                    self.signals[ticker][signal] = 1

            else:
                self.signals[ticker] = {signal: 1}

    def to_dataframe(self) -> pd.DataFrame:
        """Converts the collected statistics to a DataFrame."""

        data = []
        for ticker, signal_map in self.signals.items():
            for signal_type, signal_value in signal_map.items():
                data.append({
                    "ticker": ticker,
                    "type": signal_type,
                    "value": signal_value
                })

        for ticker, threshold_map in self.risk_management_thresholds.items():
            for threshold_name, threshold_value in threshold_map.items():
                    data.append({
                        "ticker": ticker,
                        "type": threshold_name,
                        "value": threshold_value
                    })

        return pd.DataFrame(data)

    def to_csv(self, filename: str) -> None:
        """Exports the statistics to a CSV file."""
        df = self.to_dataframe()

        if not df.empty: 
            df.to_csv(filename, index=False)
            logging.info(f"Exporting statistics to {filename}")
        else:
            logging.info(f"No statistics to export.")
