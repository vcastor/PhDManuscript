#!/usr/bin/python3
import matplotlib.pyplot as plt
import networkx as nx

# Create a graph
G = nx.Graph()

# Define positions for the nodes
positions = {
    "A": (110.1, 106.1),
    "B": (250.1, 147.1),
    "C": (140.5, 249.5),
    "D": (350.2, 251.7),
    "E": (241, 350.3)
}

# Add nodes and edges
G.add_nodes_from(positions.keys())
edges = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("D", "E")]
G.add_edges_from(edges)

# Plot the graph
plt.figure(figsize=(8, 8))

# Draw nodes with a black border (circle), white background, and black edges
nx.draw(
    G, positions,
    with_labels=True,
    node_size=9000,      # Size of circles
    node_color='white',
    edgecolors='black',
    font_size=36,
    font_weight='bold',
    edge_color='black',
    width=5,             # Width of edges
    linewidths=5,        # Width of node borders
)

plt.savefig("abcde_charges.pdf")
# plt.show()

