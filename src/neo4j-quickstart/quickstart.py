import neo4j
import re
from pathlib import Path
import os
from dotenv import load_dotenv 
load_dotenv()  # Load environment variables from .env file

from utils.neo4jdownloader import Neo4JDownloader
from utils.builder_dataframe import neo4j_to_dataframe
from utils.builder_models import df_to_pydantic_models
from utils.visualization import visualize_graph
from utils.visualization import visualize_clusters

# -----------------------------
# NEO4J SETUP (Do not edit)
# -----------------------------

# Here are the available nodes

nodes = ["user", "repo", "org"]

# Here are the available relationships (edges)

relationships = {
    "member_of": {"type1": {"source": "user", "target": "org"}},
    "owner_of": {
        "type1": {"source": "user", "target": "repo"},
        "type2": {"source": "org", "target": "repo"},
    },
    "contributor_of": {
        "type1": {"source": "user", "target": "repo"},
        "type2": {"source": "org", "target": "repo"},
    },
    "parent_of": {
        "type1": {"source": "repo", "target": "repo"},
    },
}

def get_downloader():
    
    NEO4J_URI = os.environ.get("NEO4J_URI")
    NEO4J_USERNAME = os.environ.get("NEO4J_USER")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE")

    print(NEO4J_URI)

    return Neo4JDownloader(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE)

def connect_neo4j(): 
    downloader = get_downloader()
    return downloader

# ------------------------------------------------------------------
# EXTRACT CUSTOM SUBSET OF DATA FROM NEO4J WITH CYPHER QUERRIES
# ------------------------------------------------------------------

downloader = connect_neo4j()

# QUERY: Get all nodes that have the EPFL string in their name (whether they are user, repository or org)

epfl_query ="""
MATCH (n)
WHERE toLower(n.name) CONTAINS 'epfl'
RETURN n.name AS name, labels(n) AS node_type;
"""

epfl_nodes = downloader.run_custom_query(epfl_query)
print("RESULTS: all nodes that match the epfl string: ",epfl_nodes)

# QUERY: Get all organizations

orgs_query = """
MATCH (o:org)
RETURN o.name AS organization;
"""
organizations = downloader.run_custom_query(orgs_query)
print("RESULTS: all organizations in the graph: ",organizations)

# QUERY : Get all users for an organization 

users_of_org_query = """
MATCH (u:user)-[:member_of]->(o:org)
WHERE o.name = $org_name
RETURN u.name AS user
ORDER BY user;
"""
parameters = {
    "org_name": "SwissDataScienceCenter"
}
users_in_org = downloader.run_custom_query(users_of_org_query, parameters)
print("RESULTS: users inside the organization: ", users_in_org)

# QUERY: For a list of users get all their repositories

# Here we base the query on the Contributor of edge.
repos_of_users_query= """
MATCH (u:user)-[:contributor_of]->(repo:repo)
WHERE u.name IN $user_list
RETURN u.name AS user,
       repo.name AS repository
ORDER BY user, repository;
"""
parameters = {
    "user_list": ["yousra-elbachir", "Victor2175", "williamaeberhard"]
}
users_and_their_repos = downloader.run_custom_query(repos_of_users_query, parameters)
print("RESULTS: users and their repositories: ", users_and_their_repos)

# ---------------------------
# EXTRACT ALL DATA FROM NEO4J
# ---------------------------

def extract_data(nodes, relationships):
    downloader = connect_neo4j()

    try:
        nodes_ids, nodes_features = downloader.retrieve_nodes(nodes)
        edges_indices, edges_attributes = downloader.retrieve_edges(relationships)

        return nodes_ids, nodes_features, edges_indices, edges_attributes
    finally:
        downloader.close()


nodes_ids, nodes_features, edges_indices, edges_attributes = extract_data(nodes, relationships)
# example of looking at the output
# print(nodes_ids["org"])
# print(nodes_features["org"])
# print(edges_indices)

# -------------------------------------------
# MAKE NEO4J DATA INTO A PANDAS DATAFRAME
# -------------------------------------------

df = neo4j_to_dataframe(nodes_ids, nodes_features, edges_indices, relationships)
print("Dataframe constructed, shape is :", df.shape)

# -------------------------------------------
# EXPLORE / FILTER PANDAS DATAFRAME
# -------------------------------------------

# Define your pattern and filter the dataframe

epfl_pattern = r"EPFL"
epfl_df = df[
    df['source'].astype(str).str.contains(epfl_pattern, flags=re.IGNORECASE, na=False) |
    df['target'].astype(str).str.contains(epfl_pattern, flags=re.IGNORECASE, na=False)
]
print(epfl_df.head())
print(epfl_df.shape)

sdsc_pattern = r"(SwissDataScienceCenter|SDSC)"
sdsc_df = df[
    df["source"].astype(str).str.contains(sdsc_pattern, flags=re.IGNORECASE, na=False) |
    df["target"].astype(str).str.contains(sdsc_pattern, flags=re.IGNORECASE, na=False)
]
print(sdsc_df.head())
print(sdsc_df.shape)

# -----------------------------------------------------------------------
# FEED YOUR DATAFRAME TO THE PYDANTIC MODELS AND VISUALIZE THE GRAPH
# -----------------------------------------------------------------------

# From Dataframes to Graphs (via Pydantic)
graph = df_to_pydantic_models(sdsc_df, relationships)
sdsc_graph = df_to_pydantic_models(sdsc_df, relationships)
epfl_graph = df_to_pydantic_models(epfl_df, relationships)

# Full Graphs

output_path = Path("plots/graphs/graph_200_visualization.png")
visualize_graph(graph, output_path)

output_path = Path("plots/graphs/sdsc_graph.png")
visualize_graph(sdsc_graph, output_path)

output_path = Path("plots/graphs/epfl_graph.png")
visualize_graph(epfl_graph, output_path)

# Clusters 

output_dir = Path("plots/clusters/")

cluster_prefix_name = "200_first_nodes"
visualize_clusters(graph, output_dir, cluster_prefix_name)

cluster_prefix_name = "sdsc"
visualize_clusters(sdsc_graph, output_dir, cluster_prefix_name)

cluster_prefix_name = "epfl"
visualize_clusters(epfl_graph, output_dir, cluster_prefix_name)

# -----------------------------------------------------------------------
# DEMO FOLLOW UP 

# We can see for EPFL that just a string matching does not manage to find many of the EPFL affiliated repositories. 
# How can we complement with other tools and other approaches to find a better EPFL graph ? 
# Your turn to play around, good luck !

# -----------------------------------------------------------------------


