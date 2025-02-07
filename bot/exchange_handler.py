import ccxt
import pandas as pd
from datetime import datetime, timedelta
import os

class ExchangeHandler:
    def __init__(self, exchange_id='binance'):
        self.exchange_id = exchange_id
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')

        # Initialize exchange with API credentials
        exchange_config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'urls': {
                'api': {
                    'public': 'https://testnet.binance.vision/api/v3',
                    'private': 'https://testnet.binance.vision/api/v3',
                    'test': 'https://testnet.binance.vision/api/v3',
                    'fapiPublic': 'https://testnet.binancefuture.com/fapi/v1',
                    'fapiPrivate': 'https://testnet.binancefuture.com/fapi/v1'
                }
            },
            'test': true,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
                'createMarketBuyOrderRequiresPrice': False,
                'recvWindow': 60000,
                'test': True,
                'warnOnFetchOHLCVLimitArgument': False,
                'fetchTrades': {
                    'sort': 'timestamp',
                    'limit': 1000
                }
            },
            'timeout': 30000,
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
                'createMarketBuyOrderRequiresPrice': False,
                'recvWindow': 60000,
            },
            'timeout': 30000,
            'proxies': {
                'http': 'http://proxy.replit.org:8080',
                'https': 'http://proxy.replit.org:8080'
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        try:
            self.exchange = getattr(ccxt, exchange_id)(exchange_config)
            self.exchange.load_markets()
            print(f"Successfully connected to {exchange_id} testnet")
        except Exception as e:
            print(f"Error connecting to {exchange_id}: {str(e)}")
            raise

    def get_ohlcv(self, symbol, timeframe='1h', limit=100):
        """Get OHLCV data for a symbol"""
        try:
            # Add retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    ohlcv = self.exchange.fetch_ohlcv(
                        symbol,
                        timeframe=timeframe,
                        limit=limit
                    )

                    if not ohlcv:
                        raise Exception("Empty OHLCV data received")

                    df = pd.DataFrame(
                        ohlcv,
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    )

                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)

                    return df
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed, retrying...")

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