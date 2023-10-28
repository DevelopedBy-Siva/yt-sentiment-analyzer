import streamlit as st
import time
from app.youtube_data import YouTubeData
from app.sentiment_analyzer import SentimentAnalyzer
from app.utility import new_line, parse_info, parse_comments_dataset, SAMPLE_URL

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
    yt_url = st.text_input("Enter YouTube URL", value=SAMPLE_URL)
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
        # Comments Dataframe
        comments_df = dataset.get_dataframes()[0]
        # Replies Dataframe
        replies_df = dataset.get_dataframes()[1]

        # EndTime: Calculate process time
        end_time = time.time()
        new_line(st)
        st.success(f"Analysis finished in {round(end_time - start_time, 2)}s")
        new_line(st, 2)

        # 1. Parse and display video info
        parse_info(st, info, len(comments_df.index))

        # 2. Parse and display the sample dataset
        parse_comments_dataset(st, comments_df)

        # 3. Analyze the sentiment
        sentiment = SentimentAnalyzer(comments_df)
        sentiment.analyze_sentiment()

    except Exception as ex:
        error_msg = str(ex)
        st.error(error_msg)

