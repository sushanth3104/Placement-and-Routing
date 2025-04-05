import json
import random
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Load the JSON file
with open('../Parsing/netlist_graph.json') as f:  # Use full path if needed
    data = json.load(f)

# Extract circuit components
primary_inputs = data['primary_inputs']
primary_outputs = data['primary_outputs']
gates = data['gates']
n = 2*len(gates)
grid_size = n + 2  # Includes columns for inputs and outputs

# Initialize grid data and color matrix
grid_data = np.full((grid_size, grid_size), "", dtype=object)
colors = np.zeros((grid_size, grid_size))  # Default color code: 0 (background)

# Randomly place primary inputs in column 0
input_rows = random.sample(range(grid_size), len(primary_inputs))
for i, row in enumerate(input_rows):
    grid_data[row][0] = primary_inputs[i]
    colors[row][0] = 1  # Color code for input

# Randomly place primary outputs in column n+1
output_rows = random.sample(range(grid_size), len(primary_outputs))
for i, row in enumerate(output_rows):
    grid_data[row][-1] = primary_outputs[i]
    colors[row][-1] = 2  # Color code for output

# Randomly place gates in the inner grid [1:n, 1:n]
inner_positions = [(i, j) for i in range(1, grid_size - 1) for j in range(1, grid_size - 1)]
random.shuffle(inner_positions)
for i, gate in enumerate(gates):
    row, col = inner_positions[i]
    grid_data[row][col] = gate
    colors[row][col] = 3  # Color code for gates

# Highlight inner grid cells that are empty with light blue (code 4)
for i in range(1, grid_size - 1):
    for j in range(1, grid_size - 1):
        if colors[i][j] == 0:
            colors[i][j] = 4  # Highlight inner region

# Define a custom colormap
custom_cmap = ListedColormap([
    "#eeeeee",  # 0: Background
    "#66C2A5",  # 1: Primary Inputs (Teal Green)
    "#8DA0CB",  # 2: Primary Outputs (Blue)
    "#FC8D62",  # 3: Gates (Coral Orange)
    "#81d4fa"   # 4: Inner Grid Highlight (Light Blue)
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

# Beautify plot
plt.xticks([])
plt.yticks([])
plt.title(f"{grid_size}x{grid_size} Digital Circuit Grid with Inner Highlight", fontsize=18, weight='bold', pad=20)
plt.tight_layout()
plt.show()
