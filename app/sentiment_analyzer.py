from transformers import pipeline, RobertaForSequenceClassification, RobertaTokenizer


class SentimentAnalyzer:

    def __init__(self, data):
        self.data = data
        self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        self.model = RobertaForSequenceClassification.from_pretrained("roberta-base")
        self.sentiment_analysis = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)

    def analyze_sentiment(self):
        sentiments = []

        for comment_data in self.data:
            comment_text = comment_data['comment']['text']
            inputs = self.tokenizer(comment_text, return_tensors="pt")
            outputs = self.model(**inputs)
            logits = outputs.logits
            predicted_class = logits.argmax().item()
            sentiment_label = "POSITIVE" if predicted_class == 1 else "NEGATIVE"
            confidence = logits.softmax(dim=1)[0][predicted_class].item()

            sentiments.append({
                'text': comment_text,
                'sentiment': sentiment_label,
                'confidence': confidence
            })

        return sentiments
