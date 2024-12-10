import json
import networkx as nx

import json
import networkx as nx

def load_graph_data(graph_file):
    """Load graph data from a JSON file."""
    with open(graph_file, 'r') as f:
        graph_data = json.load(f)
    print(f"Loaded graph data with {len(graph_data[1]['instruction_control_instruction'])} edges.")
    return graph_data

def create_graph_from_json(graph_data):
    """Create a directed graph from JSON data without altering node details."""
    G = nx.DiGraph()
    for edge in graph_data[1]["instruction_control_instruction"]:
        G.add_edge(edge[0], edge[1])
    
    # Preserve node attributes as they are in the JSON
    for idx, instruction in enumerate(graph_data[0]["instruction"]):
        if idx in G.nodes():
            G.nodes[idx]["color"] = "blue"
            G.nodes[idx]["label"] = f"Node {idx}"
    
    print(f"Graph contains {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

def save_graph_to_dot(G, output_file):
    """Save graph to a DOT file for visualization."""
    nx.drawing.nx_pydot.write_dot(G, output_file)
    print(f"Graph saved to {output_file}")

if __name__ == "__main__":
    graph_file = "minmax.json"
    output_dot_file = "PDG_Original.dot"

    graph_data = load_graph_data(graph_file)
    G = create_graph_from_json(graph_data)
    save_graph_to_dot(G, output_dot_file)
