
from psaw import PushshiftAPI
import datetime as dt
from textblob import TextBlob
from matplotlib import pyplot as plt



class SentimentGME():

    def __init__(self):
        self.api = PushshiftAPI()
        self.counter = 0

    def sentimentAnalyseGME(self, month, year):
        """
        Erhält den monatlischen Polarität Score aus den Kommentaren
        Berechnet den durchschnittlichen Polarität Score aus den Kommentaren
        Unterscheidet zwischen den negativen und posiitiven Kommentaren
        :param day: Der tag in der die Kommentare ausgelesen werden sollen
        :param month: Das Monat in der die Kommentare ausgelesen werden sollen
        :param year: Das Jahr in der die Kommentare ausgelesen werden sollen
        :return: Anzahl der positiven Kommentare, Polarität Score
        """
        positive = 0
        negative = 0
        pol = 0

        start_time = int(dt.datetime(year, month, 1).timestamp())
        if month == 2:
            end_time = int(dt.datetime(year, month, 28).timestamp())
        else:
            end_time = int(dt.datetime(year, month, 30).timestamp())

        subimissions = list(self.api.search_submissions(after=start_time,
                                        subreddit='wallstreetbets',
                                        filter=['title', 'id'],
                                                        limit=10))
        comments = list(self.api.search_comments(q='GME',
                                                 after=start_time,
                                                 before=end_time,
                                                 subreddit='wallstreetbets',
                                                 sort_type='score',
                                                 sort='desc',
                                                 limit=10000))
        for comment in comments:
            blob = TextBlob(str(comment[14]))
            for sentence in blob.sentences:
                if 'GME' in sentence:
                    pol += sentence.sentiment.polarity
                    if sentence.sentiment.polarity > 0:
                        positive += 1
                    elif sentence.sentiment.polarity < 0:
                        negative += 1
                    self.counter += 1

        pscore = pol/self.counter
        print('Monat: {}.{} Polarität Score: {}'.format(month, year, pscore))
        self.counter = 0
        return pscore, positive, negative

    def getDailyPolarity(self, day ,month, year):
        """
        Siehe sentimentAnalyseGME aber in täglich
        :param day: Der tag in der die Kommentare ausgelesen werden sollen
        :param month: Das Monat in der die Kommentare ausgelesen werden sollen
        :param year: Das Jahr in der die Kommentare ausgelesen werden sollen
        :return: Anzahl der positiven Kommentare, Polarität Score
        """
        positive = 0
        negative = 0
        pol = 0
        count = 0
        pscore = 0

        start_time = int(dt.datetime(year, month, day).timestamp())
        if day == 31:
            end_time = int(dt.datetime(year, month +1, 1).timestamp())
        else:
            end_time = int(dt.datetime(year, month, day+1).timestamp())

        subimissions = list(self.api.search_submissions(after=start_time,
                                        subreddit='wallstreetbets',
                                        filter=['title', 'id'],
                                                        limit=10))
        comments = list(self.api.search_comments(q='GME',
                                                 after=start_time,
                                                 before=end_time,
                                                 subreddit='wallstreetbets',
                                                 sort_type='score',
                                                 sort='desc',
                                                 limit=10000))
        for comment in comments:
            blob = TextBlob(str(comment[14]))
            for sentence in blob.sentences:
                if 'GME' in sentence:
                    pol += sentence.sentiment.polarity
                    if sentence.sentiment.polarity > 0:
                        positive += 1
                    elif sentence.sentiment.polarity < 0:
                        negative += 1
                    count += 1

        if pol != 0:
            pscore = pol / count

        print('Monat: {}.{}.{} Polarität Score: {} Anzahl Kommentare: {}'.format(day,month, year, pscore, count))
        return positive, pscore

def printResult():
    print('Ladet...')
    gme = SentimentGME()
    pscore = 0
    i = 1

    while i < 31:
        #print('Tag: {} Polarität: {}'.format(i,gme.getDailyPolarity(i,1,2021)))
        pscore =+ gme.getDailyPolarity(i, 8, 2021)[1]
        i += 1

    print('Ergebniss: {}'.format(pscore/i*100))

def main():
    """
    Visualisiere die Ergebnisse aus getDailyPolarity in Balkendiagrammen
    """
    print('Ladet...')
    gme = SentimentGME()

    Nov = gme.sentimentAnalyseGME(11, 2020)
    Dez = gme.sentimentAnalyseGME(12, 2020)
    Jan = gme.sentimentAnalyseGME(1, 2021)
    Feb = gme.sentimentAnalyseGME(2, 2021)
    Mrz = gme.sentimentAnalyseGME(3, 2021)
    Apr = gme.sentimentAnalyseGME(4, 2021)
    Mai = gme.sentimentAnalyseGME(5, 2021)
    Jun = gme.sentimentAnalyseGME(6, 2021)
    Jul = gme.sentimentAnalyseGME(7, 2021)
    Aug = gme.sentimentAnalyseGME(8, 2021)

    plt.title("Durchschnittliche Polarität Score")
    percent = ['Nov20', 'Dez20', 'Jan21', 'Feb21', 'Mrz21', 'Apr21', 'Mai21', 'Jun21', 'Jul21', 'Aug21']
    gmepolar = [Nov[0], Dez[0],
                Jan[0], Feb[0],
                Mrz[0], Apr[0],
                Mai[0], Jun[0],
                Jul[0], Aug[0]]
    plt.xlabel('Monat')
    plt.ylabel('Polarität Score')
    #plt.ylim(-1, 1)
    plt.scatter(percent, gmepolar)
    plt.plot(percent, gmepolar)
    plt.show()

    plt.title("Anzahl der positiven GME Kommentare")
    percent = ['Nov20', 'Dez20', 'Jan21', 'Feb21', 'Mrz21', 'Apr21', 'Mai21', 'Jun21', 'Jul21', 'Aug21']
    gmepos = [Nov[1], Dez[1],
                Jan[1], Feb[1],
                Mrz[1], Apr[1],
                Mai[1], Jun[1],
                Jul[1], Aug[1]]
    plt.xlabel('Monat')
    plt.ylabel('Anzahl der positiven Kommentare')
    plt.ylim(0, 1000)
    plt.scatter(percent, gmepos)
    plt.plot(percent, gmepos)
    plt.show()

    plt.title("Anzahl der negativen GME Kommentare")
    percent = ['Nov20', 'Dez20', 'Jan21', 'Feb21', 'Mrz21', 'Apr21', 'Mai21', 'Jun21', 'Jul21', 'Aug21']
    gmeneg = [Nov[2], Dez[2],
                Jan[2], Feb[2],
                Mrz[2], Apr[2],
                Mai[2], Jun[2],
                Jul[2], Aug[2]]
    plt.xlabel('Monat')
    plt.ylabel('Anzahl der negativen Kommentare')
    plt.ylim(0, 1000)
    plt.scatter(percent, gmeneg)
    plt.plot(percent, gmeneg)
    plt.show()

if __name__ == "__main__":
    main()