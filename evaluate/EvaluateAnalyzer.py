import csv
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

negative = []
positive = []
neg_count = 0
neg_correct = 0
neg_false = 0
pos_count = 0
pos_correct = 0
pos_false = 0


#Quelle: https://www.delftstack.com/de/howto/python/python-csv-to-dictionary/
#Vergleich zwischen TextBlob und VADER
#Berechnet Accuracy, Precision, Recall & F1-Score

#Lese die Testdaten
with open('../test_data.csv', encoding='utf-8') as inp:
    reader = csv.reader(inp)
    for rows in reader:
        if rows[1] == "1":
            positive.append(rows[0])
        else:
            negative.append(rows[0])

#TextBlob
for neg_sentence in negative:
    blob = TextBlob(neg_sentence)
    for sentence in blob.sentences:
        if sentence.sentiment.polarity < 0:
            neg_correct += 1
        neg_count += 1

for pos_sentence in positive:
    blob = TextBlob(pos_sentence)
    for sentence in blob.sentences:
        if sentence.sentiment.polarity > 0:
            pos_correct += 1
        pos_count += 1

pos_false = pos_count - pos_correct
neg_false = neg_count - neg_correct

accuracy = (pos_correct + neg_correct)/(neg_count+pos_count)
precision = pos_correct/(pos_correct+pos_false)
recall = pos_correct/(pos_correct+neg_false)
f_one_score = 2*(recall*precision)/(recall+precision)

print('TextBlob')
print('TP: {}  FP: {}  FN: {}  TN: {}'.format(pos_correct, pos_false, neg_false, neg_correct))
print('Accuracy: {}  Precision: {}  Recall: {}  F1 Score: {}'.format(accuracy, precision, recall, f_one_score))

#VADER
vader = SentimentIntensityAnalyzer()

neg_count = 0
neg_correct = 0
neg_false = 0
pos_count = 0
pos_correct = 0
pos_false = 0

for neg_sentence in negative:
    score = vader.polarity_scores(neg_sentence)['compound']
    if score < 0:
        neg_correct += 1
    neg_count += 1

for pos_sentence in positive:
    score = vader.polarity_scores(pos_sentence)['compound']
    if score > 0:
        pos_correct += 1
    pos_count += 1

pos_false = pos_count - pos_correct
neg_false = neg_count - neg_correct

accuracy = (pos_correct + neg_correct)/(neg_count+pos_count)
precision = pos_correct/(pos_correct+pos_false)
recall = pos_correct/(pos_correct+neg_false)
f_one_score = 2*(recall*precision)/(recall+precision)

print('VADER NLTK')
print('TP: {}  FP: {}  FN: {}  TN: {}'.format(pos_correct, pos_false, neg_false, neg_correct))
print('Accuracy: {}  Precision: {}  Recall: {}  F1 Score: {}'.format(accuracy, precision, recall, f_one_score))
