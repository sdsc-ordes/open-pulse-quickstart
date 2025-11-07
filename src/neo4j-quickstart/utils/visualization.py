"""Visualization utilities for graph rendering."""

import logging
import math
from pathlib import Path
from typing import Set, Optional

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

def create_networkx_graph(graph: GraphData) -> Optional[nx.DiGraph]:
    # Create directed graph
    G = nx.DiGraph()

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
        if repo.parent_of and repo.parent_of in graph.repos:
            G.add_edge(repo.name, repo.parent_of, relationship="parent_of")
    return G


def visualize_graph(
    graph: GraphData,
    output_path: Path,
    figsize: tuple = (24, 24),
    dpi: int = 300,
):
    """
    Visualize a GitHub relationship graph using the Pydantic models.
    Handles user-org-repo relationships and fork hierarchy.
    """
    G = create_networkx_graph(graph)

    # ---------------------------
    # Visualization
    # ---------------------------
    if len(G.nodes()) == 0:
        logger.warning("No nodes to visualize.")
        return

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor="#2b2b2b")
    ax.set_facecolor("#2b2b2b")

    # Layout
    n_nodes = len(G.nodes())
    try:
        pos = nx.spectral_layout(G, scale=4.0)
        optimal_k = 2.0 / math.sqrt(n_nodes) if n_nodes > 1 else 2.0
        pos = nx.spring_layout(G, pos=pos, k=optimal_k, iterations=50)
    except Exception:
        pos = nx.spring_layout(G, k=2.0 / math.sqrt(n_nodes))

    # Node colors
    node_colors = [
        COLOR_MAP.get(G.nodes[n].get("node_type", "user"), "#ffffff")
        for n in G.nodes()
    ]

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_colors,
        node_size=200,
        node_shape="o",
        alpha=0.9,
        edgecolors="#ffffff",
        linewidths=1.5,
        ax=ax,
    )

    # Edges
    edge_lists_by_type = {}
    for u, v, data in G.edges(data=True):
        rel_type = data.get("relationship", "unknown")
        edge_lists_by_type.setdefault(rel_type, []).append((u, v))

    for rel_type, edges in edge_lists_by_type.items():
        edge_color = EDGE_COLOR_MAP.get(rel_type, "#ffffff")
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=edges,
            edge_color=edge_color,
            alpha=0.5,
            arrows=True,
            arrowsize=15,
            arrowstyle="->",
            width=2.0,
            ax=ax,
        )

    # Labels
    if len(G.nodes()) <= 80:
        labels_to_show = {n: G.nodes[n].get("label", n) for n in G.nodes()}
        if HAS_ADJUST_TEXT:
            texts = []
            for node, label in labels_to_show.items():
                x, y = pos[node]
                text = ax.text(
                    x,
                    y,
                    label,
                    fontsize=7,
                    fontweight="bold",
                    color="#ffffff",
                    ha="center",
                    va="center",
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="#3a3a3a",
                        edgecolor="#ffffff",
                        linewidth=0.5,
                        alpha=0.8,
                    ),
                )
                texts.append(text)
            adjust_text(
                texts,
                arrowprops=dict(
                    arrowstyle="->", color="#ffffff", lw=0.8, alpha=0.6
                ),
                expand_points=(1.5, 1.5),
                force_text=(0.5, 0.5),
                force_points=(0.2, 0.2),
                ax=ax,
            )
        else:
            nx.draw_networkx_labels(
                G,
                pos,
                labels=labels_to_show,
                font_size=7,
                font_weight="bold",
                font_color="#ffffff",
                ax=ax,
            )

    # Legend
    legend_elements = [
        mpatches.Patch(
            facecolor=COLOR_MAP["user"],
            label="User",
            edgecolor="#ffffff",
            linewidth=1,
        ),
        mpatches.Patch(
            facecolor=COLOR_MAP["org"],
            label="Organization",
            edgecolor="#ffffff",
            linewidth=1,
        ),
        mpatches.Patch(
            facecolor=COLOR_MAP["repo"],
            label="Repository",
            edgecolor="#ffffff",
            linewidth=1,
        ),
        mpatches.Patch(facecolor="none", edgecolor="none", label=""),
    ]
    for rel, color in EDGE_COLOR_MAP.items():
        legend_elements.append(
            mpatches.Patch(
                facecolor=color,
                label=rel.replace("_", " ").title(),
                edgecolor="#ffffff",
                linewidth=1,
            )
        )

    # Place legend outside the plot for large graphs to prevent clipping
    ax.legend(
        handles=legend_elements,
        fontsize=11,
        framealpha=0.9,
        facecolor='#3a3a3a',
        edgecolor='#ffffff',
        labelcolor='#ffffff',
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
        bbox_transform=fig.transFigure
    )

    # Adjust layout manually
    fig.subplots_adjust(right=0.80)  # Leave space for the legend

    ax.set_title(
        f"GitHub Network Graph\n"
        f"{len(graph.users)} Users • {len(graph.orgs)} Orgs • {len(graph.repos)} Repos",
        fontsize=18,
        fontweight="bold",
        color="#ffffff",
        pad=20,
    )
    ax.axis("off")

    # plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="#2b2b2b")
    plt.close()

    logger.info(f"Graph visualization saved to {output_path}")


def visualize_clusters(
    graph: GraphData,
    output_dir: Path,
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

        # Visualize each cluster
        for idx, component in enumerate(sorted(components, key=len, reverse=True), 1):
            subgraph = G.subgraph(component)

            # Figure setup
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor='#2b2b2b')
            ax.set_facecolor('#2b2b2b')

            n_nodes = len(component)
            logger.debug(f"Cluster {idx}: {n_nodes} nodes")

            # Use spectral+spring layout for non-circular spacing
            try:
                pos = nx.spectral_layout(subgraph, scale=4.0)
                optimal_k = 2.0 / math.sqrt(n_nodes) if n_nodes > 1 else 2.0
                pos = nx.spring_layout(subgraph, pos=pos, k=optimal_k, iterations=50, seed=None)
            except Exception:
                pos = nx.random_layout(subgraph)
                optimal_k = 2.0 / math.sqrt(n_nodes) if n_nodes > 1 else 2.0
                pos = nx.spring_layout(subgraph, pos=pos, k=optimal_k, iterations=100, seed=None)

            # Draw nodes
            node_colors = [COLOR_MAP.get(subgraph.nodes[n].get('node_type', 'user'), '#ffffff') for n in subgraph.nodes()]
            nx.draw_networkx_nodes(
                subgraph, pos,
                node_color=node_colors,
                node_size=220,
                node_shape='o',
                alpha=0.85,
                edgecolors='#ffffff',
                linewidths=1.5,
                ax=ax
            )

            # Draw edges grouped by relationship type
            edge_lists_by_type = {}
            for u, v, data in subgraph.edges(data=True):
                rel_type = data.get('relationship', 'unknown')
                edge_lists_by_type.setdefault(rel_type, []).append((u, v))

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

            # Labels (only for smaller clusters or key nodes)
            if len(component) <= 50:
                labels_to_show = {n: subgraph.nodes[n].get('label', n)[:25] for n in component}
            else:
                # For large clusters, show only repos (most meaningful)
                labels_to_show = {n: subgraph.nodes[n].get('label', n)[:25]
                                  for n in component if subgraph.nodes[n].get('node_type') == 'repo'}

            if labels_to_show:
                if HAS_ADJUST_TEXT and len(labels_to_show) <= 50:
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
                            bbox=dict(boxstyle='round,pad=0.3',
                                      facecolor='#3a3a3a',
                                      edgecolor='#ffffff',
                                      linewidth=0.5,
                                      alpha=0.8)
                        )
                        texts.append(text)
                    adjust_text(
                        texts,
                        arrowprops=dict(arrowstyle='->', color='#ffffff', lw=0.8, alpha=0.6),
                        expand_points=(1.5, 1.5),
                        force_text=(0.5, 0.5),
                        force_points=(0.2, 0.2),
                        ax=ax
                    )
                else:
                    nx.draw_networkx_labels(
                        subgraph, pos,
                        labels=labels_to_show,
                        font_size=8,
                        font_weight='bold',
                        font_color='#ffffff',
                        ax=ax
                    )

            # Count node types for legend
            users_count = sum(1 for n in component if subgraph.nodes[n].get('node_type') == 'user')
            orgs_count = sum(1 for n in component if subgraph.nodes[n].get('node_type') == 'org')
            repos_count = sum(1 for n in component if subgraph.nodes[n].get('node_type') == 'repo')

            # Legend setup
            legend_elements = [
                mpatches.Patch(facecolor=COLOR_MAP['user'], label=f'User ({users_count})', edgecolor='#ffffff', linewidth=1),
                mpatches.Patch(facecolor=COLOR_MAP['org'], label=f'Organization ({orgs_count})', edgecolor='#ffffff', linewidth=1),
                mpatches.Patch(facecolor=COLOR_MAP['repo'], label=f'Repository ({repos_count})', edgecolor='#ffffff', linewidth=1),
                mpatches.Patch(facecolor='none', edgecolor='none', label=''),
            ]

            for rel_type in edge_lists_by_type.keys():
                if rel_type in EDGE_COLOR_MAP:
                    legend_elements.append(
                        mpatches.Patch(facecolor=EDGE_COLOR_MAP[rel_type], label=rel_type.replace('_', ' ').title(), edgecolor='#ffffff', linewidth=1)
                    )

            # Anchor legend outside the plot (prevents clipping)
            ax.legend(
                handles=legend_elements,
                fontsize=10,
                framealpha=0.9,
                facecolor='#3a3a3a',
                edgecolor='#ffffff',
                labelcolor='#ffffff',
                loc='upper left',
                bbox_to_anchor=(1.02, 1),
                borderaxespad=0,
                bbox_transform=fig.transFigure
            )

            fig.subplots_adjust(right=0.80)

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

            # Save cluster image
            cluster_path = output_dir / f'cluster_{idx:02d}.png'
            plt.savefig(cluster_path, dpi=dpi, bbox_inches='tight', facecolor='#2b2b2b')
            plt.close()

            logger.info(f"Cluster {idx} visualization saved to {cluster_path} ({len(component)} nodes)")

    except Exception as e:
        logger.error(f"Failed to create cluster visualizations: {e}")
        raise