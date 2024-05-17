import os
import pickle

import altair as alt
import nltk
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import re

from app.utility import new_line

nltk.download('stopwords')

model_path = os.path.join(os.path.dirname(__file__), '../train/yt_model.h5')
tokenizer_path = os.path.join(os.path.dirname(__file__), '../train/tokenizer.pkl')


def clean_data(comment):
    text = re.sub(r'http\S+', '', comment)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    text = text.split()
    stop_words = set(stopwords.words('english'))
    text = [word for word in text if word not in stop_words]
    text = ' '.join(text)
    return text


class SentimentAnalyzer:

    def __init__(self):
        self.comments_df = None
        self.replies_df = None
        # Load model
        self.model = load_model(model_path)

        # Load tokenizer
        with open(tokenizer_path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    def get_sentiments(self, texts):
        texts_cleaned = [clean_data(text) for text in texts]
        texts_tokenized = self.tokenizer.texts_to_sequences(texts_cleaned)
        texts_padded = pad_sequences(texts_tokenized, maxlen=self.model.input_shape[1])
        predictions = self.model.predict(texts_padded, verbose=0)
        labels = np.argmax(predictions, axis=1)
        sentiment_map = {-1: 'Negative', 0: 'Neutral', 1: 'Positive'}
        predicted_sentiments = [sentiment_map[label - 1] for label in labels]
        return predicted_sentiments

    def set_data(self, comments_df, replies_df):
        """
        :param comments_df: Comments dataframe
        :param replies_df: Replies dataframe
        """
        self.comments_df = comments_df
        self.replies_df = replies_df

    def analyze_sentiment(self):
        self.comments_df['comment'] = self.comments_df['comment'].apply(
            clean_data)
        self.comments_df['analysis'] = self.get_sentiments(self.comments_df['comment'])

        return self.comments_df

    def show_report_and_plot(self):
        """
        Plots sentiment analysis result on a chart
        :return: None
        """
        st.markdown("##### Sentiment Analysis Results")

        # Calculate the percentage & display pie chart
        sentiment_counts = self.comments_df['analysis'].value_counts()

        total_comments = len(self.comments_df)
        percentage_positive = (sentiment_counts.get(
            "Positive", 0) / total_comments) * 100
        percentage_negative = (sentiment_counts.get(
            "Negative", 0) / total_comments) * 100
        percentage_neutral = (sentiment_counts.get(
            "Neutral", 0) / total_comments) * 100

        st.caption("The breakdown of user comments with positive, negative, and neutral sentiments "
                   "helps to understand the overall tone of audience interactions.")
        fig = px.pie(
            values=[percentage_positive,
                    percentage_negative, percentage_neutral],
            names=['Positive', 'Negative', 'Neutral'],
            labels={'label': 'Sentiment'},
            color_discrete_sequence=[
                "#1F77B4",
                "#AEC7E8",
                "#FF5252",
            ],
        )
        st.plotly_chart(fig)

        st.markdown("###### Sentiment Analysis Breakdown")
        st.caption(
            "Delve into the key takeaways from this table, which summarizes the sentiment—positive, negative, "
            "or neutral—gleaned from analyzing YouTube comments.")
        new_line(2)
        # Result in tabular form
        st.dataframe(
            self.comments_df[["comment", "analysis"]])
        new_line(4)

        st.markdown("###### Sentiment Distribution")
        st.caption(
            "This bar chart reveals the count of positive, negative, and neutral comments.")
        new_line(2)

        # Create a bar chart
        chart = alt.Chart(self.comments_df).mark_bar().encode(
            x='analysis:N',
            y='count():Q',
            color=alt.Color('analysis:N', scale=alt.Scale(
                domain=['Positive', 'Neutral', 'Negative'],
                range=['#1F77B4', '#AEC7E8', '#FF5252']
            )),
        )
        # Display the bar chart
        st.altair_chart(chart, use_container_width=True)
        new_line(3)

        st.markdown("###### Sentiment Over Time")
        st.caption(
            "This line chart illustrates changes in positive, negative, and neutral comments over time.")
        new_line()

        # Group by timestamp and sentiment analysis, then count the occurrences
        grouped_df = self.comments_df.groupby(
            ['timestamp', 'analysis']).size().reset_index(name='count')
        # Pivot the DataFrame to have separate columns for positive, negative, and neutral counts
        pivot_df = grouped_df.pivot_table(index='timestamp', columns='analysis', values='count',
                                          fill_value=0).reset_index()

        # Resample the DataFrame to have daily counts
        resampled_df = pivot_df.resample(
            'M', on='timestamp').sum().reset_index()
        melted_df = pd.melt(resampled_df, id_vars=['timestamp'], value_vars=['Positive', 'Neutral', 'Negative'],
                            var_name='Sentiment', value_name='Count')

        # Create & display line chart
        overall_sentiment = alt.Chart(melted_df).mark_line().encode(
            x='timestamp:T',
            y='Count:Q',
            color=alt.Color('Sentiment:N', scale=alt.Scale(
                domain=['Positive', 'Neutral', 'Negative'],
                range=['#1F77B4', '#AEC7E8', '#FF5252']
            )),
            tooltip=['timestamp:T', 'Count:Q', 'Sentiment:N']
        ).interactive()

        positive_sentiment = alt.Chart(melted_df[melted_df['Sentiment'] == 'Positive']).mark_line().encode(
            x='timestamp:T',
            y='Count:Q',
            color=alt.value('#1F77B4'),
        ).interactive()

        negative_sentiment = alt.Chart(melted_df[melted_df['Sentiment'] == 'Negative']).mark_line().encode(
            x='timestamp:T',
            y='Count:Q',
            color=alt.value('#FF5252'),
        ).interactive()

        neutral_sentiment = alt.Chart(melted_df[melted_df['Sentiment'] == 'Neutral']).mark_line().encode(
            x='timestamp:T',
            y='Count:Q',
            color=alt.value('#AEC7E8'),
        ).interactive()

        # Create 4 columns as tabs
        col1, col2, col3, col4 = st.tabs(
            ["Overall", "Positive", "Neutral", "Negative"])

        # Display charts based on the selected tab
        with col1:
            st.altair_chart(overall_sentiment, use_container_width=True)
        with col2:
            st.altair_chart(positive_sentiment, use_container_width=True)
        with col3:
            st.altair_chart(neutral_sentiment, use_container_width=True)
        with col4:
            st.altair_chart(negative_sentiment, use_container_width=True)
