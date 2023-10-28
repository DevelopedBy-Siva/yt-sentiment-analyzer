from sklearn.feature_extraction.text import re


def clean_data(comment):
    no_punc = re.sub(r'[^\w\s]', '', comment)
    no_digits = ''.join([i for i in no_punc if not i.isdigit()])
    return no_digits


class SentimentAnalyzer:

    def __init__(self, comments_df):
        self.comments_df = comments_df

    def analyze_sentiment(self):

        self.comments_df['comment'] = self.comments_df['comment'].apply(clean_data)
        print(self.comments_df.loc[0, 'comment'])
        pass
