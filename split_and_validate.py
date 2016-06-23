import bson
import json
import spacy
#import NETagger.py
#import pandas as pd
import matplotlib.pyplot as plt

from pymongo import MongoClient
from random import shuffle
spacy.load("en")
nlp = spacy.en.English(parser = False, matcher = False)


client = MongoClient()

db = client.toxic_docs
coll = db.documents
cursor = coll.find()


def split_and_tag(cursor):
    fold_1 = {"PERSON": [], "GPE": [], "ORG": []}
    fold_2 = {"PERSON": [], "GPE": [], "ORG": []}
    #### Logic: ####
    # Split document on spaces; put first half of document's words into an array; do the same for the second half
    document = document.replace("\n", "").replace(";", " ; ")
    document_split = document.split(" ")
    first_half = document_split[:len(document_split) / 2]
    second_half = document_split[len(document_split) / 2: ]
    first_half_tagged = nlp(first_half)
    second_half_tagged = nlp(second_half)


    ### FIX THIS LATER!!!! ###
    first_half_entities = [x for x in first_half_tagged.ents if x.label_ in set("PERSON", "GPE", "ORG")]
    second_half_entities = [x for x in second_half_tagged.ents if x.label_ in set("PERSON", "GPE", "ORG")]
    for i in enumerate(first_half_entities):
        assignment = [first_half_entities[i], second_half_entities[i]]
        shuffle(assignment)
        for entity in assignment[0]:
            fold_1[entity.label_].append(str(entity))
        for entity in assignment[1]:
            fold_2[entity.label_].append(str(entity))
        return (fold1, fold2)

def count_entity_docs(entities, result_dict):
    for entity in entities:
        try:
            result_dict[entity] += 1
        except:
            result_dict[entity] = 1

people_occurrences_fold1 = {}
places_occurrences_fold1 = {}
organizations_occurrences_fold1 = {}

people_occurrences_fold2 = {}
places_occurrences_fold2 = {}
organizations_occurrences_fold2 = {}

count_entity_docs(fold1["PEOPLE"], people_occurrences_fold1)
count_entity_docs(fold1["GPE"], places_occurrences_fold1)
count_entity_docs(fold1["ORG"], organizations_occurrences_fold1)

count_entity_docs(fold1["PEOPLE"], people_occurrences_fold2)
count_entity_docs(fold1["GPE"], places_occurrences_fold2)
count_entity_docs(fold1["ORG"], organizations_occurrences_fold2)

important_people_fold1 = [key for key,value in people_occurrences_fold1.items() if value > 20]
important_places_fold1 = [key for key,value in places_occurrences_fold1.items() if value > 20] ### MAGIC NUMBERS
important_organizations_fold1 = [key for key,value in organizations_occurrences_fold1.items() if value > 20] ### MAGIC NUMBERS

important_people_fold2 = [key for key,value in people_occurrences_fold1.items() if value > 20]
important_places_fold2 = [key for key,value in places_occurrences_fold1.items() if value > 20] ### MAGIC NUMBERS
important_organizations_fold2 = [key for key,value in organizations_occurrences_fold1.items() if value > 20] ### MAGIC NUMBERS

#### Find overlap ####
overlapping_people = set(important_people_fold1).intersection(important_people_fold2)
overlapping_places = set(important_places_fold1).intersection(important_places_fold2)
overlapping_organizations = set(important_organizations_fold1).intersection(important_places_fold2)

missed_people = len(important_people_fold_1) + len(important_people_fold2) - 2 * len(overlapping_people)
missed_places = len(important_places_fold_1) + len(important_places_fold2) - 2 * len(overlapping_places)
missed_organizations = len(important_organizations_fold_1) + len(important_organizations_fold2) - 2 * len(overlapping_organizations)

people_counts_dict = {}    
places_counts_dict = {}    
organizations_counts_dict = {}    


for aPerson in overlapping_people:
    people_counts_dict[aPerson] = [people_occurrences_fold1[aPerson], people_occurrences_fold2[aPerson]]

for aPlace in overlapping_places:
    places_counts_dict[aPlace] = [places_occurrences_fold1[aPlace], places_occurrences_fold2[aPlace]]

for anOrg in overlapping_organizations:
    organizations_counts_dict[anOrg] = [organizations_occurrences_fold1[anOrg], organizations_occurrences_fold2[anOrg]]



    # NLP both halves
    # randomly assign list of extracted named entities to set1, set2.
    
people_data_frame = pd.DataFrame.from_dict(people_counts_dict, columns = ["Fold1", "Fold2"])
places_data_frame = pd.DataFrame.from_dict(places_counts_dict, columns = ["Fold1", "Fold2"])
organizations_data_frame = pd.DataFrame.from_dict(organizations_counts_dict, columns = ["Fold1", "Fold2"])


people_data_frame["difference"] = Math.abs(people_data_frame["Fold1"] - people_data_frame["Fold2"])
places_data_frame["difference"] = Math.abs(places_data_frame["Fold1"] - places_data_frame["Fold2"])
organizations_data_frame["difference"] = Math.abs(organizations_data_frame["Fold1"] - organizations_data_frame["Fold2"])

scatter_plot = plt.figure()
plt.scatter(people_data_frame["Fold1"], people_data_frame["Fold2"])
plt.show()

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
