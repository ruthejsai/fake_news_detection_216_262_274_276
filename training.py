# -*- coding: utf-8 -*-
"""training.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19qUFumLEqi1E0ZCqyA_lDe4cRIp_cS-Q
"""

import pandas as pd
import numpy as np
import re
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load the dataset
data = pd.read_csv('political_fact_checker.csv')

# Cleaning the text data
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()
    return text

data['statement'] = data['statement'].apply(clean_text)

# Tokenization and sequence padding
tokenizer = Tokenizer()
tokenizer.fit_on_texts(data['statement'])
sequences = tokenizer.texts_to_sequences(data['statement'])
X = pad_sequences(sequences, maxlen=100)

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(data['target'])

# Splitting the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preparing the embedding layer with GloVe or other pre-trained word embeddings
embedding_matrix = np.zeros((len(tokenizer.word_index) + 1, 300))  # Change dimensions as per your embeddings

# Model architecture
model = Sequential([
    Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=300,
              embeddings_initializer='uniform', input_length=100, trainable=False),
    Bidirectional(LSTM(128, return_sequences=True)),
    Dropout(0.5),
    Bidirectional(LSTM(64)),
    Dropout(0.5),
    Dense(len(label_encoder.classes_), activation='softmax')
])

# Model compilation
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Callbacks for early stopping and model checkpointing
early_stopping = EarlyStopping(monitor='val_loss', patience=5)
model_checkpoint = ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_loss', mode='min')

# Training the model
model.fit(X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping, model_checkpoint])

# Loading the best model and evaluating
model.load_weights('best_model.h5')
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test accuracy: {accuracy*100:.2f}%")

from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer

# Load the trained model
model = load_model('best_model.h5')

# Function to preprocess user input
def preprocess_input(statement):
    # Clean the text
    statement = clean_text(statement)
    # Tokenize and pad the sequence
    sequence = tokenizer.texts_to_sequences([statement])
    padded_sequence = pad_sequences(sequence, maxlen=100)
    return padded_sequence

# Function to predict label for user input
def predict_label(statement):
    preprocessed_input = preprocess_input(statement)
    prediction = model.predict(preprocessed_input)
    label_index = np.argmax(prediction)
    confidence = prediction[0][label_index]
    label = label_encoder.inverse_transform([label_index])[0]
    return label, confidence

# User input
user_input = input("Enter a political news statement: ")

# Make prediction
predicted_label, confidence = predict_label(user_input)
print(f"Predicted Label: {predicted_label} (Confidence: {confidence * 100:.2f}%)")
