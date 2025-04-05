import re
import networkx as nx
import matplotlib.pyplot as plt
import json

# === CONFIG ===
file_path = "../BenchFiles/s27.bench"  # Change this to any .bench file you want to use

# === PARSE NETLIST FILE ===
with open(file_path, "r") as f:
    lines = f.readlines()

primary_inputs = set()
primary_outputs = set()
gates = set()
edges = []

for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("INPUT("):
        pi = re.findall(r"INPUT\((.*?)\)", line)[0]
        primary_inputs.add(pi)
    elif line.startswith("OUTPUT("):
        po = re.findall(r"OUTPUT\((.*?)\)", line)[0]
        primary_outputs.add(po)
    elif "=" in line:
        left, right = line.split("=")
        gate = left.strip()
        gates.add(gate)
        inputs = re.findall(r"\((.*?)\)", right)[0].split(",")
        inputs = [inp.strip() for inp in inputs]
        for inp in inputs:
            edges.append((inp, gate))

# Add gate → output edges
for po in primary_outputs:
    for line in lines:
        if line.startswith(po + " ="):
            source = re.findall(r"\((.*?)\)", line)[0].split(",")[0].strip()
            edges.append((source, po))

# === BUILD DIRECTED GRAPH ===
DG = nx.DiGraph()
DG.add_edges_from(edges)

# === ASSIGN COLORS ===
color_map = []
for node in DG.nodes():
    if node in primary_inputs:
        color_map.append("green")
    elif node in primary_outputs:
        color_map.append("red")
    else:
        color_map.append("skyblue")

# === DRAW GRAPH ===
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(DG, seed=42)
nx.draw(DG, pos, with_labels=True, node_color=color_map, node_size=1000, font_size=10, arrows=True)
plt.title("Directed Netlist Graph\nPrimary Inputs (Green), Outputs (Red), Gates (Blue)")
plt.show()

## === Save Nodes and Edges to File ===


# Convert graph to dict
graph_data = {
    "nodes": list(DG.nodes),
    "edges": list(DG.edges)
}

# Save to JSON file
with open("netlist_graph.json", "w") as f:
    json.dump(graph_data, f, indent=2)
