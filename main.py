from app.youtube_data import YouTubeData
from app.sentiment_analyzer import SentimentAnalyzer

url = "https://www.youtube.com/watch?v=hXdLpnvbixs"

dataset = YouTubeData(url)

# Collect YouTube video details
info = dataset.get_video_info()
comments = dataset.get_comments()

sentiment_analyzer = SentimentAnalyzer(comments)

# Collect Sentiment Analysis report
sentiments = sentiment_analyzer.analyze_sentiment()

print(sentiments)
