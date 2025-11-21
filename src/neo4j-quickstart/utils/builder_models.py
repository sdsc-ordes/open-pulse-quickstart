from utils.models import GraphData, UserModel, OrgModel, RepoModel
import pandas as pd
from typing import Dict

def df_to_pydantic_models(df: pd.DataFrame, relationships) -> GraphData:
    """
    Parse a pandas DataFrame containing GitHub relationships into a GraphData model.
    Expected columns:
        source, target, property, source_type, target_type, source_id, target_id
    """
    graph = GraphData()

    for _, row in df.iterrows():
        source = row["source"]
        target = row["target"]
        prop = row["property"]
        source_type = row["source_type"]
        target_type = row["target_type"]
        source_id = int(row.get("source_id", 0))
        target_id = int(row.get("target_id", 0))

        # Defensive: skip unrecognized relationship types
        if prop not in relationships:
            continue

        # Create or update entities based on type
        if source_type == "user":
            source_obj = graph.add_user(source, source_id)
        elif source_type == "org":
            source_obj = graph.add_org(source, source_id)
        elif source_type == "repo":
            source_obj = graph.add_repo(source, source_id)
        else:
            continue

        if target_type == "user":
            target_obj = graph.add_user(target, target_id)
        elif target_type == "org":
            target_obj = graph.add_org(target, target_id)
        elif target_type == "repo":
            target_obj = graph.add_repo(target, target_id)
        else:
            continue

        # Apply relationship logic
        if prop == "member_of" and source_type == "user" and target_type == "org":
            target_obj.members.append(source)

        elif prop == "owner_of":
            if target_type == "repo":
                source_obj.owner_of.append(target)
                graph.repos[target].owner = source

        elif prop == "contributor_of":
            if target_type == "repo":
                source_obj.contributor_of.append(target)
                graph.repos[target].contributors.append(source)

        elif prop == "parent_of":
            graph.repos[source].parent_of.append(target)

    return graph
