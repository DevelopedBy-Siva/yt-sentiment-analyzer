import pandas as pd
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, SpatialDropout1D
from keras.callbacks import ModelCheckpoint, EarlyStopping

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

checkpoint = ModelCheckpoint('model_checkpoint.h5', monitor='val_loss', mode='min', save_best_only=True, verbose=1)
early_stopping = EarlyStopping(monitor='val_loss', patience=3, verbose=1)

# Train the model
batch_size = 32
epochs = 5

history = model.fit(
    X_train, y_train,
    epochs=epochs,
    batch_size=batch_size,
    validation_data=(X_test, y_test),
    callbacks=[checkpoint, early_stopping],
    verbose=1
)

score, acc = model.evaluate(X_test, y_test, verbose=2, batch_size=batch_size)
print("Test Score:", score)
print("Test Accuracy:", acc)

# Save the model
model.save('yt_model.keras')
