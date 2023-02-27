import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

import numpy as np
from causallearn.graph.GeneralGraph import GeneralGraph
from causallearn.graph.GraphNode import GraphNode
from causallearn.graph.Endpoint import Endpoint
from causallearn.graph.Edge import Edge

import java.util as util
import edu.cmu.tetrad.data as td


# TEMPORARY NOTES #
# dtype allows the user to specify a list of dtypes should be 
# interpreted as continuous, the default is [np.floating], to 
# interpret integers as continuous as well use [np.floating, np.integer]
# implemnetaion not final: could be changed flag for ints as continous
def data_frame_to_tetrad_data(df, dtypes=[np.floating]):
    cols = df.columns
    discrete_cols = [col for col in cols if df[col].dtypes not in dtypes]
    category_map = {col: {val: i for i, val in enumerate(df[col].unique())} for col in discrete_cols}
    df = df.replace(category_map)
    values = df.values
    n, p = df.shape

    variables = util.ArrayList()
    for col in cols:
        if col in discrete_cols:    
            categories = util.ArrayList()
            for category in category_map[col]:
                categories.add(str(category))
            variables.add(td.DiscreteVariable(str(col), categories))
        else: 
            variables.add(td.ContinuousVariable(str(col)))

    if len(discrete_cols) == len(cols):
        databox = td.IntDataBox(n, p)
    elif len(discrete_cols) == 0:
        databox = td.DoubleDataBox(n, p)
    else:
        databox = td.MixedDataBox(variables, n)

    for col, var in enumerate(values.T):
        for row, val in enumerate(var):
            databox.set(row, col, val)

    return td.BoxDataSet(databox, variables)

# Note: This works too -- JR 2023-02-27
# def data_frame_to_tetrad_data(df, dtypes=[np.floating]):
#     cols = df.columns
#     discrete_cols = [col for col in cols if df[col].dtypes not in dtypes]
#     values = df.values
#     n, p = df.shape
#
#     variables = util.ArrayList()
#     for col in cols:
#         if col in discrete_cols:
#             variables.add(td.DiscreteVariable(str(col)))
#         else:
#             variables.add(td.ContinuousVariable(str(col)))
#
#     if len(discrete_cols) == len(cols):
#         databox = td.IntDataBox(n, p)
#     elif len(discrete_cols) == 0:
#         databox = td.DoubleDataBox(n, p)
#     else:
#         databox = td.MixedDataBox(variables, n)
#
#     data = td.BoxDataSet(databox, variables)
#
#     for col, var in enumerate(values.T):
#         for row, val in enumerate(var):
#             data.setObject(row, col, val)
#
#     return data


def tetrad_graph_to_pcalg(g):
    endpoint_map = {"NULL": 0,
                    "CIRCLE": 1,
                    "ARROW": 2,
                    "TAIL": 3}

    nodes = g.getNodes()
    p = g.getNumNodes()
    A = np.zeros((p, p), dtype=int)

    for edge in g.getEdges():
        i = nodes.indexOf(edge.getNode1())
        j = nodes.indexOf(edge.getNode2())
        A[j][i] = endpoint_map[edge.getEndpoint1().name()]
        A[i][j] = endpoint_map[edge.getEndpoint2().name()]

    return A


def tetrad_graph_to_causal_learn(g):
    endpoint_map = {"TAIL": Endpoint.TAIL,
                    "NULL": Endpoint.NULL,
                    "ARROW": Endpoint.ARROW,
                    "CIRCLE": Endpoint.CIRCLE,
                    "STAR": Endpoint.STAR}

    nodes = [GraphNode(str(node.getName())) for node in g.getNodes()]
    graph = GeneralGraph(nodes)

    for edge in g.getEdges():
        node1 = graph.get_node(edge.getNode1().getName())
        node2 = graph.get_node(edge.getNode2().getName())
        endpoint1 = endpoint_map[edge.getEndpoint1().name()]
        endpoint2 = endpoint_map[edge.getEndpoint2().name()]
        graph.add_edge(Edge(node1, node2, endpoint1, endpoint2))

    return graph
