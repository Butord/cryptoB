from datetime import datetime
import numpy as np

class SignalGenerator:
    def __init__(self):
        self.signals = []
        self.min_signal_interval = 3600  # minimum seconds between signals for same pair

    def generate_signal(self, pair, technical_signals, price_levels, news_sentiment=None):
        """Generate trading signal based on technical and optional news analysis"""
        current_time = datetime.now()
        
        # Check if we recently generated a signal for this pair
        if self._check_recent_signal(pair, current_time):
            return None
            
        signal = self._analyze_signals(technical_signals, price_levels, news_sentiment)
        
        if signal:
            signal['pair'] = pair
            signal['timestamp'] = current_time
            self.signals.append(signal)
            return signal
            
        return None

    def _check_recent_signal(self, pair, current_time):
        """Check if we have generated a signal for this pair recently"""
        if not self.signals:
            return False
            
        recent_signals = [s for s in self.signals if s['pair'] == pair]
        if recent_signals:
            last_signal_time = recent_signals[-1]['timestamp']
            time_diff = (current_time - last_signal_time).total_seconds()
            return time_diff < self.min_signal_interval
            
        return False

    def _analyze_signals(self, technical_signals, price_levels, news_sentiment):
        """Analyze all signals and generate trading recommendation"""
        if not technical_signals:
            return None
            
        # Count buy and sell signals
        buy_signals = len([s for s in technical_signals if s[2] == "BUY"])
        sell_signals = len([s for s in technical_signals if s[2] == "SELL"])
        
        # Calculate signal strength
        total_signals = len(technical_signals)
        buy_strength = buy_signals / total_signals
        sell_strength = sell_signals / total_signals
        
        # Consider news sentiment if available
        if news_sentiment is not None:
            if news_sentiment > 0:
                buy_strength += 0.2
            elif news_sentiment < 0:
                sell_strength += 0.2
        
        # Generate signal if strength is significant
        signal = None
        if buy_strength > 0.6:
            signal = self._generate_buy_signal(price_levels)
        elif sell_strength > 0.6:
            signal = self._generate_sell_signal(price_levels)
            
        return signal

    def _generate_buy_signal(self, price_levels):
        """Generate buy signal with entry, targets and stop loss"""
        current_price = price_levels['current_price']
        
        # Calculate targets and stop loss
        target_1 = current_price * 1.02  # 2% profit
        target_2 = current_price * 1.04  # 4% profit
        target_3 = current_price * 1.06  # 6% profit
        stop_loss = current_price * 0.98  # 2% loss
        
        return {
            'type': 'BUY',
            'entry': current_price,
            'targets': [target_1, target_2, target_3],
            'stop_loss': stop_loss,
            'risk_reward': (target_2 - current_price) / (current_price - stop_loss)
        }

    def _generate_sell_signal(self, price_levels):
        """Generate sell signal with entry, targets and stop loss"""
        current_price = price_levels['current_price']
        
        # Calculate targets and stop loss
        target_1 = current_price * 0.98  # 2% profit
        target_2 = current_price * 0.96  # 4% profit
        target_3 = current_price * 0.94  # 6% profit
        stop_loss = current_price * 1.02  # 2% loss
        
        return {
            'type': 'SELL',
            'entry': current_price,
            'targets': [target_1, target_2, target_3],
            'stop_loss': stop_loss,
            'risk_reward': (current_price - target_2) / (stop_loss - current_price)
        }
