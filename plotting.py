from pymongo import MongoClient
import matplotlib.pyplot as plt
client = MongoClient()

db = client.toxic_docs
coll = db.documents
cursor = coll.find()

def count_entity_docs(entities, result_dict):
    for entity in entities:
        try:
            result_dict[entity] += 1
        except:
            result_dict[entity] = 1

people_occurrences = {}
places_occurrences = {}
organizations_occurrences = {}

for document in cursor:
    people = document["PEOPLE"]
    places = document["PLACES"]
    organizations = document["ORGANIZATIONS"]
    count_entity_docs(people, people_occurrences)
    count_entity_docs(places, places_occurrences)
    count_entity_docs(organizations, organizations_occurrences)

### plotting code
def make_plot(aList, label):
    plt.hist(aList, bins = range(2, max(aList)))
    plt.xlabel('Count')
    plt.ylabel('Frequency')
    plt.title('Frequency of Counts for ' + label)
    plt.axis([1, 100, 0, 25000])
    #plt.loglog(20*np.exp(-t/10.0), basex=10)
    plt.grid(True)
    plt.savefig(label + ".png")
    plt.clf()

make_plot(people_occurrences.values(), "People")
make_plot(places_occurrences.values(), "Places")
make_plot(organizations_occurrences.values(), "Organizations")
