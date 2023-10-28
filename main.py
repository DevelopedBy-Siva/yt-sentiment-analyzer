import streamlit as st
from app.youtube_data import YouTubeData
from app.sentiment_analyzer import SentimentAnalyzer
from app.utility import new_line

st.title("YouTube Sentiment Analyzer")
new_line(st, 1)
st.info("The processing time for analysis depends on the size of comments. The more comments there are, "
        "the longer it may take.")
new_line(st, 1)

with st.form(key="input_form"):
    yt_url = st.text_input("Enter YouTube URL")
    submit_btn = st.form_submit_button("Analyze", use_container_width=True)

if submit_btn and yt_url:
    try:
        # Collect YouTube video details
        dataset = YouTubeData(yt_url)
        info = dataset.get_video_info()
    except Exception as ex:
        error_msg = str(ex)
        st.error(error_msg)

# comments = dataset.get_comments()
#
# sentiment_analyzer = SentimentAnalyzer(comments)
#
# # Collect Sentiment Analysis report
# sentiments = sentiment_analyzer.analyze_sentiment()
#
# print(sentiments)
