# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, invalid-name
from xml.etree.ElementTree import Element, SubElement, tostring

from google.cloud import bigquery

from utils import clean_id

client = bigquery.Client()


class Graph:
    def __init__(self, graph_type) -> None:
        self.tree = Element(graph_type, attrib={"xmlns":"http://graphml.graphdrawing.org/xmlns", "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance", "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"})
        self.graph = SubElement(self.tree, "graph", attrib={"edgedefault": "directed"})
        self.nodes = []
        self.edges = []

    def add_node(self, new_node) -> None:
        if new_node.id not in self.nodes:
            node_attributes = {"id": new_node.id}
            SubElement(self.graph, new_node.type, attrib=node_attributes)
            self.nodes.append(new_node.id)

    def add_edge(self, new_edge):
            edge_attributes = {"source": new_edge.source.id, "target": new_edge.target.id}
            SubElement(self.graph, new_edge.type, attrib=edge_attributes)

    def save_to_file(self, filename):
        xmlstr = tostring(self.tree, encoding="utf8", method="xml")
        f = open(filename, "wb")
        f.write(xmlstr)
        f.close()



class Node:
    def __init__(self, id: str) -> None:
        self.type = "node"
        self.id = id

class Edge:
    def __init__(self, source: Node, target: Node) -> None:
        self.type = "edge"
        self.source = source
        self.target = target


def generate_graphML(rows):
    graphML = Graph("graphml")
    for row in rows:
        big_query_id, powerbi_id = row.values()
        big_query_node = Node(clean_id(big_query_id))
        powerbi_node = Node(clean_id(powerbi_id))
        graphML.add_node(big_query_node)
        graphML.add_node(powerbi_node)
        new_edge = Edge(big_query_node, powerbi_node)
        graphML.add_edge(new_edge)
    graphML.save_to_file("shshshs.xml")


def read_big_query_table(columns, dataset, table):
    query = f"SELECT {columns} " f"FROM {dataset}.{table};"
    query_job = client.query(query)
    rows = query_job.result()
    generate_graphML(rows)


read_big_query_table("bigquery, powerbi", "test_pierre_alexandre", "power_bi_clean")
