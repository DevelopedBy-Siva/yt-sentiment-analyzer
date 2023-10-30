from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import re
from textblob import TextBlob
import streamlit as st
import altair as alt
import pandas as pd
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
        st.markdown("##### Sentiment Analysis Results")
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
        new_line(3)

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
        new_line(4)

        st.markdown("###### Sentiment Over Time")
        new_line(3)

        # Group by timestamp and sentiment analysis, then count the occurrences
        grouped_df = self.comments_df.groupby(['timestamp', 'analysis']).size().reset_index(name='count')
        # Pivot the DataFrame to have separate columns for positive, negative, and neutral counts
        pivot_df = grouped_df.pivot_table(index='timestamp', columns='analysis', values='count',
                                          fill_value=0).reset_index()

        # Resample the DataFrame to have daily counts
        resampled_df = pivot_df.resample('M', on='timestamp').sum().reset_index()
        melted_df = pd.melt(resampled_df, id_vars=['timestamp'], value_vars=['Positive', 'Neutral', 'Negative'],
                            var_name='Sentiment', value_name='Count')

        # Create & display line chart for
        chart_sentiment_analysis = alt.Chart(melted_df).mark_line().encode(
            x='timestamp:T',
            y='Count:Q',
            color=alt.Color('Sentiment:N', scale=alt.Scale(
                domain=['Positive', 'Neutral', 'Negative'],
                range=['#1F77B4', '#AEC7E8', '#FF5252']
            )),
            tooltip=['timestamp:T', 'Count:Q', 'Sentiment:N']
        ).interactive()

        st.altair_chart(chart_sentiment_analysis, use_container_width=True)
