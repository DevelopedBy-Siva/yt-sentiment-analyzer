import streamlit as st
import time
from app.youtube_data import YouTubeData
from app.sentiment_analyzer import SentimentAnalyzer
from app.utility import new_line, parse_info

# Configure the page
st.set_page_config(page_title="YouTube Sentiment Analyzer", page_icon=None, layout="centered")

# App title
st.title(":blue[YouTube Sentiment Analyzer]")
new_line(st)

st.info("The processing time for analysis depends on the size of comments. The more comments there are, "
        "the longer it may take.")
new_line(st)

with st.form(key="input_form"):
    new_line(st)
    yt_url = st.text_input("Enter YouTube URL")
    new_line(st)
    submit_btn = st.form_submit_button("Analyze", use_container_width=True)
    new_line(st)

if submit_btn and yt_url:
    try:
        # StartTime: Calculate process time
        start_time = time.time()

        # Collect YouTube video details
        dataset = YouTubeData(yt_url)
        info = dataset.get_video_info()
        comments = dataset.get_comments()

        # Analyze Sentiment
        sentiment_analyzer = SentimentAnalyzer(comments)
        sentiments = sentiment_analyzer.analyze_sentiment()

        # EndTime: Calculate process time
        end_time = time.time()
        st.success(f"Analysis finished in {round(end_time - start_time, 2)}s")
        new_line(st, 2)

        # Parse and display video info
        parse_info(st, info, len(comments))

    except Exception as ex:
        error_msg = str(ex)
        st.error(error_msg)

