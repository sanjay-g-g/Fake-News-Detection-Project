# -*- coding: utf-8 -*-
"""Fake_news.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1e8_PhosHMgTZEuJ0Q8yQlLMLjkF10p2Y
"""

# Commented out IPython magic to ensure Python compatibility.
## importing necessary libraries 
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.metrics import confusion_matrix
# %matplotlib inline
import seaborn as sns
import numpy as np
import pandas as pd
import os
import re
import nltk

from google.colab import drive
drive.mount('/content/drive')

data_train=pd.read_csv('/content/drive/My Drive/Fack_news/train.csv')
data_test=pd.read_csv('/content/drive/My Drive/Fack_news/test.csv')

data_train.head()

# importing neural network libraries
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Embedding, GRU, LSTM, RNN, SpatialDropout1D

data_train = data_train.set_index('id', drop = True)

print(data_train.shape)
data_train.head()

# checking for missing values
data_train.isnull().sum()

# dropping missing values from text columns alone. 
data_train[['title', 'author']] = data_train[['title', 'author']].fillna(value = 'Missing')
data_train = data_train.dropna()
data_train.isnull().sum()

length = []
[length.append(len(str(text))) for text in data_train['text']]
data_train['length'] = length
data_train.head()

min(data_train['length']), max(data_train['length']), round(sum(data_train['length'])/len(data_train['length']))

#we can keep 4500 as max features for training the neural network.

#minimum length is 1 ?? Looks like there are some outliers.
len(data_train[data_train['length'] < 50])

#There are 207 outliers in this dataset. Outliers can be removed. It is a good practice to check the outliers before removing them
data_train['text'][data_train['length'] < 50]

# dropping the outliers
data_train = data_train.drop(data_train['text'][data_train['length'] < 50].index, axis = 0)

#Creating Wordcloud Visuals
real_words = ''
fake_words = ''
stopwords = set(STOPWORDS) 
  
# iterate through the csv file 
for val in data_train[data_train['label']==1].text: 
  
    # split the value 
    tokens = val.split() 
      
    # Converts each token into lowercase 
    for i in range(len(tokens)): 
        tokens[i] = tokens[i].lower() 
      
    real_words += " ".join(tokens)+" "

for val in data_train[data_train['label']==0].text: 
      
    # split the value 
    tokens = val.split() 
      
    # Converts each token into lowercase 
    for i in range(len(tokens)): 
        tokens[i] = tokens[i].lower() 
      
    fake_words += " ".join(tokens)+" "

wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10).generate(real_words) 
  
# plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
  
plt.show()

max_features = 4500

# Tokenizing the text - converting the words, letters into counts or numbers. 
# We dont need to explicitly remove the punctuations. we have an inbuilt option in Tokenizer for this purpose
tokenizer = Tokenizer(num_words = max_features, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n', lower = True, split = ' ')
tokenizer.fit_on_texts(texts = data_train['text'])
X = tokenizer.texts_to_sequences(texts = data_train['text'])

# now applying padding to make them even shaped.
X = pad_sequences(sequences = X, maxlen = max_features, padding = 'pre')

print(X.shape)
y = data_train['label'].values
print(y.shape)

# splitting the data training data for training and validation.
from string import punctuation
from zipfile import ZipFile
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 101)

#We got our training data preprocessed and ready for training the neural network.

#We have to create a neural network now
# LSTM Neural Network
lstm_model = Sequential(name = 'lstm_nn_model')
lstm_model.add(layer = Embedding(input_dim = max_features, output_dim = 120, name = '1st_layer'))
lstm_model.add(layer = LSTM(units = 120, dropout = 0.2, recurrent_dropout = 0.2, name = '2nd_layer'))
lstm_model.add(layer = Dropout(rate = 0.5, name = '3rd_layer'))
lstm_model.add(layer = Dense(units = 120,  activation = 'relu', name = '4th_layer'))
lstm_model.add(layer = Dropout(rate = 0.5, name = '5th_layer'))
lstm_model.add(layer = Dense(units = len(set(y)),  activation = 'sigmoid', name = 'output_layer'))
# compiling the model
lstm_model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = ['accuracy'])

lstm_model_fit = lstm_model.fit(X_train, y_train, epochs = 1)

# GRU neural Network
gru_model = Sequential(name = 'gru_nn_model')
gru_model.add(layer = Embedding(input_dim = max_features, output_dim = 120, name = '1st_layer'))
gru_model.add(layer = GRU(units = 120, dropout = 0.2, 
                          recurrent_dropout = 0.2, recurrent_activation = 'relu', 
                          activation = 'relu', name = '2nd_layer'))
gru_model.add(layer = Dropout(rate = 0.4, name = '3rd_layer'))
gru_model.add(layer = Dense(units = 120, activation = 'relu', name = '4th_layer'))
gru_model.add(layer = Dropout(rate = 0.2, name = '5th_layer'))
gru_model.add(layer = Dense(units = len(set(y)), activation = 'softmax', name = 'output_layer'))
# compiling the model
gru_model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = ['accuracy'])

gru_model.summary()

