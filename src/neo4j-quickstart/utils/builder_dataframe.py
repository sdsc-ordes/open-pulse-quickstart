import pandas as pd
import numpy as np

def neo4j_to_dataframe(nodes_ids, nodes_features, edges_indices, relationships):
    rows = []

    # Step 1: Build lookup tables {node_id: features_dict}
    node_lookup = {}
    for ntype, ids in nodes_ids.items():
        features_list = nodes_features.get(ntype, [])
        # Zip IDs with feature dicts safely
        node_lookup[ntype] = {
            nid: features_list[i] for i, nid in enumerate(ids) if i < len(features_list)
        }

    # Step 2: Iterate through relationships
    for rel_name, rel_types in relationships.items():
        for rel_type, rel_info in rel_types.items():
            if rel_name not in edges_indices or rel_type not in edges_indices[rel_name]:
                continue

            edge_array = edges_indices[rel_name][rel_type]
            src_type = rel_info["source"]
            tgt_type = rel_info["target"]

            src_ids = edge_array[0]
            tgt_ids = edge_array[1]

            src_names = [
                node_lookup[src_type].get(sid, {}).get("name", f"{src_type}_{sid}")
                for sid in src_ids
            ]
            tgt_names = [
                node_lookup[tgt_type].get(tid, {}).get("name", f"{tgt_type}_{tid}")
                for tid in tgt_ids
            ]

            for sid, tid, sname, tname in zip(src_ids, tgt_ids, src_names, tgt_names):
                rows.append({
                    "source": sname,
                    "target": tname,
                    "property": rel_name,
                    "source_type": src_type,
                    "target_type": tgt_type,
                    "source_id": sid,
                    "target_id": tid
                })

    df = pd.DataFrame(rows)
    return df
