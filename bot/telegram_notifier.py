import telegram
import asyncio
from datetime import datetime

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        self.enabled = False

        if token and chat_id:
            try:
                self.bot = telegram.Bot(token=token)
                self.enabled = True
            except Exception as e:
                print(f"Error initializing Telegram bot: {str(e)}")
                print("Telegram notifications will be disabled")

    async def send_message(self, message):
        """Send message to Telegram channel"""
        if not self.enabled:
            print("Telegram notifications are disabled")
            return

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Error sending Telegram message: {str(e)}")

    def send_trading_signal(self, pair, signal_type, entry_price, targets, stop_loss, indicators=None, news_sentiment=None):
        """Send trading signal with formatted message"""
        if not self.enabled:
            print("Telegram notifications are disabled")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"🚨 <b>Trading Signal</b> 🚨\n\n"
        message += f"📊 Pair: {pair}\n"
        message += f"⚡ Signal: {signal_type}\n"
        message += f"💰 Entry Price: {entry_price:.8f}\n\n"

        message += "🎯 Targets:\n"
        for i, target in enumerate(targets, 1):
            message += f"   Target {i}: {target:.8f}\n"

        message += f"\n🛑 Stop Loss: {stop_loss:.8f}\n\n"

        if indicators:
            message += "📈 Technical Indicators:\n"
            for indicator, value in indicators.items():
                if indicator == 'RSI':
                    message += f"   RSI: {value:.2f} ({'Oversold' if value < 30 else 'Overbought' if value > 70 else 'Neutral'})\n"
                elif indicator == 'MACD':
                    message += f"   MACD: {value:.8f}\n"
                elif indicator == 'Signal':
                    message += f"   Signal Line: {value:.8f}\n"
                else:
                    message += f"   {indicator}: {value}\n"

        if news_sentiment is not None:
            sentiment_emoji = "😊" if news_sentiment > 0 else "😐" if news_sentiment == 0 else "😟"
            message += f"\n📰 News Sentiment: {sentiment_emoji} {news_sentiment:.2f}\n"

        message += f"\n⚠️ This is using Binance Testnet data\n"
        message += f"\n⏰ Time: {timestamp}"

        # Send message asynchronously
        asyncio.run(self.send_message(message))

    def send_error(self, error_message):
        """Send error message to Telegram"""
        if not self.enabled:
            return
        message = f"❌ Error:\n{error_message}"
        asyncio.run(self.send_message(message))

    def send_status_update(self, status_message):
        """Send status update to Telegram"""
        if not self.enabled:
            return
        message = f"ℹ️ Status Update:\n{status_message}"
        asyncio.run(self.send_message(message))