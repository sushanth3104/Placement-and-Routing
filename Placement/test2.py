import json
import math
from collections import defaultdict
import json
import random
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


# For plotting

def SimulatedAnnealingPlacement(Net, Gate, initial_temp=100.0, final_temp=0.1, alpha=0.995, max_iters=10000):
    T = initial_temp
    L1 = sum(net.HPWL for net in Net.instances)
    tracking_progress = [L1]

    for i in range(max_iters):
    # Randomly select two gates
        gate1, gate2 = random.sample(Gate.instances, 2)

    # Swap positions
        gate1.position, gate2.position = gate2.position, gate1.position

    # Recalculate HPWL for affected nets
        affected_nets = [net for net in Net.instances if gate1 in net.gates or gate2 in net.gates]
        for net in affected_nets:
            net.update_hpwl()

    # Compute new cost
        L2 = sum(net.HPWL for net in Net.instances)
        delta = L2 - L1

    # Decide whether to accept
        if delta < 0 or random.random() < math.exp(-delta / T):
        # Accept move
            L1 = L2
            tracking_progress.append(L1)
        else:
        # Revert swap
            gate1.position, gate2.position = gate2.position, gate1.position
            for net in affected_nets:
                net.update_hpwl()

    # Cool down temperature
        T *= alpha

    # Optional early stop
        if T < final_temp:
            break

# Plot cost trend
    plt.figure(figsize=(10, 4))
    plt.stem(range(len(tracking_progress)), tracking_progress, basefmt=" ")
    plt.title("Simulated Annealing - HPWL Progress")
    plt.xlabel("Iteration")
    plt.ylabel("Total HPWL")
    plt.grid(True)
    plt.tight_layout()
    plt.show()






def plot_circuit_grid(grid_size, PrimaryInput, PrimaryOutput, Gate):
    """
    Visualizes the digital circuit layout on a grid using seaborn heatmap.

    Parameters:
    - grid_size (int): Size of the grid (NxN)
    - PrimaryInput (class): PrimaryInput class with `instances` list
    - PrimaryOutput (class): PrimaryOutput class with `instances` list
    - Gate (class): Gate class with `instances` list
    """

    # Initialize grid data and color matrix
    grid_data = np.full((grid_size, grid_size), "", dtype=object)
    colors = np.zeros((grid_size, grid_size))  # Default color code: 0 (background)

    # Primary Inputs
    for pi in PrimaryInput.instances:
        row, col = pi.position
        grid_data[row][col] = pi.name
        colors[row][col] = 1  # Teal Green

    # Primary Outputs
    for po in PrimaryOutput.instances:
        row, col = po.position
        grid_data[row][col] = po.name
        colors[row][col] = 2  # Blue

    # Gates
    for gate in Gate.instances:
        row, col = gate.position
        grid_data[row][col] = gate.name
        colors[row][col] = 3  # Orange

    # Highlight unused inner grid cells
    for i in range(1, grid_size - 1):
        for j in range(1, grid_size - 1):
            if colors[i][j] == 0:
                colors[i][j] = 4  # Light blue highlight

    # Define a custom colormap
    custom_cmap = ListedColormap([
        "#eeeeee",  # 0: Background
        "#66C2A5",  # 1: Primary Inputs
        "#8DA0CB",  # 2: Primary Outputs
        "#FC8D62",  # 3: Gates
        "#81d4fa"   # 4: Inner Grid Highlight
    ])

    # Plotting
    plt.figure(figsize=(10, 10))
    sns.heatmap(
        colors,
        cbar=False,
        annot=grid_data,
        fmt="",
        annot_kws={"size": 9, "weight": "bold", "color": "black"},
        linewidths=1.5,
        linecolor='white',
        square=True,
        cmap=custom_cmap
    )

    plt.xticks([])
    plt.yticks([])
    plt.title(f"{grid_size}x{grid_size} Placement Grid", fontsize=18, weight='bold', pad=20)
    plt.tight_layout()
    plt.show()






# Load the JSON data
with open("../Parsing/netlist_graph.json") as f:  # adjust path as needed
    circuit_data = json.load(f)

# Define Gate and Net classes
class Gate:
    instances = []
    def __init__(self, name):
        self.name = name
        self.inputs = []     # list of input signal names
        self.output = None   # single output signal name
        self.position = None # to be used later for layout
        Gate.instances.append(self) 

    def __repr__(self):
        return f"Gate(name={self.name}, inputs={self.inputs}, output={self.output}, position={self.position})"

class Net:
    instances = []
    def __init__(self, name):
        self.name = name
        self.primary_input_or_output = False  
        self.gates = set()  # gates connected to this signal
        self.HPWL = 0
        Net.instances.append(self)

    def update_hpwl(self):
        x = []
        y = []

        for gate in self.gates:
            x.append(gate.position[0])
            y.append(gate.position[1])

        self.HPWL = max(x) - min(x) + max(y) - min(y)

       


    

    def __repr__(self):
        return f"Net(name={self.name}, Primary in/op ={self.primary_input_or_output}, gates={list(self.gates)})"
    
class PrimaryInput:
    instances = []
    def __init__(self, name):
        self.name = name
        self.position = None # to be used later for layout
        self.Net = None
        PrimaryInput.instances.append(self)

    def __repr__(self):
        return f"PrimaryInput(name={self.name}, position={self.position})"
    
class PrimaryOutput:
    instances = []
    def __init__(self, name):
        self.name = name
        self.position = None # to be used later for layout
        self.Net = None
        PrimaryOutput.instances.append(self)

    def __repr__(self):
        return f"PrimaryOutput(name={self.name}, position={self.position})"
    

N = 2*len(circuit_data["gates"])
grid_size = N + 2  # Includes columns for inputs and outputs





# For PI : 
pi_positions = random.sample(range(1, grid_size-1), len(circuit_data["primary_inputs"]))


for i, PI in enumerate(circuit_data["primary_inputs"]):
    pi_obj = PrimaryInput(PI)
    pi_obj.position = [pi_positions[i],0]  # Column 0, random row
    pi_obj.Net = PI

# For PO :
po_positions = random.sample(range(1, grid_size-1), len(circuit_data["primary_outputs"]))

for i, PO in enumerate(circuit_data["primary_outputs"]):
    po_obj = PrimaryOutput(PO)
    po_obj.position = [po_positions[i],grid_size-1]  # Column N+1, random row
    po_obj.Net = PO

valid_positions = [[i, j] for i in range(1, grid_size - 1) for j in range(1, grid_size - 1)]
random.shuffle(valid_positions)


for i,gate in enumerate(circuit_data["gates"]):
    gate_obj = Gate(gate)
    gate_obj.output = set([edge["signal"] for edge in circuit_data["edges"] if edge["source"] == gate])
    gate_obj.inputs = set([edge["signal"] for edge in circuit_data["edges"] if edge["target"] == gate])
    gate_obj.position = valid_positions[i]  # Random position in the inner grid     



nets = circuit_data["primary_inputs"] + circuit_data["primary_outputs"] + [edge["signal"] for edge in circuit_data["edges"]]
nets = set(nets)

L = 0 # Total HPWL 

for net in nets:
    net_obj = Net(net)
    net_obj.gates = set([gate for gate in Gate.instances if net in gate.inputs or net in gate.output])

    ## Treat Primary input and Primary Output as Dummy Gates ad add them to the list as connected gates
        
    if net in circuit_data["primary_inputs"]:
        for pi in PrimaryInput.instances:
            if pi.name == net_obj.name:
                net_obj.gates.add(pi)
        net_obj.primary_input_or_output = True

    if net in circuit_data["primary_outputs"]:
        for po in PrimaryOutput.instances:
            if po.name == net_obj.name:
                net_obj.gates.add(po)
        net_obj.primary_input_or_output = True

    net_obj.update_hpwl()

    



# For Random Iterative Improvement : Only Pure gates are allowed to move
plot_circuit_grid(grid_size, PrimaryInput, PrimaryOutput, Gate)

Total_HPWL = 0
for net in Net.instances:
    Total_HPWL += net.HPWL

print("Total Initial HPWL:", Total_HPWL)

for net in Net.instances:
   for gate in net.gates:
        print(f"Net: {net.name}, Gate: {gate.name}, Position: {gate.position}")
   print(net.HPWL)


SimulatedAnnealingPlacement(Net,Gate)

Total_HPWL = 0
for net in Net.instances:
    Total_HPWL += net.HPWL

print("Total HPWL after Random Improvement:", Total_HPWL)


plot_circuit_grid(grid_size, PrimaryInput, PrimaryOutput, Gate)


#for net in Net.instances:
#  for gate in net.gates:
#       print(f"Net: {net.name}, Gate: {gate.name}, Position: {gate.position}")
#  print(net.HPWL)






