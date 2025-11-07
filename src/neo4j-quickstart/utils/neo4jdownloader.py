"""Neo4JDownloader class for graph downloading from Neo4J."""

from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError
import logging
import numpy as np


class Neo4JDownloader:
    def __init__(self, uri, user, password, database=None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        # Don't forget to close the driver connection when you are finished
        # with it
        self.driver.close()

    def get_entire_graph(self, driver):
        query = """
        MATCH (s)-[r]->(t)
        RETURN s, r, t
        """
        results = driver.run(query)
        for record in results:
            print(record)

    def get_nodes(self, driver, label):
        query = """
        CALL apoc.cypher.run(
            'MATCH (n:`' + $label + '`)
            RETURN ID(n) AS id, n.name AS name, n.anchor AS anchor',
            {label: $label}
        ) YIELD value
        RETURN value.id, {name: value.name, anchor: value.anchor} AS features;
        """
        try:
            results = driver.run(query, {"label": label})
            ids, features = [], []
            for record in results:
                ids.append(record["value.id"])
                features.append(record["features"])
            return ids, features
        except (DriverError, Neo4jError) as exception:
            logging.error("%s raised an error: \n%s", query, exception)
            raise

    def get_node_name_by_id(self, driver, node_id):
        query = f"""
        MATCH (n)
        WHERE ID(n) = {node_id}
        RETURN n.name AS name
        """
        try:
            result = driver.run(query).single()
            if result:
                return result["name"]
            else:
                return None
        except (DriverError, Neo4jError) as exception:
            logging.error("%s raised an error: \n%s", query, exception)
            raise

    def get_edges(self, driver, src_label, rel_type, dst_label):
        query = f"""
        MATCH (a:{src_label})-[r:`{rel_type}`]->(b:{dst_label})
        RETURN ID(a) AS src, ID(b) AS dst, r.feat AS edge_features
        """
        results = driver.run(query)
        edge_index, edge_attrs = [], []
        for record in results:
            edge_index.append([record["src"], record["dst"]])
            edge_attrs.append(record["edge_features"])
        return np.array(edge_index).T, edge_attrs

    def retrieve_nodes(self, nodes_list):
        ids = {}
        feats = {}
        with self.driver.session(database=self.database) as session:
            for node in nodes_list:
                id, feat = session.execute_read(self.get_nodes, node)
                ids[node] = id
                feats[node] = feat
        return ids, feats

    def retrieve_edges(self, relationship_dict):
        edges_index = {}
        edges_attributes = {}
        for key, subdict in relationship_dict.items():
            edges_index[key] = {}
            edges_attributes[key] = {}
            for type, val in subdict.items():
                with self.driver.session(database=self.database) as session:
                    source = val["source"]
                    target = val["target"]
                    relationship = key
                    edge_index, edge_attributes = session.execute_read(
                        self.get_edges, source, relationship, target
                    )
                    edges_index[key][type] = edge_index
                    edges_attributes[key][type] = edge_attributes
        return edges_index, edges_attributes

    def retrieve_all(self):
        with self.driver.session(database=self.database) as session:
            session.execute_read(self.get_entire_graph)
