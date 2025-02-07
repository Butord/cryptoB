import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
from bot.analysis import TechnicalAnalyzer
from bot.news_analyzer import NewsAnalyzer
from bot.telegram_notifier import TelegramNotifier
from bot.exchange_handler import ExchangeHandler
from bot.signal_generator import SignalGenerator
from bot.database import init_db, db_session
from bot.models import BotSettings, TradingSignal
from utils.logger import setup_logger

logger = setup_logger()

def load_settings_from_db():
    """Load settings from database"""
    settings = BotSettings.query.first()
    if not settings:
        return {}
    return settings.to_dict()

def save_settings_to_db(config):
    """Save settings to database"""
    settings = BotSettings.query.first()
    if not settings:
        settings = BotSettings(**config)
        db_session.add(settings)
    else:
        for key, value in config.items():
            setattr(settings, key, value)
    db_session.commit()

def save_signal_to_db(signal_data, pair, technical_indicators=None, news_sentiment=None):
    """Save trading signal to database"""
    signal = TradingSignal(
        pair=pair,
        signal_type=signal_data['type'],
        entry_price=signal_data['entry'],
        target_1=signal_data['targets'][0],
        target_2=signal_data['targets'][1],
        target_3=signal_data['targets'][2],
        stop_loss=signal_data['stop_loss'],
        rsi_value=technical_indicators.get('RSI') if technical_indicators else None,
        macd_value=technical_indicators.get('MACD') if technical_indicators else None,
        news_sentiment=news_sentiment
    )
    db_session.add(signal)
    db_session.commit()
    return signal

def main():
    st.set_page_config(page_title="Crypto Trading Bot", layout="wide")
    st.title("🤖 Crypto Trading Bot")

    # Initialize database
    init_db()

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # Load settings from database
    settings = load_settings_from_db()

    # Exchange settings
    st.sidebar.subheader("Exchange Settings")
    exchange = st.sidebar.selectbox("Select Exchange", 
                                  ["binance", "kucoin", "bitfinex"],
                                  index=["binance", "kucoin", "bitfinex"].index(settings.get('exchange', 'binance')))
    trading_pairs = st.sidebar.text_input("Trading Pairs (comma-separated)", 
                                        value=settings.get('trading_pairs', 'BTC/USDT,ETH/USDT'))

    # Technical Analysis Settings
    st.sidebar.subheader("Technical Analysis")
    rsi_period = st.sidebar.slider("RSI Period", 7, 21, settings.get('rsi_period', 14))
    macd_fast = st.sidebar.slider("MACD Fast", 8, 20, settings.get('macd_fast', 12))
    macd_slow = st.sidebar.slider("MACD Slow", 21, 30, settings.get('macd_slow', 26))
    macd_signal = st.sidebar.slider("MACD Signal", 5, 12, settings.get('macd_signal', 9))

    # News Analysis Settings
    st.sidebar.subheader("News Analysis")
    enable_news = st.sidebar.checkbox("Enable News Analysis", settings.get('enable_news', False))

    # Telegram Settings
    st.sidebar.subheader("Telegram Notifications")
    telegram_token = st.sidebar.text_input("Telegram Bot Token", 
                                         value=settings.get('telegram_token', ''), 
                                         type="password")
    telegram_chat_id = st.sidebar.text_input("Telegram Chat ID", 
                                           value=settings.get('telegram_chat_id', ''))

    # Save configuration button
    if st.sidebar.button("Save Configuration"):
        config = {
            'exchange': exchange,
            'trading_pairs': trading_pairs,
            'rsi_period': rsi_period,
            'macd_fast': macd_fast,
            'macd_slow': macd_slow,
            'macd_signal': macd_signal,
            'enable_news': enable_news,
            'telegram_token': telegram_token,
            'telegram_chat_id': telegram_chat_id
        }
        save_settings_to_db(config)
        st.sidebar.success("Configuration saved!")

    # Main content area
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Active Trading Pairs")
        for pair in trading_pairs.split(","):
            st.write(f"📊 {pair.strip()}")

    with col2:
        st.subheader("Bot Status")
        status = st.empty()
        status.success("Bot is running")

    # Initialize components
    exchange_handler = ExchangeHandler(exchange)
    technical_analyzer = TechnicalAnalyzer(
        rsi_period=rsi_period,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )

    if enable_news:
        news_analyzer = NewsAnalyzer()

    telegram_notifier = TelegramNotifier(telegram_token, telegram_chat_id)
    signal_generator = SignalGenerator()

    # Display latest signals
    st.subheader("Latest Signals")
    signals_container = st.empty()

    # Get latest signals from database
    latest_signals = TradingSignal.query.order_by(TradingSignal.created_at.desc()).limit(5).all()
    if latest_signals:
        signals_df = pd.DataFrame([signal.to_dict() for signal in latest_signals])
        signals_container.dataframe(signals_df)
    else:
        signals_container.info("No signals generated yet")

    # Display charts
    st.subheader("Market Analysis")
    chart_placeholder = st.empty()

    def plot_analysis(pair):
        data = exchange_handler.get_ohlcv(pair)
        if data is not None:
            fig = go.Figure()

            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='OHLCV'
            ))

            # Add technical indicators
            technical_analyzer.add_indicators_to_plot(fig, data)

            fig.update_layout(
                title=f'{pair} Analysis',
                yaxis_title='Price',
                xaxis_title='Date',
                template='plotly_dark'
            )

            return fig

    # Display chart for first trading pair
    first_pair = trading_pairs.split(",")[0].strip()
    try:
        chart = plot_analysis(first_pair)
        if chart:
            chart_placeholder.plotly_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting chart: {str(e)}")

if __name__ == "__main__":
    main()