import time
import threading
from datetime import datetime
from typing import List, Dict

class SignalMonitor:
    def __init__(self, exchange_handler, technical_analyzer, signal_generator, telegram_notifier, pairs: List[str]):
        self.exchange_handler = exchange_handler
        self.technical_analyzer = technical_analyzer
        self.signal_generator = signal_generator
        self.telegram_notifier = telegram_notifier
        self.pairs = pairs
        self.is_running = False
        self.check_interval = 300  # 5 minutes
        self.monitor_thread = None

    def start(self):
        """Start signal monitoring"""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("Signal monitoring started")

    def stop(self):
        """Stop signal monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            print("Signal monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                self._check_signals()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)  # Wait before retry

    def _check_signals(self):
        """Check for signals across all pairs"""
        for pair in self.pairs:
            try:
                # Get market data
                data = self.exchange_handler.get_ohlcv(pair)
                if data is None:
                    continue

                # Get price levels
                price_levels = self.exchange_handler.calculate_price_levels(pair)
                if price_levels is None:
                    continue

                # Generate technical signals
                technical_signals = self.technical_analyzer.generate_signals(data)
                
                # Generate trading signal
                signal = self.signal_generator.generate_signal(
                    pair=pair,
                    technical_signals=technical_signals,
                    price_levels=price_levels
                )

                # If signal generated, send notification
                if signal:
                    # Prepare indicators info
                    latest_data = data.iloc[-1]
                    indicators = {
                        'RSI': latest_data.get('rsi', 0),
                        'MACD': latest_data.get('macd', 0),
                        'Signal': latest_data.get('macd_signal', 0)
                    }

                    # Send notification
                    self.telegram_notifier.send_trading_signal(
                        pair=signal['pair'],
                        signal_type=signal['type'],
                        entry_price=signal['entry'],
                        targets=signal['targets'],
                        stop_loss=signal['stop_loss'],
                        indicators=indicators
                    )

            except Exception as e:
                print(f"Error checking signals for {pair}: {str(e)}")
