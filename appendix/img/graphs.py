#!/usr/bin/python3
import matplotlib.pyplot as plt
import networkx as nx

# Common styling function
def draw_graph(G, positions, title, filename):
    plt.figure(figsize=(8, 8))
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
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.savefig(filename)

# 1. Zigzag Chain [A-B-C-D] - flatter, more horizontal
G1 = nx.Graph()
zigzag_positions = {
    "A": (0, 0),
    "B": (150, 30),
    "C": (300, -30),
    "D": (450, 0)
}
G1.add_nodes_from(zigzag_positions.keys())
zigzag_edges = [("A", "B"), ("B", "C"), ("C", "D")]
G1.add_edges_from(zigzag_edges)
draw_graph(G1, zigzag_positions, "Flat Zigzag Chain: A-B-C-D", "chain.pdf")

# 2. Ring with four elements
G2 = nx.Graph()
ring_positions = {
    "A": (0, 100),      # Top
    "B": (100, 0),      # Right
    "C": (0, -100),     # Bottom
    "D": (-100, 0)      # Left
}
G2.add_nodes_from(ring_positions.keys())
ring_edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")]
G2.add_edges_from(ring_edges)
draw_graph(G2, ring_positions, "Ring: A-B-C-D-A", "ring_graph.pdf")

# 3. Tree structure: A-B,A-C down; D right; B-E up (zigzag); C-F,D-G down with angle
G3 = nx.Graph()
tree_positions = {
    "A": (0, 150),      # Root at center-top
    "B": (-90, 60),     # Down and left from A (~127 units)
    "C": (20, 60),       # Down from A (130 units)
    "D": (150, 150),    # To the right of A (130 units)
    "E": (-180, 150),   # Same y as A and D for horizontal alignment
    "F": (70, -20),     # Moved up to compress image height
    "G": (190, 70)      # Down from D with small angle (~134 units)
}
G3.add_nodes_from(tree_positions.keys())
tree_edges = [("A", "B"), ("A", "C"), ("A", "D"), ("B", "E"), ("C", "F"), ("D", "G")]
G3.add_edges_from(tree_edges)
draw_graph(G3, tree_positions, "Tree: A-{B↓,C↓,D→} then {B-E↑, C-F↓, D-G↓}", "tree_graph.pdf")

# 4. Pyramid projection: Triangle [A-B-C] with center D connected to all
G4 = nx.Graph()
pyramid_positions = {
    "A": (0, 150),      # Top of triangle
    "B": (-130, -75),   # Bottom left of triangle
    "C": (130, -75),    # Bottom right of triangle
    "D": (0, 0)         # Center
}
G4.add_nodes_from(pyramid_positions.keys())
pyramid_edges = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "A"), ("D", "B"), ("D", "C")]
G4.add_edges_from(pyramid_edges)
draw_graph(G4, pyramid_positions, "Pyramid Projection: Triangle ABC with center D", "pyramid_graph.pdf")

