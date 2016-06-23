from pymongo import MongoClient
import nltk



client = MongoClient()
db = client.toxic_docs
coll = db.documents
cursor = coll.find()
documents = [x["text"] for x in cursor]
word_lists = [nltk.word_tokenize(x) for x in documents]


#corpus = "\n".join(documents)
#tokenized = nltk.word_tokenize(corpus)



def buildTrie(list_of_collocations):
    
