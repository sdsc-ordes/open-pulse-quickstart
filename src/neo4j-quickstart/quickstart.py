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

# ---------------------------
# EXTRACT DATA FROM NEO4J
# ---------------------------

# Define your nodes

nodes = ["user", "repo", "org"]

# Define your relationships (edges)

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

def extract_data(nodes, relationships):
    downloader = get_downloader()

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


