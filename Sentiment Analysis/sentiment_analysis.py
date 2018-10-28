#!/usr/bin/python3

import nltk
import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

def main():
    global stop_words

    stop_words = set(stopwords.words('english'))
    
    i_data = pd.read_csv('data_1_train.csv', header=0, skipinitialspace=True)
    
    X = []
    y = []
    for i in range(len(i_data)):
        X.append(i_data.loc[i, 'text'])
        y.append(i_data.loc[i, 'class'])
    
    bow_transformer = TfidfVectorizer(analyzer=preprocess_text).fit(X)
    X = bow_transformer.transform(X)

    # Splitting data into 70% training data and 30% testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=101)
    classifier = MultinomialNB().fit(X_train, y_train)
    predicted = classifier.predict(X_test)
    print(classification_report(y_test, predicted))
    print("Accuracy score is {}".format(accuracy_score(y_test, predicted)))

    # Splitting data for 10 fold cross validation
    # data = pd.read_csv('data_3_train.csv', header=0, skipinitialspace=True)
    # kf = KFold(n_splits=10)
    # i = 1
    # with open('out.txt', 'w') as o_file:
    #     for train, test in kf.split(data):
    #         #train_data = np.array(data)[train]
    #         #test_data = np.array(data)[test]
    #         o_file.write("\nTraining data - {}\n".format(i))
    #         o_file.write(str(train))
    #         o_file.write("\nTesting data - {}\n".format(i))
    #         o_file.write(str(test))
    #         i = i + 1

def preprocess_word(word):
    word = word.strip(',.?!:;\"\'()')
    word = re.sub('[^\w]', '', word)
    return word

def preprocess_text(text):
    global stop_words
    processed_text = []
    text = text.lower()
    text = re.sub('\[comma\]', ',', text)
    text = text.strip(' "\'')
    text = re.sub('\s+', ' ', text)
    words = text.split()

    for word in words:
        word = preprocess_word(word)
        if word not in stop_words:
            word = str(PorterStemmer().stem(word))
            processed_text.append(word)

    return processed_text

if __name__ == '__main__':
    main()