# -*- coding: utf-8 -*-
"""amazon_reviews_to_Sentiment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nsH9xf_E6RkL03DnoCbzUbXQdPMgaJMY

# Import Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
#Basic libraries
import re
import pandas as pd 
import numpy as np 


# nltk
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import stopwords  #stopwords
from nltk import word_tokenize,sent_tokenize # tokenizing
from nltk.stem import PorterStemmer,LancasterStemmer  
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer 

#Metrics libraries

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,f1_score, confusion_matrix
from sklearn.metrics import classification_report


#Visualization libraries
import matplotlib.pyplot as plt 
from matplotlib import rcParams
import seaborn as sns
from textblob import TextBlob
from plotly import tools
import plotly.graph_objs as go
from plotly.offline import iplot
# %matplotlib inline

#Keras

from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from keras.layers import Dense , Input , LSTM , Embedding, Dropout , Activation, GRU, Flatten
from keras.layers import Bidirectional, GlobalMaxPool1D
from keras.models import Model, Sequential
from keras.layers import Convolution1D
from keras import initializers, regularizers, constraints, optimizers, layers

#Ignore warnings
import warnings

"""# Importing The Dataset"""

raw_reviews = pd.read_csv('Musical_instruments_reviews.csv', engine ="python")
## print shape of dataset with rows and columns and information 
print ("The shape of the  data is (row, column):"+ str(raw_reviews.shape))
print (raw_reviews.info())

raw_reviews.head(5)

"""Concatenating review text and summary

"""

raw_reviews['reviews']=raw_reviews['reviewText']+raw_reviews['summary']
raw_reviews=raw_reviews.drop(['reviewText', 'summary'], axis=1)
raw_reviews.head()

"""Creating a dataframe with the reviews and the corresponding rating"""

df=raw_reviews[['reviews','overall']]
df.head()

"""Removing all the records with rating 3"""

df= df[df['overall']!=3]
df.shape

"""# Preprocessing and cleaning

Creating a copy
"""

process_reviews=df.copy()

stop_words=set(nltk.corpus.stopwords.words('english'))

""" Handling NaN values"""

process_reviews.isnull().sum()

process_reviews=process_reviews.dropna()

process_reviews.isnull().sum()

"""Creating 'sentiment' column"""

process_reviews['overall'].value_counts()

process_reviews['overall'] = process_reviews['overall'].astype(float)

ratings = process_reviews['overall'].unique().tolist()
ratings

process_reviews['overall'].value_counts()

process_reviews['overall'] = process_reviews['overall'].apply(lambda x : 1 if x>3 else 0)

process_reviews['overall'].value_counts()

"""In this step, following operations are performed on the review text

Removing website links

Removing html tags

Decontracting(expanding from the original form)

Removing the words with numeric digits

Removing non-word characters

Converting to lower case

Removing stop words

Performing Lemmatization

"""

def decontract(text):
    text = re.sub(r"won\'t", "will not", text)
    text = re.sub(r"can\'t", "can not", text)
    text = re.sub(r"n\'t", " not", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'s", " is", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'t", " not", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'m", " am", text)
    return text

lemmatizer = WordNetLemmatizer()
def preprocess_text(review):
    review = re.sub(r"http\S+", "", review)            
     
    review = decontract(review)                        
    review = re.sub("\S*\d\S*", "", review).strip()     
    review = re.sub('[^A-Za-z]+', ' ', review)          
    review = review.lower()                             
    review = [word for word in review.split(" ") if not word in stop_words]
    review = [lemmatizer.lemmatize(token, "v") for token in review] #Lemmatization
    review = " ".join(review)
    review.strip()
    return review

process_reviews['reviews'] = process_reviews['reviews'].apply(lambda x: preprocess_text(str(x)))

X = []
sentences = list(process_reviews['reviews'])
for sen in sentences:
    X.append((sen))

X[2]

y = np.array(process_reviews['overall'])

y[2]

"""
# Train-test split(80:20)"""

train_df, test_df = train_test_split(process_reviews, test_size = 0.2, random_state = 42)
print("Training data size : ", train_df.shape)
print("Test data size : ", test_df.shape)

"""# Model Building¶

"""

top_words = 6000
tokenizer = Tokenizer(num_words=top_words)
tokenizer.fit_on_texts(train_df['reviews'])
list_tokenized_train = tokenizer.texts_to_sequences(train_df['reviews'])

max_review_length = 130
X_train = pad_sequences(list_tokenized_train, maxlen=max_review_length)
y_train = train_df['overall']

embedding_vecor_length = 32
model = Sequential()
model.add(Embedding(top_words+1, embedding_vecor_length, input_length=max_review_length))
model.add(LSTM(128))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

model.fit(X_train,y_train, epochs=3, batch_size=64, validation_split=0.2)

list_tokenized_test = tokenizer.texts_to_sequences(test_df['reviews'])
X_test = pad_sequences(list_tokenized_test, maxlen=max_review_length)
y_test = test_df['overall']
y_test = test_df['overall']
prediction = model.predict(X_test)
y_pred = (prediction > 0.5)

print("Accuracy of the model : ", accuracy_score(y_pred, y_test))
print('Confusion matrix:')
print(confusion_matrix(y_test,y_pred))
print('Classification report:')
print(classification_report(y_test, y_pred))

