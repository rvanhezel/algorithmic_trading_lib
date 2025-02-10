from src.data_structures.marketdata_state import MarketDataState
import pandas as pd
from typing import Optional


class MarketDataService:
    """The market data service layer focuses on reusable business logic, 
    operating on the market data state."""

    def __init__(self, state: MarketDataState) -> None:
        self.state = state

    def get_latest_price(self, api_name: str, ticker: str, price_type: str = 'close') -> float:
        """Retrieve the latest price for a given ticker from the market data."""
        return self.get_latest_entry(api_name, ticker)[price_type]
    
    def get_latest_entry(self, api_name: str, ticker: str) -> float:
        """Retrieve the latest price for a given ticker from the market data."""
        data = self.state.market_data.get(api_name, {}).get(ticker, None)
        if data is None or data.empty:
            return None
        
        return data.iloc[0]
    
    def get_price(self, api_name: str, ticker: str, date: pd.Timestamp, price_type: str = 'close') -> float:
        data = self.state.market_data.get(api_name, {}).get(ticker, None)
        if data is None or data.empty:
            return None
        
        return float(data.loc[date][price_type])
    
    def get_real_time_price(self, symbol: str, api_name: str = "twelve_data") -> float:
        return self.state.apis[api_name].get_real_time_price(symbol)

    def filter_data_by_date(self, api_name: str, ticker: str, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
        """Filter market data for a specific ticker by date range."""
        data = self.state.market_data.get(api_name, {}).get(ticker, None)
        if data is None or data.empty:
            return pd.DataFrame()
        return data.loc[start_date:end_date]
    
    def get_news(self, 
                 api_name: str, 
                 ticker: str, 
                 from_date: Optional[pd.Timestamp] = None, 
                 to_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        return self.state.apis[api_name].get_news(ticker, from_date, to_date)

            

