from transformers import pipeline


class SentimentAnalyzer:

    def __init__(self, data):
        self.data = data
        self.sentiment_analysis = pipeline("sentiment-analysis")

    def analyze_sentiment(self):
        sentiments = []

        for comment_data in self.data:
            comment_text = comment_data['comment']['text']
            comment_sentiment = self.sentiment_analysis(comment_text)
            sentiments.append({
                'text': comment_text,
                'sentiment': comment_sentiment[0]['label'],
                'confidence': comment_sentiment[0]['score']
            })

        return sentiments
