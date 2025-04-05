import json
from collections import defaultdict


with open("../Parsing/netlist_graph.json", "r") as f:
    data = json.load(f)

gates = data["gates"]
edges = data["edges"]


nets = defaultdict(list)

# Populate the nets
#for edge in edges:
   # start, end = edge
   # nets[start].append(end)

# Convert to regular dict if needed
#nets = dict(nets)


#print(gates)
print(edges)
