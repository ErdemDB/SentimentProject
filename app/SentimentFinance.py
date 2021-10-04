import praw, csv

import nltk
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as mpy
from textblob import TextBlob
import numpy as np
import datetime as dt

from datapackage import Package

class Reddit():

    def __init__(self):
        self.reddit = praw.Reddit(client_id='CnLI-nPqn-Gr1Q', client_secret='2tz9J7iOueoMQeYIzU5T_LpFJwQ8jw', user_agent='TextMining/V0.1 by erdembedel')
        self.ps = PorterStemmer()
        self.stocks = []
        self.stock_comment = []
        self.gme_comment = []
        self.sid = SentimentIntensityAnalyzer()
        self.counterdata = 0

    def getUsStockSymbols(self):
        """
        Setze die NASDAQ Aktiennamen Kürzel in stock_nasdaq Liste
        Setze die NYSE Aktiennamen Kürzel in stock_nyse Liste
        :return: Liste aus stock_nasdaq + stock_nyse
        """
        package = Package('https://datahub.io/core/nasdaq-listings/datapackage.json')
        stock_nasdaq = []
        stock_nyse = []
        for resource in package.resources:
            if resource.descriptor['datahub']['type'] == 'derived/csv':
                for i, j in enumerate(resource.read()):
                    stock_nasdaq.append(j[0])
        package = Package('https://datahub.io/core/nyse-other-listings/datapackage.json')
        for resource in package.resources:
            if resource.descriptor['datahub']['type'] == 'derived/csv':
                for i, j in enumerate(resource.read()):
                    stock_nyse.append(j[0])

        self.stocks = stock_nasdaq + stock_nyse


    def getMostNamedStocks(self):
        """
        Auslesen der Reddit Kommentaren aus wallstreetbets, stocks, investing und stockmarket.
        Alle Kommentare die NASDAQ & NYSE Aktiennamen Kürzel enthalten werden in self.stock_comment gelistet.
        Wenn NASDAQ & NYSE Aktiennamen Kürzel im Kommentar erwähnt werden, dann wird count jeweils nach Aktiennamen hochgezählt.
        most_popular_stocks sortiert die Liste absteigend nach 10 mit dem höchsten "count".
        """
        subs = ['wallstreetbets', 'stocks', 'investing', 'stockmarket']
        categories = {'Daily Discussion', 'Weekend Discussion','Discussion'}
        titles, stock_list, count = [], [], {}
        counter = dict()

        for s in subs:
            subreddit = self.reddit.subreddit(s)
            hot = subreddit.hot()
            for raw_comment in hot:
                if raw_comment.upvote_ratio >= 0.80 and raw_comment.ups > 20 and (
                        raw_comment.link_flair_text in categories or raw_comment.link_flair_text is None):
                    raw_comment.comment_sort = 'new'
                    comments = raw_comment.comments
                    raw_comment.comments.replace_more(limit=10)
                    for comment in comments:
                        cleaned_text = self.getCleanedText(comment.body)
                        for filter_comment in cleaned_text:
                            if filter_comment in self.stocks and 5 >= len(filter_comment) >= 2:
                                if filter_comment in count:
                                    count[filter_comment] += 1
                                    stock_list.append(filter_comment)
                                    self.stock_comment.append([comment.body])
                                else:
                                    count[filter_comment] = 1
                                    stock_list.append(filter_comment)
                            self.counterdata += 1

        for k in stock_list:
            counter.update({k: counter.get(k, 0) + 1})

        #Sortiert die gesamte Liste absteigend und nimmt anschließend die 10 ersten Aktien
        most_popular_stocks = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:10]
        print('Kommentare : {}'.format(self.counterdata))
        self.writeToCSV(most_popular_stocks)


    def get_date(self, created):
        return dt.datetime.fromtimestamp(created)

    def getCleanedText(self,text):
        """
        Die Kommentare werden für die Analyse aufbereitet:
            - Alle Sonderzeichen und Zahlen werden entfernt
            - In Kleinbuchstaben umgewandelt
            - Stoppwörter entfernt
            - Tokenisiert
            - Wörter in Wortstämmen umgewandelt
        :param text: extrahierte Kommentare
        :return: Aufbereitetes Text
        """
        letters_only = re.sub("[^a-zA-Z]", " ", text)
        lower_test = letters_only.lower()
        stops = set(stopwords.words("english"))
        cleaned_text = [w for w in lower_test if not w in stops]
        cleaned_token = nltk.word_tokenize(letters_only)
        stemmed_text = [self.ps.stem(lower_test)for lower_test in cleaned_text]
        return cleaned_token

    def writeToCSV(self, most_popular_stocks):
       """
       Schreibe die 10 meistgenannten Finanzprodukte in eine CSV Datei
       :param most_popular_stocks:
       :return:
       """
       csv_columns = ['Stock', 'Amount']
       with open('most_popular_stocks.csv', 'w', encoding='utf8', newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_columns)
            csv_writer.writerows(most_popular_stocks)

    def readCSV(self, csvfile):
        """
        Lese die CSV Datei aus und schreibe sie in ein Dictionary
        :param csvfile: 10 meistgenannten Finanzprodukte in eine CSV Datei
        :return: Dictionary aus der CSV Datei
        """
        with open(csvfile, mode='r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            dict_from_csv = {rows[0]: rows[1] for rows in reader}
        return dict_from_csv


    def sentimentAnalyse(self):
        """
        Iteriere durch alle Kommentare und gebe den Polarität Score aus
        Wenn Pol. Score > 0 dann positive
        Wenn Pol. Score < 0 dann negative
        """
        polarityScore,positiveScore, negativeScore = {}, {}, {}

        most_popular_stocks = self.readCSV('most_popular_stocks.csv')

        for i, symbol in enumerate(most_popular_stocks):
            polarityScore[symbol] = 0
            positiveScore[symbol] = 0
            negativeScore[symbol] = 0
            counter = 0
            positiveCounter = 0
            negativeCounter = 0

            for j, comments in enumerate(self.stock_comment):
                if symbol in str(comments):
                    counter += 1
                    blob = TextBlob(str(comments))
                    for sentence in blob.sentences:
                        counter += 1
                        polarityScore[symbol] += sentence.sentiment.polarity
                        if sentence.sentiment.polarity > 0:
                            positiveCounter += 1
                        elif sentence.sentiment.polarity < 0:
                            negativeCounter += 1
            if counter != 0:
                polarityScore[symbol] = polarityScore[symbol] / counter
                positiveScore[symbol] = positiveCounter / counter * 100
                negativeScore[symbol] = negativeCounter / counter * 100

        print('Positive: {}'.format(positiveScore))
        print('Negative: {}'.format(negativeScore))

        self.visualization(polarityScore,negativeScore ,positiveScore)


    def visualization(self, scores, negative, positive):
        """
        Stelle die Ergebnisse in einem Balkendiagramm dar
        :param scores: Durchschnittliche Polarität Score
        :param negative: Negative Stimmung
        :param positive: Positive Stimmung
        :return:
        """
        mpy.bar(scores.keys(), scores.values(), color='orange')
        mpy.xlabel("Finanzprodukte")
        mpy.ylabel("Polarität Score")
        mpy.title("Polarität Score der Top 10 Finanzprodukte:")
        mpy.show()

        X_axis = np.arange(len(negative.keys()))

        mpy.bar(X_axis - 0.2, positive.values(), 0.4, label='Positive', color='forestgreen')
        mpy.bar(X_axis + 0.2, negative.values(), 0.4, label='Negative', color='r')

        mpy.xticks(X_axis, positive.keys())
        mpy.xlabel("Picks")
        mpy.ylabel("Score in percent")
        mpy.title("Sentiment analysis of top 10 picks:")
        mpy.legend()
        mpy.show()


def main():
    print('Die Wartezeit kann einige Minuten dauern...')
    r = Reddit()
    r.getUsStockSymbols()
    r.getMostNamedStocks()
    r.sentimentAnalyse()


if __name__ == "__main__":
    main()

