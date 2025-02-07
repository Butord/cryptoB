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
from utils.config import load_config, save_config
from utils.logger import setup_logger

logger = setup_logger()

def main():
    st.set_page_config(page_title="Crypto Trading Bot", layout="wide")
    st.title("🤖 Crypto Trading Bot")

    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Load or initialize configuration
    if 'config' not in st.session_state:
        st.session_state.config = load_config()

    # Exchange settings
    st.sidebar.subheader("Exchange Settings")
    exchange = st.sidebar.selectbox("Select Exchange", ["binance", "kucoin", "bitfinex"])
    trading_pairs = st.sidebar.text_input("Trading Pairs (comma-separated)", 
                                        value=st.session_state.config.get("trading_pairs", "BTC/USDT,ETH/USDT"))

    # Technical Analysis Settings
    st.sidebar.subheader("Technical Analysis")
    rsi_period = st.sidebar.slider("RSI Period", 7, 21, st.session_state.config.get("rsi_period", 14))
    macd_fast = st.sidebar.slider("MACD Fast", 8, 20, st.session_state.config.get("macd_fast", 12))
    macd_slow = st.sidebar.slider("MACD Slow", 21, 30, st.session_state.config.get("macd_slow", 26))
    macd_signal = st.sidebar.slider("MACD Signal", 5, 12, st.session_state.config.get("macd_signal", 9))

    # News Analysis Settings
    st.sidebar.subheader("News Analysis")
    enable_news = st.sidebar.checkbox("Enable News Analysis", st.session_state.config.get("enable_news", False))

    # Telegram Settings
    st.sidebar.subheader("Telegram Notifications")
    telegram_token = st.sidebar.text_input("Telegram Bot Token", 
                                         value=st.session_state.config.get("telegram_token", ""), 
                                         type="password")
    telegram_chat_id = st.sidebar.text_input("Telegram Chat ID", 
                                           value=st.session_state.config.get("telegram_chat_id", ""))

    # Save configuration button
    if st.sidebar.button("Save Configuration"):
        config = {
            "exchange": exchange,
            "trading_pairs": trading_pairs,
            "rsi_period": rsi_period,
            "macd_fast": macd_fast,
            "macd_slow": macd_slow,
            "macd_signal": macd_signal,
            "enable_news": enable_news,
            "telegram_token": telegram_token,
            "telegram_chat_id": telegram_chat_id
        }
        save_config(config)
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
    signals_placeholder = st.empty()

    # Display charts
    st.subheader("Market Analysis")
    chart_placeholder = st.empty()

    # Example visualization
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
