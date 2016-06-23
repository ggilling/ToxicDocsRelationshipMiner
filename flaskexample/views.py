from flask import render_template, request
import networkx as nx
from networkx.readwrite import json_graph
import graph_generator as gg
from flaskexample import app


@app.route('/')
@app.route('/index')
def index():
    return render_template("input.html")

@app.route('/input')
def year_input():
    return render_template("input.html")

@app.route('/output')
def generate_output():
    start_year = request.args.get('start_year')
    try:
        start_year = int(start_year)
    except:
        return render_template("input.html")
    graph = gg.get_json_graph_for_year(start_year)
    #print graph
#    important_people = gg.get_people_by_year(int(start_year))
#    print "Got ", len(important_people), " documents. Making graph...."
    ### connect them, put them into a json object of edges, and pass that to the output.html file
#    list_of_graphs = gg.make_graphs(important_people)
#    composed_graph = gg.compose_all(list_of_graphs)
#    most_important = gg.most_important(composed_graph)
#    data = json_graph.node_link_data(most_important)
#    gg.map_edges_to_node_names(data)
#    edges = data['links']
#    edges = gg.stringify(edges)
#    print edges
#    edges = ""
    return render_template('output.html',graph = graph)
