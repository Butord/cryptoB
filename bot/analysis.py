import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

class TechnicalAnalyzer:
    def __init__(self, rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9):
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def calculate_indicators(self, df):
        """Calculate technical indicators for the given dataframe"""
        try:
            # RSI
            df['rsi'] = ta.rsi(df['close'], length=self.rsi_period)

            # MACD
            macd = ta.macd(
                df['close'],
                fast=self.macd_fast,
                slow=self.macd_slow,
                signal=self.macd_signal
            )
            df['macd'] = macd['MACD_' + str(self.macd_fast) + '_' + str(self.macd_slow) + '_' + str(self.macd_signal)]
            df['macd_signal'] = macd['MACDs_' + str(self.macd_fast) + '_' + str(self.macd_slow) + '_' + str(self.macd_signal)]
            df['macd_hist'] = macd['MACDh_' + str(self.macd_fast) + '_' + str(self.macd_slow) + '_' + str(self.macd_signal)]

            # Moving Averages
            df['sma_20'] = ta.sma(df['close'], length=20)
            df['sma_50'] = ta.sma(df['close'], length=50)
            df['ema_20'] = ta.ema(df['close'], length=20)

            # Bollinger Bands
            bb = ta.bbands(df['close'], length=20)
            df['bb_upper'] = bb['BBU_20_2.0']
            df['bb_middle'] = bb['BBM_20_2.0']
            df['bb_lower'] = bb['BBL_20_2.0']

            return df
        except Exception as e:
            raise Exception(f"Error calculating indicators: {str(e)}")

    def add_indicators_to_plot(self, fig, df):
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

    def generate_signals(self, df):
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