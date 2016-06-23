from flask import render_template
from pymongo import MongoClient
import networkx as nx
from networkx.readwrite import json_graph
import graph_generator as gg

client = MongoClient("ec2-52-33-219-239.us-west-2.compute.amazonaws.com")
db = client.toxic_docs
coll = db.documents

def get_people_by_year(year = 1970): # The default year is 1970
    cursor = coll.find({u"year":year})
    important_people = [x[u"IMPORTANT_PEOPLE"] for x in cursor]
    return important_people


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/output')
year = request.args.get('year')
important_people = get_people_by_year(year)
### connect them, put them into a json object of edges, and pass that to the displaytd2.html file
list_of_graphs = gg.make_graphs(important_people)
composed_graph = gg.compose_all(list_of_graphs)
data = json_graph.node_link_data(composed_graph)
gg.map_edges_to_node_names(data)
edges = data['links']

return render_template('displaytd2.html',edges = edges, year = year)

