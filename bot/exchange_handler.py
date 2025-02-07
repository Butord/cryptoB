import ccxt
import pandas as pd
from datetime import datetime, timedelta

class ExchangeHandler:
    def __init__(self, exchange_id='binance'):
        self.exchange_id = exchange_id
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

    def get_ohlcv(self, symbol, timeframe='1h', limit=100):
        """Get OHLCV data for a symbol"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching OHLCV data: {str(e)}")
            return None

    def get_ticker(self, symbol):
        """Get current ticker information"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            print(f"Error fetching ticker: {str(e)}")
            return None

    def get_order_book(self, symbol, limit=20):
        """Get order book for a symbol"""
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return order_book
        except Exception as e:
            print(f"Error fetching order book: {str(e)}")
            return None

    def calculate_price_levels(self, symbol):
        """Calculate important price levels"""
        try:
            ohlcv = self.get_ohlcv(symbol, timeframe='1d', limit=30)
            if ohlcv is None:
                return None
                
            latest_close = ohlcv['close'].iloc[-1]
            
            levels = {
                'support_1': ohlcv['low'].tail(7).min(),
                'support_2': ohlcv['low'].tail(14).min(),
                'resistance_1': ohlcv['high'].tail(7).max(),
                'resistance_2': ohlcv['high'].tail(14).max(),
                'current_price': latest_close
            }
            
            return levels
            
        except Exception as e:
            print(f"Error calculating price levels: {str(e)}")
            return None
