import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple

class TechnicalAnalyzer:
    def __init__(self, rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9):
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def calculate_rsi(self, data: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, data: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        exp1 = data.ewm(span=self.macd_fast).mean()
        exp2 = data.ewm(span=self.macd_slow).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.macd_signal).mean()
        hist = macd - signal
        return macd, signal, hist

    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()

    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period).mean()

    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        middle_band = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        return upper_band, middle_band, lower_band

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the given dataframe"""
        try:
            # RSI
            df['rsi'] = self.calculate_rsi(df['close'], self.rsi_period)

            # MACD
            df['macd'], df['macd_signal'], df['macd_hist'] = self.calculate_macd(df['close'])

            # Moving Averages
            df['sma_20'] = self.calculate_sma(df['close'], 20)
            df['sma_50'] = self.calculate_sma(df['close'], 50)
            df['ema_20'] = self.calculate_ema(df['close'], 20)

            # Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = self.calculate_bollinger_bands(df['close'])

            return df
        except Exception as e:
            raise Exception(f"Error calculating indicators: {str(e)}")

    def add_indicators_to_plot(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add technical indicators to the plotly figure"""
        # Calculate indicators
        df = self.calculate_indicators(df)

        # Add Moving Averages
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_20'],
            name='SMA 20',
            line=dict(color='yellow', width=1)
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_50'],
            name='SMA 50',
            line=dict(color='orange', width=1)
        ))

        # Add Bollinger Bands
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['bb_upper'],
            name='BB Upper',
            line=dict(color='gray', width=1, dash='dash')
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['bb_lower'],
            name='BB Lower',
            line=dict(color='gray', width=1, dash='dash'),
            fill='tonexty'
        ))

        # Create subplot for RSI
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['rsi'],
            name='RSI',
            yaxis="y2"
        ))

        # Create subplot for MACD
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['macd'],
            name='MACD',
            yaxis="y3"
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['macd_signal'],
            name='Signal',
            yaxis="y3"
        ))

        # Update layout for subplots
        fig.update_layout(
            yaxis2=dict(
                title="RSI",
                anchor="free",
                overlaying="y",
                side="right",
                position=1
            ),
            yaxis3=dict(
                title="MACD",
                anchor="free",
                overlaying="y",
                side="right",
                position=0.85
            )
        )

    def generate_signals(self, df: pd.DataFrame) -> List[Tuple[str, str, str]]:
        """Generate trading signals based on technical indicators"""
        signals = []
        df = self.calculate_indicators(df)

        # Get the latest data point
        latest = df.iloc[-1]

        # RSI signals
        if latest['rsi'] < 30:
            signals.append(("RSI", "Oversold", "BUY"))
        elif latest['rsi'] > 70:
            signals.append(("RSI", "Overbought", "SELL"))

        # MACD signals
        if latest['macd'] > latest['macd_signal'] and df.iloc[-2]['macd'] <= df.iloc[-2]['macd_signal']:
            signals.append(("MACD", "Bullish Crossover", "BUY"))
        elif latest['macd'] < latest['macd_signal'] and df.iloc[-2]['macd'] >= df.iloc[-2]['macd_signal']:
            signals.append(("MACD", "Bearish Crossover", "SELL"))

        # Moving Average signals
        if latest['close'] > latest['sma_20'] and df.iloc[-2]['close'] <= df.iloc[-2]['sma_20']:
            signals.append(("MA", "Price crossed above SMA20", "BUY"))
        elif latest['close'] < latest['sma_20'] and df.iloc[-2]['close'] >= df.iloc[-2]['sma_20']:
            signals.append(("MA", "Price crossed below SMA20", "SELL"))

        return signals