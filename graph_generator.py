import networkx as nx
import numpy as np
from networkx.readwrite import json_graph
#graph = nx.Graph()

### COMMENT NEXT LINE OUT LATER
#test_people = cursor[0]["IMPORTANT_PEOPLE"]
from pymongo import MongoClient

from itertools import combinations
##

def get_query(start_year = 1908, end_year = None, contaminant = None, company = None):
    query = {}
    if start_year is not None:
        query[u"year"] = start_year
#    if end_year != start_year:
#        query["$and"] = [{"$gte" { u"year" : start_year }}, {"$lte" { u"year" : end_year }}]
#        query[u"year"].remove()
# The next two entries presuppose that the database has a text index created over the "text" field.
    if contaminant is not None:
        pass
    if company is not None:
        pass
    client = MongoClient("52.41.71.181") ## if database error fix here
    db = client.toxic_docs
    coll = db.documents
    cursor = coll.find(query)
    important_people = [x[u"IMPORTANT_PEOPLE"] for x in cursor]

def get_entities_by_year(year = 1908): # The default year is 1908
    client = MongoClient("52.41.71.181") ## if database error fix here
    db = client.toxic_docs
    coll = db.documents

    cursor = coll.find({u"year":year})
    important_people = []
    important_places = []
    important_organizations = []
    for x in cursor: ### I JUST CHANGED THIS FROM LIST COMPREHENSIONS!
        important_people.append(x[u"IMPORTANT_PEOPLE"])
        important_places.append(x[u"IMPORTANT_PLACES"])
        important_organizations.append(x[u"IMPORTANT_ORGANIZATIONS"])

    return important_people, important_places, important_organizations

def add_typed_nodes_to_graph(list_of_nodes, type_label, graph):
    list_of_nodes = [str(x) for x in list_of_nodes if len(str(x)) > 3]
    graph.add_nodes_from(list_of_nodes, type = type_label, count = 0)
#    edges = combinations(list_of_nodes, 2)
#    graph.add_edges_from(edges)

def fully_connect_graph(graph):
    edges = combinations(graph.nodes(),2)
    graph.add_edges_from(edges, weight = 1)

## 
#graph = nx.Graph()
#test_people = cursor[6]["IMPORTANT_PEOPLE"]
#test_places = cursor[6]["IMPORTANT_PLACES"]
#test_organizations = cursor[6]["IMPORTANT_ORGANIZATIONS"]

#add_typed_nodes_to_graph(test_people, "PERSON", graph)
#add_typed_nodes_to_graph(test_places, "PLACE", graph)
#add_typed_nodes_to_graph(test_organizations, "ORG", graph)
#fully_connect_graph(graph)

#graph2 = nx.Graph()
#test_people2 = cursor[12]["IMPORTANT_PEOPLE"]
#test_places2 = cursor[12]["IMPORTANT_PLACES"]
#test_organizations2 = cursor[12]["IMPORTANT_ORGANIZATIONS"]

#add_typed_nodes_to_graph(test_people2, "PERSON", graph2)
#add_typed_nodes_to_graph(test_places2, "PLACE", graph2)
#add_typed_nodes_to_graph(test_organizations2, "ORG", graph2)
#fully_connect_graph(graph2)


#graph3 = nx.compose(graph, graph2)


#data = json_graph.node_link_data(graph3)


### code for composing full list of graphs:

def compose_all(list_of_graphs):
    composed_graph = nx.Graph()
    for aGraph in list_of_graphs:
        counts = nx.get_node_attributes(aGraph,'count')
        ### YOU HAVE TO CHANGE THIS IT'S NOT RIGHT
        totals = {}
        for a_node in aGraph.nodes_iter():
            try:
                totals[a_node] = composed_graph.node[a_node]["count"] + aGraph.node[a_node]["count"] + 1
            except:
                totals[a_node] = aGraph.node[a_node]["count"] + 1

        # logic here:
        ### aGraph, composedGraph have some nodes in common. Find those nodes, get all the pairs of them, update weight on edge between them or set it to 1 if it didn't previously exist

            
        inCommonNodes = set(aGraph.nodes()).intersection(composed_graph.nodes())
        newEdges = combinations(inCommonNodes,2)
        new_weights = []

        for (node1, node2) in newEdges:
            try:
                new_weights.append((node1, node2, composed_graph[node1][node2]["weight"] + 1))
            except:
                new_weights.append((node1, node2, 1))

        composed_graph = nx.compose(aGraph, composed_graph)
        for a_node in aGraph.nodes_iter():
            try:
                composed_graph.node[a_node]["count"] = totals[a_node]
                #print composed_graph.node[a_node]["count"]
            except:
                print "Error: key not in graph."
        for node1, node2, weight in new_weights:
            composed_graph[node1][node2]["weight"] = weight

                
    return composed_graph
def countEnts(ent, countDict):
    try:
        countDict[ent] += 1
    except:
        countDict[ent] = 1

def make_graphs(entities_lists):
    list_of_graphs = []
    list_of_people = entities_lists[0]
    list_of_places = entities_lists[1]
    list_of_orgs = entities_lists[2]

    entities_count_dict = {}
    for listOfEnts in entities_lists[0] + entities_lists[1] + entities_lists[2]:
        for ent in listOfEnts:
            countEnts(ent, entities_count_dict)

    for document_index in range(len(list_of_people)):
        graph = nx.Graph()
        add_typed_nodes_to_graph([x for x in list_of_people[document_index] if entities_count_dict[x] > 1], "PERSON", graph)
        add_typed_nodes_to_graph([x for x in list_of_places[document_index]  if entities_count_dict[x] > 1], "PLACE", graph)
        add_typed_nodes_to_graph([x for x in list_of_orgs[document_index] if entities_count_dict[x] > 1], "ORG", graph)
        fully_connect_graph(graph)
        list_of_graphs.append(graph)
    return list_of_graphs


def map_edges_to_node_names(data):        
    for x in data['links']:
         source_index = x['source']
         target_index = x['target']
         x['source'] = data['nodes'][source_index]['id']
         x['target'] = data['nodes'][target_index]['id']
         x['type'] = "PERSON"

def stringify(edges):
    lines = []
    for anEdge in edges:
        #### key: "value"
        lines.append("{source: '" + anEdge["source"] + "', target: '" + anEdge['target'] + "', type: '" + anEdge["type"] + "'}")
    stringified = "[" + ",\n".join(lines) + "]"
    return stringified


def most_important(G):
    ranking = nx.get_node_attributes(G, "betweenness").items()#nx.betweenness_centrality(G).items()
#    print ranking
    counts = nx.get_node_attributes(G, "count").items()
    c = [v for _, v in counts]
    mean_count = sum(c)/len(c)
    std_count = np.std(c)
    crit_count = mean_count + 0.5 * std_count
    r = [x[1] for x in ranking]
    m = sum(r)/len(r) # mean centrality
    std = np.std(r)
    t = m #+ std # threshold, we keep only the nodes with n-times the mean ## TODO: Clean Magic Number
    Gt = G.copy()
    for k, v in ranking:
       # print type(G)
        if (v < t and G.node[k]["type"] != "PERSON") or G.node[k]["count"] < crit_count:
            Gt.remove_node(k)
    return Gt

#def measure_connectedness(edges):
#    for anEdge in edges:
            
#def get_betweennesses(graph):
#    pass


def set_normalized_counts_for_nodes(graph):
    attributes = nx.get_node_attributes(graph, "count")
    denom = sum([v for k,v in attributes.items()])#([x["weight"] for x in graph.edges()])
    normalizer = lambda x: x / float(denom)
    normalized_counts = dict(zip([k for k,v in attributes.items()], [normalizer(v) for x in attributes]))
    nx.set_node_attributes(graph, "normalized_count", normalized_counts)
    
def set_normalized_centrality(graph):
    betweenness = nx.betweenness_centrality(graph)
    nx.set_node_attributes(graph, "betweenness", betweenness)

def set_normalized_edge_weights(graph):
    attributes = nx.get_edge_attributes(graph, "weight")
    denom = sum([v for k,v in attributes.items()])#([x["weight"] for x in graph.edges()])
    normalizer = lambda x: x / float(denom)
    normalized_weights = dict(zip([k for k,v in attributes.items()], [normalizer(v) for x in attributes]))
    nx.set_edge_attributes(graph, "normalized_weight", normalized_weights)
        
def get_json_graph_for_year(year):
    important_people, important_places, important_organizations = get_entities_by_year(year)
    #    print "Got ", len(important_people), " documents. Making graph...."
    assert len(important_people) == len(important_places)
    assert len(important_people) == len(important_organizations)
    list_of_graphs = make_graphs([important_people, important_places, important_organizations]) ### CHANGED HERE
    composed_graph = compose_all(list_of_graphs)
#    print composed_graph.nodes()
    set_normalized_centrality(composed_graph)
    composed_graph = most_important(composed_graph) ##### REMOVE IF YOU DON'T WANT PRUNED GRAPH 
#    set_normalized_edge_weights(composed_graph)
#    set_normalized_counts_for_nodes(composed_graph)
    graph_json = json_graph.node_link_data(composed_graph)
    try:
        del graph_json['directed']
        del graph_json['multigraph']
    except KeyError:
        pass
#    print graph_json
    #    most_important = gg.most_important(composed_graph)
    print "Graph stats: "
    print "Number of Nodes: ", len(composed_graph.nodes()), "\tNumber of edges: ", len(composed_graph.edges())
    return graph_json
if __name__ == '__main__':
    get_json_graph_for_year(1908)
