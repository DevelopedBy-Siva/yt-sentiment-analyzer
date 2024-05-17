import pandas as pd
from textblob import TextBlob
import re
import nltk
from nltk.corpus import stopwords
import zipfile

nltk.download('stopwords')

with zipfile.ZipFile('old_dataset.csv.zip', 'r') as zip_ref:
    zip_ref.extractall()

# Load dataset
df = pd.read_csv('old_dataset.csv', encoding='ISO-8859-1', header=None)
df.columns = ['target', 'ids', 'date', 'flag', 'user', 'text']


def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    text = text.split()
    stop_words = set(stopwords.words('english'))
    text = [word for word in text if word not in stop_words]
    text = ' '.join(text)
    return text


df['cleaned_text'] = df['text'].apply(clean_text)


# find sentiment
def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1


df['sentiment'] = df['cleaned_text'].apply(get_sentiment)
new_df = df[['cleaned_text', 'sentiment']].rename(columns={'cleaned_text': 'comment'})
new_df.to_csv('dataset.csv', index=False)

print(new_df.head())
