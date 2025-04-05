import re
import networkx as nx
import matplotlib.pyplot as plt
import json

# Load Verilog file
with open("../BenchFiles/s27.v", "r") as file:
    verilog_text = file.read()

# Initialize sets
primary_inputs = set()
primary_outputs = set()
ignore_signals = {"CK", "VDD", "GND"}

# Parse inputs and outputs
input_match = re.search(r'input\s+([^;]+);', verilog_text)
output_match = re.search(r'output\s+([^;]+);', verilog_text)

if input_match:
    primary_inputs = set(re.findall(r'\b\w+\b', input_match.group(1))) - ignore_signals
if output_match:
    primary_outputs = set(re.findall(r'\b\w+\b', output_match.group(1)))

# Parse all gate declarations
gate_lines = re.findall(r'(dff|not|and|or|nand|nor)\s+(\w+)\s*\(([^)]+)\);', verilog_text, re.IGNORECASE)

# Create graph
G = nx.DiGraph()
signal_to_gate = {}

# Add primary nodes
for inp in primary_inputs:
    G.add_node(inp, type='input')
for outp in primary_outputs:
    G.add_node(outp, type='output')

# Process gates
for gate_type, gate_name, args_str in gate_lines:
    args = [arg.strip() for arg in args_str.split(",") if arg.strip() not in ignore_signals]
    gate_type = gate_type.lower()
    G.add_node(gate_name, type='gate')

    if gate_type == "dff":
        if len(args) >= 2:
            output_sig = args[0]
            input_sig = args[1]
            signal_to_gate[output_sig] = gate_name
            if input_sig in signal_to_gate:
                G.add_edge(signal_to_gate[input_sig], gate_name)
            elif input_sig in primary_inputs:
                G.add_edge(input_sig, gate_name)
    else:
        if not args:
            continue
        output_sig = args[0]
        input_sigs = args[1:]
        signal_to_gate[output_sig] = gate_name
        for sig in input_sigs:
            if sig in signal_to_gate:
                G.add_edge(signal_to_gate[sig], gate_name)
            elif sig in primary_inputs:
                G.add_edge(sig, gate_name)

# Link outputs and consumers
for sig, producer_gate in signal_to_gate.items():
    for gate_type, gate_name, args_str in gate_lines:
        args = [arg.strip() for arg in args_str.split(",") if arg.strip() not in ignore_signals]
        if sig in args[1:]:
            G.add_edge(producer_gate, gate_name)
    if sig in primary_outputs:
        G.add_edge(producer_gate, sig)

# Draw graph with edge labels
color_map = []
for node, attr in G.nodes(data=True):
    if attr['type'] == 'input':
        color_map.append('green')
    elif attr['type'] == 'output':
        color_map.append('red')
    else:
        color_map.append('skyblue')

# Edge labels
edge_labels = {}
for sig, producer_gate in signal_to_gate.items():
    for gate_type, gate_name, args_str in gate_lines:
        args = [arg.strip() for arg in args_str.split(",") if arg.strip() not in ignore_signals]
        if sig in args[1:]:
            edge_labels[(producer_gate, gate_name)] = sig
    if sig in primary_outputs:
        edge_labels[(producer_gate, sig)] = sig

for inp in primary_inputs:
    for gate_type, gate_name, args_str in gate_lines:
        args = [arg.strip() for arg in args_str.split(",") if arg.strip() not in ignore_signals]
        if inp in args[1:]:
            edge_labels[(inp, gate_name)] = inp

# Draw
plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=1500, font_size=10, arrows=True)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
plt.title("Verilog Circuit Graph with Edge Labels")
plt.show()


gates = [node for node, attr in G.nodes(data=True) if attr["type"] == "gate"]

# Organize data
graph_structure = {
    "primary_inputs": sorted(list(primary_inputs)),
    "primary_outputs": sorted(list(primary_outputs)),
    "gates": sorted(gates),
    "edges": []
}

# Add edges with signal names
for (src, dst), label in edge_labels.items():
    graph_structure["edges"].append({
        "source": src,
        "target": dst,
        "signal": label
    })

# Save to new JSON file
structured_json_path = "netlist_graph.json"
with open(structured_json_path, "w") as f:
    json.dump(graph_structure, f, indent=4)


# Add node i