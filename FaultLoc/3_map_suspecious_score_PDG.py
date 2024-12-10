import json
import networkx as nx
import re

def load_data(graph_file, score_file):
    with open(graph_file, 'r') as f:
        graph_data = json.load(f)
    scores = {}
    with open(score_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("Line"):
                print(f"Skipping invalid line: {line}")
                continue
            match = re.match(r"Line (\d+): Suspiciousness ([0-9.]+)", line)
            if match:
                line_number = int(match.group(1))
                score = float(match.group(2))
                scores[line_number] = score
            else:
                print(f"Skipping invalid line: {line}")
    print(f"Loaded {len(graph_data)} graph entries and {len(scores)} scores.")
    return graph_data, scores


def map_scores_to_instructions(graph_data, scores):
    instruction_mapping = {}
    for idx, instruction in enumerate(graph_data[0]["instruction"]):
        if instruction[1] and len(instruction[1]) > 0:
            code = instruction[1][0]  # First element of the instruction
            print(f"Processing instruction: {code}")  # Debug
            # Match line numbers from the instruction
            line_match = re.search(r"\(Line\s+(\d+)\)", code)
            if line_match:
                line_number = int(line_match.group(1))
                print(f"Matched line number: {line_number}")  # Debug
                if line_number in scores:
                    instruction_mapping[line_number] = idx
                    print(f"Mapped line {line_number} to instruction {idx}")  # Debug
            else:
                print(f"No line number found in instruction: {code}")  # Debug
    print(f"Total mapped instructions: {len(instruction_mapping)}")
    return instruction_mapping



def create_highlighted_graph(graph_data, scores, instruction_mapping):
    G = nx.DiGraph()
    for edge in graph_data[1]["instruction_control_instruction"]:
        G.add_edge(edge[0], edge[1])
    
    for node in G.nodes():
        line_number = None
        for ln, mapped_node in instruction_mapping.items():
            if node == mapped_node:
                line_number = ln
                break
        score = scores.get(line_number, 0) if line_number else 0
        if score > 0.6:
            G.nodes[node]["color"] = "red"
            G.nodes[node]["label"] = f"High ({score:.2f})"
        elif score > 0.4:
            G.nodes[node]["color"] = "yellow"
            G.nodes[node]["label"] = f"Medium ({score:.2f})"
        elif score > 0:
            G.nodes[node]["color"] = "green"
            G.nodes[node]["label"] = f"Low ({score:.2f})"
        else:
            G.nodes[node]["color"] = "blue"
            G.nodes[node]["label"] = "Not Suspicious"
    print(f"Graph contains {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G


def save_graph_to_dot(G, output_file):
    """Save graph to a DOT file for visualization."""
    nx.drawing.nx_pydot.write_dot(G, output_file)
    print(f"Graph saved to {output_file}")


if __name__ == "__main__":
    graph_file = "updated_minmax.json"
    score_file = "score.log"
    output_dot_file = "highlighted_pdg.dot"

    graph_data, scores = load_data(graph_file, score_file)
    if graph_data and scores:
        instruction_mapping = map_scores_to_instructions(graph_data, scores)
        G = create_highlighted_graph(graph_data, scores, instruction_mapping)
        save_graph_to_dot(G, output_dot_file)
