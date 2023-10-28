import streamlit as st
from app.youtube_data import YouTubeData
from app.sentiment_analyzer import SentimentAnalyzer

st.title("YouTube Sentiment Analyzer")

yt_url = st.text_input("Enter YouTube URL")


if yt_url:
    # Collect YouTube video details
    dataset = YouTubeData(yt_url)
    info = dataset.get_video_info()

# comments = dataset.get_comments()
#
# sentiment_analyzer = SentimentAnalyzer(comments)
#
# # Collect Sentiment Analysis report
# sentiments = sentiment_analyzer.analyze_sentiment()
#
# print(sentiments)
