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
            RETURN ID(n) AS id, n.name AS name',
            {label: $label}
        ) YIELD value
        RETURN value.id, {name: value.name} AS features;
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

    def retrieve_subgraph(self, relationships, cypher_filter_query, depth):
        """
        Extract a subgraph based on:
            - A Cypher filter query (must return n)
            - A depth N expansion 
        Returns:
            nodes_ids, nodes_features, edges_indices, edges_attributes
        """
        with self.driver.session(database=self.database) as session:
            # Step 1: filter query → seed nodes
            seed_result = session.run(cypher_filter_query)
            seed_ids = [record["n"].id for record in seed_result]

            if not seed_ids:
                return {}, {}, {}, {}

            # Step 2: expand subgraph to depth N
            expand_query = f"""
            MATCH (start)
            WHERE id(start) IN $seed_ids
            MATCH p = (start)-[*1..{depth}]-(other)
            RETURN p
            """
            print("Starting expansion and extraction of subgraph...")
            result = session.run(expand_query, seed_ids=seed_ids)

            nodes_ids = {}          # label -> [ids]
            nodes_features = {}     # label -> [ {props} ]

            edges_indices = {}      # rel -> {type_name: np.array([...])}
            edges_attributes = {}   # rel -> {type_name: props}

            # Temporary storage for edges
            tmp_edges = {}  # (rel_type) → [ (src_id, dst_id, props, src_labels, dst_labels) ]
            paths = list(result)

            for record in paths:
                p = record["p"]

                # --- Nodes ---
                for n in p.nodes:
                    for lab in n.labels:

                        if lab not in nodes_ids:
                            nodes_ids[lab] = []
                            nodes_features[lab] = []

                        if n.id not in nodes_ids[lab]:
                            nodes_ids[lab].append(n.id)
                            nodes_features[lab].append(dict(n))

                # --- Relationships ---
                for r in p.relationships:
                    reltype = r.type

                    if reltype not in tmp_edges:
                        tmp_edges[reltype] = []

                    tmp_edges[reltype].append((
                        r.start_node.id,
                        r.end_node.id,
                        dict(r),
                        list(r.start_node.labels),
                        list(r.end_node.labels)
                    ))

            for reltype, triples in tmp_edges.items():

                edges_indices[reltype] = {}
                edges_attributes[reltype] = {}

                # Look up allowed types & their expected direction
                # Example: relationships["owner_of"]["type1"] -> ("user", "repo")
                rel_def = relationships[reltype] 

                # Build a mapping:  (src_label, dst_label) -> "type1"
                label_to_type = {}
                for typename, info in rel_def.items():
                    sl = info["source"]
                    tl = info["target"]
                    label_to_type[(sl, tl)] = typename

                grouped = {typename: [] for typename in rel_def.keys()}

                for src_id, dst_id, props, src_labels, dst_labels in triples:
                    for sl in src_labels:
                        for tl in dst_labels:
                            if (sl, tl) in label_to_type:
                                typename = label_to_type[(sl, tl)]
                                grouped[typename].append((src_id, dst_id, props))

                for typename, items in grouped.items():
                    if not items:
                        continue

                    srcs = [e[0] for e in items]
                    dsts = [e[1] for e in items]
                    feats = [e[2] for e in items]

                    edges_indices[reltype][typename] = np.array([srcs, dsts])
                    edges_attributes[reltype][typename] = feats
                    
            print("Finished extraction of subgraph.")
            return nodes_ids, nodes_features, edges_indices, edges_attributes
    
    def run_custom_query(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            results = session.run(query, parameters)
            data = [result.data() for result in results]
            return data
