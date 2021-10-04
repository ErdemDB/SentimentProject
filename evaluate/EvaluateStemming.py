from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from nltk.tokenize import word_tokenize

ps = PorterStemmer()
ls = LancasterStemmer()

sentence = 'American similar to watching a person walk up the stairs with a yo yo.'
words = word_tokenize(sentence)

#Porter Stemmer
for w in words:
    print(w, " : ", ps.stem(w))

#Lancaster Stemmer
for l in words:
    print(l, " : ", ls.stem(l))

