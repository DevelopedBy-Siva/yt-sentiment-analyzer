import pickle

import pandas as pd
from keras.layers import Embedding, LSTM, Dense, SpatialDropout1D
from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split

# Load dataset: Dataset already cleaned-> ./data/classify_data.py
data = pd.read_csv('data/dataset.csv', encoding='ISO-8859-1', header=0)
# Remove rows where 'comment' is NaN
data = data.dropna(subset=['comment'])

print(data.head())

# Tokenize text
tokenizer = Tokenizer(num_words=5000, split=' ')
tokenizer.fit_on_texts(data['comment'].values)
X = tokenizer.texts_to_sequences(data['comment'].values)
X = pad_sequences(X)

y = pd.get_dummies(data['sentiment']).values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build LSTM model
model = Sequential()
model.add(Embedding(input_dim=5000, output_dim=128, input_length=X.shape[1]))
model.add(SpatialDropout1D(0.2))
model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(3, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
batch_size = 64
epochs = 20

history = model.fit(
    X_train, y_train,
    epochs=epochs,
    batch_size=batch_size,
    validation_data=(X_test, y_test),
    verbose=1
)

score, acc = model.evaluate(X_test, y_test, verbose=2, batch_size=batch_size)
print("Test Score:", score)
print("Test Accuracy:", acc)

# Save model
model.save('yt_model.h5')

# Save tokenizer
with open('tokenizer.pkl', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
