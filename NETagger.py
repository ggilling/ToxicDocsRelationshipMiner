import json
import bson
import spacy
from pymongo import MongoClient

spacy.load("en")
nlp = spacy.en.English(parser = False, matcher = False)

### Connect to database
client = MongoClient()

db = client.toxic_docs
coll = db.documents
cursor = coll.find()
### db entry fields:
### [u'file_source', u'document_type', u'date_terminated', u'num_pages', u'title', u'date_filed', u'created_at', u'jurisdiction', u'year', u'case_title', u'updated_at', u'text', u'original_filename', u'case_number', u'_id', u'hash_id']


### clean the strings
def replacer(a_string):
    #TODO: Replace with a regex?
    return a_string.replace("\n", " ").replace(";", " ; ")

def parse_entities(text):
    doc = nlp(text)
    people = []
    places = []
    organizations = []
    
    # zip tag, word 
    for entity in doc.ents:
        tag = str(entity.label_)
        name = str(entity)
        if tag == "PERSON":
            people.append(name)
        elif tag == "GPE":
            places.append(name)
        elif tag == "ORG":
            organizations.append(name)
    people = list(set(people))
    places = list(set(places))
    organizations = list(set(organizations))
    return people, places, organizations
###
for document in cursor:
    text = document["text"]
    people,places,organizations = parse_entities(replacer(text))
    coll.update({"_id": document["_id"]}, {"$set": {"PEOPLE":people, "PLACES": places, "ORGANIZATIONS": organizations}}, upsert=TRUE)

    
## def map_entities_to_docs(entities, doc, result_dict):
##     for entity in entities:
##         try:
##             result_dict[entity].append(doc)
##         except:
##             result_dict[entity] = [doc]

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
    
important_people = [key for key,value in people_occurrences.items() if value > 20]
important_places = [key for key,value in places_occurrences.items() if value > 20] ### MAGIC NUMBERS
important_organizations = [key for key,value in organizations_occurrences.items() if value > 20] ### MAGIC NUMBERS

def intersect_important(entities, important_entities):
    return list(set(entities).intersection(important_entities))

for document in cursor:
    people = document["PEOPLE"]
    places = document["PLACES"]
    organizations = document["ORGANIZATIONS"]
    coll.update({"_id": document["_id"]}, {"$set": {"IMPORTANT_PEOPLE": intersect_important(people, important_people), "IMPORTANT_PLACES": intersect_important(places, important_places), "IMPORTANT_ORGANIZATIONS": intersect_important(organizations, important_organizations)}}, upsert=True)


## ### Clean an entry and parse it into entities:

## toxic_docs_df["text_cleaned"] = toxic_docs_df["text"].apply(replacer)
## toxic_docs_df["ENTITIES"]= toxic_docs_df["text_cleaned"].apply(parse_entities)

## toxic_docs_df["PEOPLE"] = toxic_docs_df["ENTITIES"].apply(lambda x: x[0])
## toxic_docs_df["PLACES"] = toxic_docs_df["ENTITIES"].apply(lambda x: x[1])
## toxic_docs_df["ORGANIZATIONS"] = toxic_docs_df["ENTITIES"].apply(lambda x: x[2])

## ### Map entities to their documents

## people_doc_dict = {}
## places_doc_dict = {}
## organizations_doc_dict = {}
## map(lambda x: map_entities_to_docs(x[1], x[0], people_doc_dict), zip(toxic_docs_df[u"hash_id"], toxic_docs_df["PEOPLE"]))
## map(lambda x: map_entities_to_docs(x[1], x[0], places_doc_dict), zip(toxic_docs_df[u"hash_id"], toxic_docs_df["PLACES"]))
## map(lambda x: map_entities_to_docs(x[1], x[0], organizations_doc_dict), zip(toxic_docs_df[u"hash_id"], toxic_docs_df["ORGANIZATIONS"]))

## print "People Types: ", len(people_doc_dict.keys()), "\tPeople Tokens: ", sum(toxic_docs_df["PEOPLE"].apply(len))
## print "Place Types: ", len(places_doc_dict.keys()), "\tPlace Tokens: ", sum(toxic_docs_df["PLACES"].apply(len))
## print "Organization Types: ", len(organizations_doc_dict.keys()), "\tOrganization Tokens: ", sum(toxic_docs_df["ORGANIZATIONS"].apply(len))


