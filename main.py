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
from bot.signal_monitor import SignalMonitor # Import SignalMonitor

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
    st.set_page_config(
        page_title="🤖 Crypto Trading Bot",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Встановлюємо тему
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stButton>button {
            background-color: #FF4B4B;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🤖 Crypto Trading Bot")

    try:
        # Initialize database
        init_db()

        # Add warning about testnet
        st.sidebar.markdown("""
        <div style='background-color: #FF4B4B; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
        ⚠️ <b>Важливе попередження</b><br>
        Бот працює в тестовому режимі (Binance Testnet).<br>
        Сигнали генеруються на основі тестових даних і не повинні використовуватися для реальної торгівлі.
        </div>
        """, unsafe_allow_html=True)

        # Sidebar configuration
        st.sidebar.header("⚙️ Налаштування")

        # Load settings from database
        settings = load_settings_from_db()

        # Exchange settings
        st.sidebar.subheader("Налаштування біржі")
        exchange = st.sidebar.selectbox(
            "Виберіть біржу", 
            ["binance", "kucoin", "bitfinex"],
            index=["binance", "kucoin", "bitfinex"].index(settings.get('exchange', 'binance'))
        )

        trading_pairs = st.sidebar.text_input(
            "Торгові пари (через кому)", 
            value=settings.get('trading_pairs', 'BTC/USDT,ETH/USDT')
        )

        # Technical Analysis Settings
        st.sidebar.subheader("📊 Технічний аналіз")
        rsi_period = st.sidebar.slider("RSI період", 7, 21, settings.get('rsi_period', 14))
        macd_fast = st.sidebar.slider("MACD швидка", 8, 20, settings.get('macd_fast', 12))
        macd_slow = st.sidebar.slider("MACD повільна", 21, 30, settings.get('macd_slow', 26))
        macd_signal = st.sidebar.slider("MACD сигнал", 5, 12, settings.get('macd_signal', 9))

        # News Analysis Settings
        st.sidebar.subheader("📰 Аналіз новин")
        enable_news = st.sidebar.checkbox("Включити аналіз новин", settings.get('enable_news', False))

        # Telegram Settings
        st.sidebar.subheader("📱 Налаштування Telegram")
        telegram_token = st.sidebar.text_input(
            "Telegram Bot Token", 
            value=settings.get('telegram_token', ''), 
            type="password"
        )
        telegram_chat_id = st.sidebar.text_input(
            "Telegram Chat ID", 
            value=settings.get('telegram_chat_id', '')
        )

        # Save configuration button
        if st.sidebar.button("💾 Зберегти налаштування"):
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
            st.sidebar.success("✅ Налаштування збережено!")

        # Main content area
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Активні торгові пари")
            for pair in trading_pairs.split(","):
                st.write(f"📈 {pair.strip()}")

        with col2:
            st.subheader("🤖 Статус бота")
            status = st.empty()
            exchange_handler = None
            try:
                exchange_handler = ExchangeHandler(exchange)
                status.success("✅ Бот працює")
            except Exception as e:
                status.error(f"❌ Помилка: {str(e)}")
                return

        # Initialize components
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

        # Initialize signal monitor
        pairs_list = [pair.strip() for pair in trading_pairs.split(",")]
        signal_monitor = SignalMonitor(
            exchange_handler=exchange_handler,
            technical_analyzer=technical_analyzer,
            signal_generator=signal_generator,
            telegram_notifier=telegram_notifier,
            pairs=pairs_list
        )

        # Add signal monitoring control
        st.sidebar.subheader("🔔 Моніторинг сигналів")
        monitor_enabled = st.sidebar.checkbox("Увімкнути моніторинг сигналів", value=False)

        if monitor_enabled:
            signal_monitor.start()
            st.sidebar.success("✅ Моніторинг сигналів активний")
        else:
            signal_monitor.stop()
            st.sidebar.info("ℹ️ Моніторинг сигналів вимкнено")


        # Display latest signals
        st.subheader("📊 Останні сигнали")
        signals_container = st.empty()

        # Get latest signals from database
        latest_signals = TradingSignal.query.order_by(TradingSignal.created_at.desc()).limit(5).all()
        if latest_signals:
            signals_df = pd.DataFrame([signal.to_dict() for signal in latest_signals])
            signals_container.dataframe(signals_df)
        else:
            signals_container.info("Поки що немає сигналів")

        # Display charts
        st.subheader("📈 Аналіз ринку")

        # Add pair selector
        pairs_list = [pair.strip() for pair in trading_pairs.split(",")]
        selected_pair = st.selectbox(
            "Виберіть торгову пару для аналізу",
            pairs_list,
            index=0
        )

        # Add auto-refresh option
        auto_refresh = st.checkbox("🔄 Автоматичне оновлення", value=True)
        if auto_refresh:
            st.empty()  # This will force a rerun every few seconds

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
                    title=f'{pair} Аналіз',
                    yaxis_title='Ціна',
                    xaxis_title='Дата',
                    template='plotly_dark',
                    height=800
                )

                return fig

        # Display chart for selected pair
        try:
            chart = plot_analysis(selected_pair)
            if chart:
                chart_placeholder.plotly_chart(chart, use_container_width=True)
            else:
                chart_placeholder.error(f"❌ Помилка отримання даних для {selected_pair}")
        except Exception as e:
            st.error(f"❌ Помилка побудови графіка: {str(e)}")

    except Exception as e:
        st.error(f"❌ Помилка: {str(e)}")
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()