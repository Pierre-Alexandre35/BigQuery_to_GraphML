# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, invalid-name, unspecified-encoding
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from fastapi import Path
from google.cloud import bigquery
from networkx.drawing.nx_agraph import to_agraph

import networkx as nx

from utils import clean_id
from settings import GRAPHML_ATTRIBUTES


client = bigquery.Client()

class Node:
    def __init__(self, id: str) -> None:
        self.type = "node"
        self.id = id


class Edge:
    def __init__(self, source: Node, target: Node) -> None:
        self.type = "edge"
        self.source = source
        self.target = target


class Graph:
    def __init__(self, graph_type: str) -> None:
        self.tree = Element(
            graph_type,
            attrib=GRAPHML_ATTRIBUTES,
        )
        self.graph = SubElement(self.tree, "graph", attrib={
                                "edgedefault": "directed"})
        self.nodes = []
        self.edges = []

    def add_node(self, new_node: Node) -> None:
        if new_node.id not in self.nodes:
            node_attributes = {"id": new_node.id}
            SubElement(self.graph, new_node.type, attrib=node_attributes)
            self.nodes.append(new_node.id)

    def add_edge(self, new_edge: Edge) -> None:
        edge_attributes = {"source": new_edge.source.id,
                           "target": new_edge.target.id}
        SubElement(self.graph, new_edge.type, attrib=edge_attributes)

    def save_to_file(self, filename: Path) -> None:
        xmlstr = minidom.parseString(
            tostring(self.tree)).toprettyxml(indent="   ")
        with open(filename, "w") as f:
            f.write(xmlstr)


def generate_graphML(rows: bigquery.table.RowIterator) -> None:
    graphML = Graph("graphml")
    for row in rows:
        big_query_id, powerbi_id = row.values()
        big_query_node = Node(clean_id(big_query_id))
        powerbi_node = Node(clean_id(powerbi_id))
        graphML.add_node(big_query_node)
        graphML.add_node(powerbi_node)
        new_edge = Edge(big_query_node, powerbi_node)
        graphML.add_edge(new_edge)
    graphML.save_to_file("shshshs.graphml")


def read_big_query_table(columns, dataset, table):
    query = f"SELECT {columns} " f"FROM {dataset}.{table};"
    query_job = client.query(query)
    rows = query_job.result()
    generate_graphML(rows)


def draw_graph(graph: nx.DiGraph, filepath: str):
    graph.graph["graph"] = {
        "rankdir": "LR",
        # "nodesep": "3",
    }
    graph.graph["node"] = {"shape": "rectangle"}
    # graph.graph["edges"] = {"arrowsize": "40.0"}
    pygraphviz_graph = to_agraph(graph)
    pygraphviz_graph.layout("dot")
    pygraphviz_graph.draw(filepath)


read_big_query_table("bigquery, powerbi", "test_pierre_alexandre", "power_bi_clean")

graph = nx.read_graphml("shshshs.graphml")
draw_graph(graph, "graph.svg")
