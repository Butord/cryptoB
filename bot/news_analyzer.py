import requests
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob

class NewsAnalyzer:
    def __init__(self):
        self.crypto_news_api_url = "https://cryptopanic.com/api/v1/posts/"
        self.sentiment_threshold = 0.1

    def fetch_news(self, currency, hours=24):
        """Fetch news for a specific cryptocurrency"""
        try:
            params = {
                "currencies": currency,
                "public": "true",
                "kind": "news"
            }
            
            response = requests.get(self.crypto_news_api_url, params=params)
            if response.status_code == 200:
                news_data = response.json()
                return self._process_news(news_data['results'])
            else:
                return None
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return None

    def _process_news(self, news_items):
        """Process news items and calculate sentiment"""
        processed_news = []
        
        for item in news_items:
            # Calculate sentiment using TextBlob
            blob = TextBlob(item['title'])
            sentiment = blob.sentiment.polarity
            
            processed_news.append({
                'title': item['title'],
                'url': item['url'],
                'published_at': item['published_at'],
                'sentiment': sentiment
            })
            
        return processed_news

    def analyze_sentiment(self, news_items):
        """Analyze overall sentiment from news items"""
        if not news_items:
            return 0
            
        total_sentiment = sum(item['sentiment'] for item in news_items)
        avg_sentiment = total_sentiment / len(news_items)
        
        return avg_sentiment

    def get_trading_signal(self, currency):
        """Generate trading signal based on news sentiment"""
        news_items = self.fetch_news(currency)
        if news_items:
            sentiment = self.analyze_sentiment(news_items)
            
            if sentiment > self.sentiment_threshold:
                return "BUY", sentiment, news_items
            elif sentiment < -self.sentiment_threshold:
                return "SELL", sentiment, news_items
            else:
                return "NEUTRAL", sentiment, news_items
                
        return None, 0, []
