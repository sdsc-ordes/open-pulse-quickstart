"""Visualization utilities for graph rendering."""

import logging
import math
import numpy as np
from pathlib import Path
from typing import Set, Optional, Dict

from .models import GraphData

logger = logging.getLogger(__name__)

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyArrowPatch
    from adjustText import adjust_text
    VISUALIZATION_AVAILABLE = True
    HAS_ADJUST_TEXT = True
except ImportError as e:
    if 'adjustText' in str(e):
        import networkx as nx
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyArrowPatch
        VISUALIZATION_AVAILABLE = True
        HAS_ADJUST_TEXT = False
        logger.warning("adjustText not available. Labels will be placed on nodes. Install with: pip install adjustText")
    else:
        VISUALIZATION_AVAILABLE = False
        HAS_ADJUST_TEXT = False
        logger.warning("Visualization libraries not available. Install networkx and matplotlib for graph visualization.")

# Color palettes
COLOR_MAP = {
    'user': '#00d9ff',
    'org': '#ffcc00',
    'repo': '#00ff88',
}

EDGE_COLOR_MAP = {
    'owner_of': '#ff6b6b',
    'contributor_of': '#4ecdc4',
    'member_of': '#95e1d3',
    'parent_of': '#ffd93d',
}

def create_networkx_graph(graph: GraphData, 
            visited_nodes: Optional[Set[str]] = None,
            discovered_nodes: Optional[Dict[str, tuple]] = None
    ) -> Optional[nx.DiGraph]:
    # Create directed graph
    G = nx.DiGraph()

    # Visited vs Discovered Nodes 

    # If no visited_nodes provided, treat all nodes as explored
    if visited_nodes is None:
        visited_nodes = set()
        visited_nodes.update(user.name for user in graph.users.values())
        visited_nodes.update(org.name for org in graph.orgs.values())
        visited_nodes.update(repo.name for repo in graph.repos.values())
    
    if discovered_nodes is None:
        discovered_nodes = {}

    # ---------------------------
    # Add nodes
    # ---------------------------
    for user in graph.users.values():
        G.add_node(
            user.name,
            node_type="user",
            label=user.name,
        )

    for org in graph.orgs.values():
        G.add_node(
            org.name,
            node_type="org",
            label=org.name,
        )

    for repo in graph.repos.values():
        G.add_node(
            repo.name,
            node_type="repo",
            label=repo.name,
        )

    # Add discovered (unexplored) nodes
    for node_id, (node_type, parent_id, parent_type) in discovered_nodes.items():
        if node_id not in G:  # Don't add if already in graph
            if node_type == 'repo':
                label = node_id.split('/')[-1] if '/' in node_id else node_id
            elif node_type in ['user', 'org']:
                label = node_id
            else:
                label = node_id
                
            G.add_node(
                node_id,
                node_type=node_type,
                is_seed=False,
                is_explored=False,  # These are unexplored
                label=label
            )
    # ---------------------------
    # Add edges
    # ---------------------------
    # Users
    for user in graph.users.values():
        # owner_of → repos
        for repo_name in user.owner_of:
            if repo_name in graph.repos:
                G.add_edge(user.name, repo_name, relationship="owner_of")

        # contributor_of → repos
        for repo_name in user.contributor_of:
            if repo_name in graph.repos:
                G.add_edge(user.name, repo_name, relationship="contributor_of")

    # Orgs
    for org in graph.orgs.values():
        # member_of (users → org)
        for member in org.members:
            if member in graph.users:
                G.add_edge(member, org.name, relationship="member_of")

        # owner_of (org → repos)
        for repo_name in org.owner_of:
            if repo_name in graph.repos:
                G.add_edge(org.name, repo_name, relationship="owner_of")

        # contributor_of (org → repos)
        for repo_name in org.contributor_of:
            if repo_name in graph.repos:
                G.add_edge(org.name, repo_name, relationship="contributor_of")

    # Repos
    for repo in graph.repos.values():
        # contributors (repo ← contributor)
        for contributor in repo.contributors:
            if contributor in graph.users or contributor in graph.orgs:
                if contributor == repo.owner:
                    G.add_edge(contributor, repo.name, relationship="owner_of")
                else:
                    G.add_edge(contributor, repo.name, relationship="contributor_of")

        # parent_of → fork relationships
        if repo.parent_of:
            for item in repo.parent_of: 
                if (item in graph.repos):
                    G.add_edge(repo.name, item, relationship="parent_of")
    
    # Add edges from explored to discovered nodes
    for node_id, (node_type, parent_id, parent_type) in discovered_nodes.items():
        if node_id in G and parent_id and parent_id in G:
            # Determine relationship type based on node types
            if parent_type == 'user' and node_type == 'repo':
                relationship = 'owner_of'
            elif parent_type == 'org' and node_type == 'repo':
                relationship = 'owner_of'
            elif parent_type == 'user' and node_type == 'org':
                relationship = 'member_of'
            elif parent_type == 'org' and node_type == 'user':
                relationship = 'member_of'
            elif parent_type == 'repo' and node_type == 'user':
                relationship = 'contributor_of'
            elif parent_type == 'repo' and node_type == 'repo':
                relationship = 'parent_of'
            else:
                relationship = 'unknown'
            
            G.add_edge(parent_id, node_id, relationship=relationship)

    return G


def visualize_graph(
    graph: GraphData,
    output_path: Path,
    seed_nodes: Set[str] = None,
    visited_nodes: Optional[Set[str]] = None,
    discovered_nodes: Optional[Dict[str, tuple]] = None,
    figsize: tuple = (24, 24),
    dpi: int = 300,
):
    """
    Visualize a GitHub relationship graph using the Pydantic models.
    Handles user-org-repo relationships and fork hierarchy.
    """
    try: 
        G = create_networkx_graph(graph, visited_nodes, discovered_nodes)

        # ---------------------------
        # Visualization
        # ---------------------------
        if len(G.nodes()) == 0:
            logger.warning("No nodes to visualize.")
            return

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor="#2b2b2b")
        ax.set_facecolor("#2b2b2b")

        # Handle disconnected components - position them separately
        components = list(nx.weakly_connected_components(G))
        logger.info(f"Found {len(components)} disconnected component(s)")
        
        pos = {}
        
        # CRITICAL: Use layouts that DON'T produce circular patterns
        # Spring/Fruchterman-Reingold inherently creates circular equilibrium
        # Instead, use a hybrid approach: spectral + force adjustment
        
        if len(components) > 1:
            # Multiple components - layout each independently
            component_data = []
            
            for idx, component in enumerate(components):
                subgraph = G.subgraph(component)
                n_nodes = len(component)
                
                # Choose layout based on connectivity and size
                if n_nodes == 1:
                    # Single node - place at origin
                    node = list(component)[0]
                    sub_pos = {node: (0, 0)}
                elif n_nodes <= 3:
                    # Very small - use simple positions
                    nodes = list(component)
                    sub_pos = {nodes[i]: (i * 2, 0) for i in range(len(nodes))}
                else:
                    # Use spectral layout for non-circular distribution
                    # Spectral uses eigenvectors, doesn't create circular patterns
                    try:
                        sub_pos = nx.spectral_layout(subgraph, scale=3.5)
                        # Add post-processing spring adjustment for extra repulsion
                        optimal_k = 2.0 / math.sqrt(n_nodes)
                        sub_pos = nx.spring_layout(
                            subgraph,
                            pos=sub_pos,
                            k=optimal_k,
                            iterations=50,  # Light adjustment for spacing
                            seed=None
                        )
                        logger.debug(f"Component {idx}: Using spectral+spring layout ({n_nodes} nodes)")
                    except:
                        # Fallback: use random + spring iterations with higher k
                        sub_pos = nx.random_layout(subgraph)
                        optimal_k = 2.0 / math.sqrt(n_nodes)  # Increased from 1.5 for more repulsion
                        sub_pos = nx.spring_layout(
                            subgraph,
                            pos=sub_pos,  # Start from random
                            k=optimal_k,
                            iterations=100,  # Limited iterations to avoid circular convergence
                            seed=None
                        )
                        logger.debug(f"Component {idx}: Using random+spring layout ({n_nodes} nodes)")
                
                # Calculate bounds
                xs = [p[0] for p in sub_pos.values()]
                ys = [p[1] for p in sub_pos.values()]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                width = (max_x - min_x) or 1.0
                height = (max_y - min_y) or 1.0
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                
                component_data.append({
                    'component': component,
                    'pos': sub_pos,
                    'width': width,
                    'height': height,
                    'center': (center_x, center_y),
                    'size': n_nodes
                })
            
            # Sort by size (largest first)
            component_data.sort(key=lambda x: x['size'], reverse=True)
            
            # Arrange components in a SCATTERED pattern (not circle, not grid)
            # Use golden angle for optimal spacing
            golden_angle = math.pi * (3 - math.sqrt(5))  # ~137.5 degrees
            
            for i, data in enumerate(component_data):
                if i == 0:
                    # Place largest at center
                    offset_x, offset_y = 0, 0
                else:
                    # Spiral placement using golden angle
                    angle = i * golden_angle
                    # Distance increases with index (spiral out)
                    radius = math.sqrt(i) * 3
                    offset_x = radius * math.cos(angle)
                    offset_y = radius * math.sin(angle)
                
                # Place component
                for node, (x, y) in data['pos'].items():
                    pos[node] = (x - data['center'][0] + offset_x,
                                y - data['center'][1] + offset_y)
        else:
            # Single connected component
            n_nodes = len(G.nodes())
            
            logger.info(f"Using spectral layout for non-circular organic distribution ({n_nodes} nodes)")
            
            try:
                # Spectral layout uses graph eigenvectors - NO circular patterns
                pos = nx.spectral_layout(G, scale=4.0)
                # Add post-processing spring adjustment for extra repulsion
                optimal_k = 2.0 / math.sqrt(n_nodes) if n_nodes > 1 else 2.0
                pos = nx.spring_layout(
                    G,
                    pos=pos,
                    k=optimal_k,
                    iterations=50,  # Light adjustment for spacing
                    seed=None
                )
                logger.info(f"Using spectral+spring layout for optimal spacing ({n_nodes} nodes)")
            except:
                # Fallback: random initialization + spring with higher k
                logger.info("Spectral failed, using random + spring iterations")
                pos = nx.random_layout(G)
                optimal_k = 2.0 / math.sqrt(n_nodes) if n_nodes > 1 else 2.0  # Increased from 1.5
                pos = nx.spring_layout(
                    G,
                    pos=pos,
                    k=optimal_k,
                    iterations=100,  # Limited to avoid full circular convergence
                    seed=None
                )
        
        # Add jitter to prevent exact overlaps
        # This addresses the issue where nodes with identical connectivity patterns
        # can end up at the exact same position, causing visual overlap
        jitter_strength = 0.05  # 5% of coordinate space
        np.random.seed(42)  # Reproducible jitter
        logger.debug(f"Adding jitter (strength={jitter_strength}) to prevent node overlaps")
        
        for node in pos:
            # Add random offset to both x and y coordinates
            # Convert to numpy array for calculation, then back to tuple/array
            current_pos = np.array(pos[node])
            jitter = np.array([
                np.random.uniform(-jitter_strength, jitter_strength),
                np.random.uniform(-jitter_strength, jitter_strength)
            ])
            pos[node] = current_pos + jitter
        
        # Separate nodes by exploration status and type
        explored_users = []
        explored_orgs = []
        explored_repos = []
        unexplored_nodes = []
        seed_nodes_list = []
        
        for node in G.nodes():
            node_data = G.nodes[node]
            node_type = node_data.get('node_type', 'user')
            is_explored = node_data.get('is_explored', True)
            is_seed = node_data.get('is_seed', False)
            
            if is_seed:
                seed_nodes_list.append(node)
            elif not is_explored:
                unexplored_nodes.append(node)
            elif node_type == 'user':
                explored_users.append(node)
            elif node_type == 'org':
                explored_orgs.append(node)
            elif node_type == 'repo':
                explored_repos.append(node)
        
        logger.debug(f"Node breakdown - Explored: {len(explored_users)} users, {len(explored_orgs)} orgs, "
                    f"{len(explored_repos)} repos | Unexplored: {len(unexplored_nodes)} | Seeds: {len(seed_nodes_list)}")
        
        # Draw unexplored nodes first (in background, grey)
        if unexplored_nodes:
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=unexplored_nodes,
                node_color='#666666',  # Grey
                node_size=150,
                node_shape='o',
                alpha=0.4,  # Semi-transparent
                edgecolors='#444444',
                linewidths=1,
                ax=ax
            )
        
        # Draw explored users (circles)
        if explored_users:
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=explored_users,
                node_color=COLOR_MAP['user'],
                node_size=180,
                node_shape='o',
                alpha=0.85,
                edgecolors='#ffffff',
                linewidths=1.5,
                ax=ax
            )
        
        # Draw explored orgs (circles)
        if explored_orgs:
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=explored_orgs,
                node_color=COLOR_MAP['org'],
                node_size=180,
                node_shape='o',
                alpha=0.85,
                edgecolors='#ffffff',
                linewidths=1.5,
                ax=ax
            )
        
        # Draw explored repos (circles)
        if explored_repos:
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=explored_repos,
                node_color=COLOR_MAP['repo'],
                node_size=180,
                node_shape='o',
                alpha=0.85,
                edgecolors='#ffffff',
                linewidths=1.5,
                ax=ax
            )
        
        # Draw seed nodes on top (squares) with thicker borders
        if seed_nodes_list:
            seed_colors = [COLOR_MAP.get(G.nodes[n].get('node_type', 'user'), '#00d9ff') 
                            for n in seed_nodes_list]
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=seed_nodes_list,
                node_color=seed_colors,
                node_size=320,
                node_shape='s',
                alpha=0.95,
                edgecolors='#ffffff',
                linewidths=2.5,
                ax=ax
            )
        
        # Draw edges with color coding by relationship type
        edge_lists_by_type = {}
        for u, v, data in G.edges(data=True):
            rel_type = data.get('relationship', 'unknown')
            if rel_type not in edge_lists_by_type:
                edge_lists_by_type[rel_type] = []
            edge_lists_by_type[rel_type].append((u, v))
        
        # Draw each edge type with its own color (straight lines)
        for rel_type, edges in edge_lists_by_type.items():
            edge_color = EDGE_COLOR_MAP.get(rel_type, '#ffffff')
            nx.draw_networkx_edges(
                G, pos,
                edgelist=edges,
                edge_color=edge_color,
                alpha=0.5,
                arrows=True,
                arrowsize=15,
                arrowstyle='->',
                width=2.0,
                ax=ax
            )
        
        # Draw labels with smart positioning (offset from nodes)
        # Always show: seed nodes + all organizations + (all nodes if small graph)
        labels_to_show = {}
        
        if len(G.nodes()) <= 50:
            # Small graphs: show all labels
            labels_to_show = {n: G.nodes[n].get('label', n)[:20] for n in G.nodes()}
        else:
            # Large graphs: show seed nodes + all organizations
            for node in G.nodes():
                node_data = G.nodes[node]
                is_seed = node_data.get('is_seed', False)
                is_org = node_data.get('node_type') == 'org'
                
                if is_seed or is_org:
                    labels_to_show[node] = node_data.get('label', node)[:20]
        
        if labels_to_show:
            
            if HAS_ADJUST_TEXT and len(labels_to_show) > 0:
                # Use adjustText for smart label placement with arrows
                texts = []
                for node, label in labels_to_show.items():
                    x, y = pos[node]
                    text = ax.text(
                        x, y, label,
                        fontsize=7,
                        fontweight='bold',
                        color='#ffffff',
                        ha='center',
                        va='center',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#3a3a3a', edgecolor='#ffffff', linewidth=0.5, alpha=0.8)
                    )
                    texts.append(text)
                
                # Adjust text positions to avoid overlap and add arrows
                adjust_text(
                    texts,
                    arrowprops=dict(arrowstyle='->', color='#ffffff', lw=0.8, alpha=0.6),
                    expand_points=(1.5, 1.5),
                    force_text=(0.5, 0.5),
                    force_points=(0.2, 0.2),
                    ax=ax
                )
            else:
                # Fallback: place labels on nodes (old behavior)
                nx.draw_networkx_labels(
                    G, pos,
                    labels=labels_to_show,
                    font_size=7,
                    font_weight='bold',
                    font_color='#ffffff',
                    ax=ax
                )
        
        # Create legend with modern styling (nodes and edges)
        legend_elements = [
            mpatches.Patch(facecolor=COLOR_MAP['user'], label='User (explored)', edgecolor='#ffffff', linewidth=1),
            mpatches.Patch(facecolor=COLOR_MAP['org'], label='Organization (explored)', edgecolor='#ffffff', linewidth=1),
            mpatches.Patch(facecolor=COLOR_MAP['repo'], label='Repository (explored)', edgecolor='#ffffff', linewidth=1),
        ]
        
        # Add unexplored indicator if there are unexplored nodes
        if unexplored_nodes:
            legend_elements.append(
                mpatches.Patch(facecolor='#666666', label='Unexplored', edgecolor='#444444', linewidth=1, alpha=0.4)
            )
        
        # Add seed indicator
        legend_elements.append(
            mpatches.Patch(facecolor='#666666', edgecolor='#ffffff', linewidth=2, label='Seed Node (square)')
        )
        
        # Add spacer and edge relationships
        legend_elements.append(mpatches.Patch(facecolor='none', edgecolor='none', label=''))  # Spacer
        legend_elements.extend([
            mpatches.Patch(facecolor=EDGE_COLOR_MAP['owner_of'], label='Owner of', edgecolor='#ffffff', linewidth=1),
            mpatches.Patch(facecolor=EDGE_COLOR_MAP['contributor_of'], label='Contributor of', edgecolor='#ffffff', linewidth=1),
            mpatches.Patch(facecolor=EDGE_COLOR_MAP['member_of'], label='Member of', edgecolor='#ffffff', linewidth=1),
            mpatches.Patch(facecolor=EDGE_COLOR_MAP['parent_of'], label='Parent of (fork)', edgecolor='#ffffff', linewidth=1),
        ])
        legend = ax.legend(
            handles=legend_elements, 
            loc='upper left', 
            fontsize=11,
            framealpha=0.9,
            facecolor='#3a3a3a',
            edgecolor='#ffffff',
            labelcolor='#ffffff'
        )
        
        # Title and styling with modern aesthetics
        component_info = f' | {len(components)} cluster(s)' if len(components) > 1 else ''
        ax.set_title(
            f'GitHub Network Graph\n'
            f'{len(graph.users)} Users • {len(graph.orgs)} Organizations • {len(graph.repos)} Repositories{component_info}',
            fontsize=18,
            fontweight='bold',
            color='#ffffff',
            pad=20
        )
        ax.axis('off')
        
        # Save
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Graph visualization saved to {output_path}")
        logger.info(f"Nodes: {len(G.nodes())}, Edges: {len(G.edges())}")

    except Exception as e:
        logger.error(f"Failed to create visualization: {e}")
        raise



def visualize_clusters(
    graph: GraphData,
    output_dir: Path,
    cluster_prefix_name: str,
    figsize: tuple = (16, 16),
    dpi: int = 300
):
    """
    Create separate visualizations for each disconnected cluster in the graph.

    Args:
        graph: GraphData to visualize
        output_dir: Directory to save cluster visualizations
        figsize: Figure size for each cluster visualization
        dpi: Resolution in dots per inch
    """
    if not VISUALIZATION_AVAILABLE:
        logger.error("Visualization requires networkx and matplotlib. Install with: pip install networkx matplotlib")
        return

    try:
        G = create_networkx_graph(graph)

        if len(G.nodes()) == 0:
            logger.warning("No nodes to visualize.")
            return

        # Get disconnected components
        components = list(nx.weakly_connected_components(G))
        logger.info(f"Creating separate visualizations for {len(components)} cluster(s)")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Visualize each component separately
        for idx, component in enumerate(sorted(components, key=len, reverse=True), 1):
            subgraph = G.subgraph(component)
            
            # Create figure with dark background
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor='#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            # Layout for non-circular organic distribution
            n_nodes = len(component)
            
            logger.debug(f"Cluster {idx}: Using spectral layout for non-circular distribution ({n_nodes} nodes)")
            
            # Use spectral layout to avoid circular patterns
            try:
                pos = nx.spectral_layout(subgraph, scale=4.0)
                # Add post-processing spring adjustment for extra repulsion
                optimal_k = 2.0 / math.sqrt(n_nodes) if n_nodes > 1 else 2.0
                pos = nx.spring_layout(
                    subgraph,
                    pos=pos,
                    k=optimal_k,
                    iterations=50,  # Light adjustment for spacing
                    seed=None
                )
                logger.debug(f"Cluster {idx}: Using spectral+spring layout ({n_nodes} nodes)")
            except:
                # Fallback: random + spring with higher k
                logger.debug(f"Cluster {idx}: Spectral failed, using random + spring")
                pos = nx.random_layout(subgraph)
                optimal_k = 2.0 / math.sqrt(n_nodes) if n_nodes > 1 else 2.0  # Increased from 1.5
                pos = nx.spring_layout(
                    subgraph,
                    pos=pos,
                    k=optimal_k,
                    iterations=100,  # Limited iterations
                    seed=None
                )
            
            # Separate nodes by exploration status
            component_seed_nodes = [n for n in component if subgraph.nodes[n].get('is_seed', False)]
            component_explored_nodes = [n for n in component 
                                      if not subgraph.nodes[n].get('is_seed', False) 
                                      and subgraph.nodes[n].get('is_explored', True)]
            component_unexplored_nodes = [n for n in component 
                                         if not subgraph.nodes[n].get('is_seed', False)
                                         and not subgraph.nodes[n].get('is_explored', True)]
            
            # Draw unexplored nodes in grey (discovered but not yet explored)
            if component_unexplored_nodes:
                nx.draw_networkx_nodes(
                    subgraph, pos,
                    nodelist=component_unexplored_nodes,
                    node_color='#666666',  # Grey for unexplored
                    node_size=180,
                    node_shape='o',
                    alpha=0.4,  # More transparent
                    edgecolors='#ffffff',
                    linewidths=1.0,
                    ax=ax
                )
            
            # Draw explored regular nodes
            if component_explored_nodes:
                explored_colors = [COLOR_MAP.get(subgraph.nodes[n].get('node_type', 'user'), '#ffffff') 
                                for n in component_explored_nodes]
                nx.draw_networkx_nodes(
                    subgraph, pos,
                    nodelist=component_explored_nodes,
                    node_color=explored_colors,
                    node_size=180,
                    node_shape='o',
                    alpha=0.85,
                    edgecolors='#ffffff',
                    linewidths=1.5,
                    ax=ax
                )
            
            # Draw seed nodes (always explored)
            if component_seed_nodes:
                seed_colors = [COLOR_MAP.get(subgraph.nodes[n].get('node_type', 'user'), '#ffffff') 
                              for n in component_seed_nodes]
                nx.draw_networkx_nodes(
                    subgraph, pos,
                    nodelist=component_seed_nodes,
                    node_color=seed_colors,
                    node_size=320,
                    node_shape='s',
                    alpha=0.95,
                    edgecolors='#ffffff',
                    linewidths=2.5,
                    ax=ax
                )
            
            # Draw edges with color coding by relationship type
            edge_lists_by_type = {}
            for u, v, data in subgraph.edges(data=True):
                rel_type = data.get('relationship', 'unknown')
                if rel_type not in edge_lists_by_type:
                    edge_lists_by_type[rel_type] = []
                edge_lists_by_type[rel_type].append((u, v))
            
            # Draw each edge type with its own color (straight lines)
            for rel_type, edges in edge_lists_by_type.items():
                edge_color = EDGE_COLOR_MAP.get(rel_type, '#ffffff')
                nx.draw_networkx_edges(
                    subgraph, pos,
                    edgelist=edges,
                    edge_color=edge_color,
                    alpha=0.5,
                    arrows=True,
                    arrowsize=15,
                    arrowstyle='->',
                    width=2.0,
                    ax=ax
                )
            
            # Draw labels with smart positioning
            if len(component) <= 30:
                labels_to_show = {n: subgraph.nodes[n].get('label', n)[:25] for n in component}
            else:
                labels_to_show = {n: subgraph.nodes[n].get('label', n)[:20] for n in component_seed_nodes}
            
            if labels_to_show:
                if HAS_ADJUST_TEXT and len(labels_to_show) <= 30:
                    # Use adjustText for smaller clusters
                    texts = []
                    for node, label in labels_to_show.items():
                        x, y = pos[node]
                        text = ax.text(
                            x, y, label,
                            fontsize=8,
                            fontweight='bold',
                            color='#ffffff',
                            ha='center',
                            va='center',
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='#3a3a3a', edgecolor='#ffffff', linewidth=0.5, alpha=0.8)
                        )
                        texts.append(text)
                    
                    # Adjust text positions
                    adjust_text(
                        texts,
                        arrowprops=dict(arrowstyle='->', color='#ffffff', lw=0.8, alpha=0.6),
                        expand_points=(1.5, 1.5),
                        force_text=(0.5, 0.5),
                        force_points=(0.2, 0.2),
                        ax=ax
                    )
                else:
                    # Fallback for large clusters or when adjustText not available
                    nx.draw_networkx_labels(
                        subgraph, pos,
                        labels=labels_to_show,
                        font_size=8,
                        font_weight='bold',
                        font_color='#ffffff',
                        ax=ax
                    )
            
            # Count node types in this cluster
            users_count = sum(1 for n in component if subgraph.nodes[n].get('node_type') == 'user')
            orgs_count = sum(1 for n in component if subgraph.nodes[n].get('node_type') == 'org')
            repos_count = sum(1 for n in component if subgraph.nodes[n].get('node_type') == 'repo')
            
            # Create legend with node types and edge types
            legend_elements = [
                mpatches.Patch(facecolor=COLOR_MAP['user'], label=f'User ({users_count})', edgecolor='#ffffff', linewidth=1),
                mpatches.Patch(facecolor=COLOR_MAP['org'], label=f'Organization ({orgs_count})', edgecolor='#ffffff', linewidth=1),
                mpatches.Patch(facecolor=COLOR_MAP['repo'], label=f'Repository ({repos_count})', edgecolor='#ffffff', linewidth=1),
            ]
            if component_seed_nodes:
                legend_elements.append(
                    mpatches.Patch(facecolor='#666666', edgecolor='#ffffff', linewidth=2, label='Seed Node')
                )
            if component_unexplored_nodes:
                legend_elements.append(
                    mpatches.Patch(facecolor='#666666', alpha=0.4, edgecolor='#ffffff', linewidth=1, label='Unexplored Node')
                )
            
            # Add edge type legend
            legend_elements.append(mpatches.Patch(facecolor='none', edgecolor='none', label=''))  # Spacer
            for rel_type in edge_lists_by_type.keys():
                if rel_type in EDGE_COLOR_MAP:
                    legend_elements.append(
                        mpatches.Patch(facecolor=EDGE_COLOR_MAP[rel_type], label=rel_type.title(), edgecolor='#ffffff', linewidth=1)
                    )
            
            ax.legend(
                handles=legend_elements,
                loc='upper left',
                fontsize=10,
                framealpha=0.9,
                facecolor='#3a3a3a',
                edgecolor='#ffffff',
                labelcolor='#ffffff'
            )
            
            # Title
            ax.set_title(
                f'Cluster {idx} of {len(components)}\n'
                f'{len(component)} nodes • {len(subgraph.edges())} edges',
                fontsize=16,
                fontweight='bold',
                color='#ffffff',
                pad=20
            )
            ax.axis('off')
            
            # Save
            cluster_path = output_dir / f'{cluster_prefix_name}_cluster_{idx:02d}.png'
            plt.tight_layout()
            plt.savefig(cluster_path, dpi=dpi, bbox_inches='tight', facecolor='#2b2b2b')
            plt.close()
            
            logger.info(f"Cluster {idx} visualization saved to {cluster_path} ({len(component)} nodes)")

    except Exception as e:
        logger.error(f"Failed to create cluster visualizations: {e}")
        raise