from app.youtube_data import YouTubeData
from app.sentiment_analyzer import SentimentAnalyzer

url = "https://www.youtube.com/watch?v=hXdLpnvbixs"

dataset = YouTubeData(url)

info = dataset.get_video_info()
comments = dataset.get_comments()

sentiment = SentimentAnalyzer(comments)
