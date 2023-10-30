from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import re
from textblob import TextBlob
import streamlit as st


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

    def __init__(self, comments_df):
        self.comments_df = comments_df
        self.tfidf = TfidfVectorizer(strip_accents=None, lowercase=False, preprocessor=None)

    def analyze_sentiment(self):
        self.comments_df['comment'] = self.comments_df['comment'].apply(clean_data)
        self.comments_df['subjectivity'] = self.comments_df['comment'].apply(get_subjectivity)
        self.comments_df['polarity'] = self.comments_df['comment'].apply(get_polarity)
        self.comments_df['analysis'] = self.comments_df['polarity'].apply(get_analysis)

        return self.comments_df

    def show_report_table(self):
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
        st.write("\n")
        # Result in tabular form
        st.dataframe(self.comments_df[["comment", "subjectivity", "polarity", "analysis"]])