import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import re
from textblob import TextBlob
from app.utility import new_line


def clean_data(comment):
    no_punc = re.sub(r'[^\w\s]', '', comment)
    no_digits = ''.join([i for i in no_punc if not i.isdigit()])
    return no_digits


def get_subjectivity(text):
    return TextBlob(text).sentiment.subjectivity


def get_polarity(text):
    return TextBlob(text).sentiment.polarity


def get_analysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


class SentimentAnalyzer:

    def __init__(self, comments_df, replies_df):
        """
        :param comments_df: Comments dataframe
        :param replies_df: Replies dataframe
        """
        self.comments_df = comments_df
        self.replies_df = replies_df
        self.tfidf = TfidfVectorizer(strip_accents=None, lowercase=False, preprocessor=None)

    def analyze_sentiment(self):
        self.comments_df['comment'] = self.comments_df['comment'].apply(clean_data)
        self.comments_df['subjectivity'] = self.comments_df['comment'].apply(get_subjectivity)
        self.comments_df['polarity'] = self.comments_df['comment'].apply(get_polarity)
        self.comments_df['analysis'] = self.comments_df['polarity'].apply(get_analysis)

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
        percentage_positive = (sentiment_counts.get("Positive", 0) / total_comments) * 100
        percentage_negative = (sentiment_counts.get("Negative", 0) / total_comments) * 100
        percentage_neutral = (sentiment_counts.get("Neutral", 0) / total_comments) * 100

        st.caption("The breakdown of user comments with positive, negative, and neutral sentiments "
                   "helps to understand the overall tone of audience interactions.")
        fig = px.pie(
            values=[percentage_positive, percentage_negative, percentage_neutral],
            names=['Positive', 'Negative', 'Neutral'],
            labels={'label': 'Sentiment'}
        )
        st.plotly_chart(fig)

        st.markdown("###### Sentiment Analysis Breakdown")
        st.caption("Explore the analysis results captured in this table, featuring key insights "
                   "derived from the dataset. The columns include:")
        st.caption('''
            - **Subjectivity** : A measure indicating the extent to which the text expresses personal opinions 
            rather than factual information. 
            - **Polarity** : The measure of the sentiment's degree, ranging from negative to positive.
            - **Analysis** : Categorized sentiment result—whether the sentiment is positive, negative, 
            or neutral.
            ''')
        new_line(2)
        # Result in tabular form
        st.dataframe(self.comments_df[["comment", "subjectivity", "polarity", "analysis"]])
        new_line(4)

        st.markdown("###### Sentiment Distribution")
        st.caption("This bar chart reveals the count of positive, negative, and neutral comments.")
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
        st.caption("This line chart illustrates changes in positive, negative, and neutral comments over time.")
        new_line()

        # Group by timestamp and sentiment analysis, then count the occurrences
        grouped_df = self.comments_df.groupby(['timestamp', 'analysis']).size().reset_index(name='count')
        # Pivot the DataFrame to have separate columns for positive, negative, and neutral counts
        pivot_df = grouped_df.pivot_table(index='timestamp', columns='analysis', values='count',
                                          fill_value=0).reset_index()

        # Resample the DataFrame to have daily counts
        resampled_df = pivot_df.resample('M', on='timestamp').sum().reset_index()
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
        col1, col2, col3, col4 = st.tabs(["Overall", "Positive", "Neutral", "Negative"])

        # Display charts based on the selected tab
        with col1:
            st.altair_chart(overall_sentiment, use_container_width=True)
        with col2:
            st.altair_chart(positive_sentiment, use_container_width=True)
        with col3:
            st.altair_chart(neutral_sentiment, use_container_width=True)
        with col4:
            st.altair_chart(negative_sentiment, use_container_width=True)