import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


grid_size = (8, 10)     # (X, Y)
agent_position = (1, 1) # position of the circle
wall_positions = [(1, 1 + 0.5)]

# Create a grid of zeros
grid = np.zeros((grid_size[1], grid_size[0]))

# Plot the grid with a circular patch and a rectangle patch
fig, ax = plt.subplots()
im = ax.imshow(grid, cmap='binary', interpolation='nearest', origin='lower', extent=[-0.55, grid_size[0]-1+0.55, -0.55, grid_size[1]-1+0.55], aspect='equal', vmin=0, vmax=1)

# Plot agent.
circle = plt.Circle(xy=agent_position, radius=0.25, color='red', fill=True, linewidth=2)
ax.add_patch(circle)
ax.text(*agent_position, 'A', fontsize=12, color='white', ha='center', va='center')

# Plot walls.
wall_thickness = 0.25
for wall in wall_positions:
    if wall[0]//1 != wall[0]:
        wall_bottom_left = (wall[0] - wall_thickness/2, wall[1] - 0.5)
        rect = Rectangle(xy=wall_bottom_left, width=wall_thickness, height=1, linewidth=2, edgecolor='blue', facecolor='blue')
    elif wall[1]//1 != wall[1]:
        wall_bottom_left = (wall[0] - 0.5, wall[1] - wall_thickness/2)
        rect = Rectangle(xy=wall_bottom_left, width=1, height=wall_thickness, linewidth=2, edgecolor='blue', facecolor='blue')
    else:
        raise Exception(f"Wall = {wall}.")
    ax.add_patch(rect)

ax.set_xticks(np.arange(grid_size[0]))
ax.set_yticks(np.arange(grid_size[1]))
plt.grid(color='black', linewidth=1, linestyle='dotted')

# Remove the axes lines
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.show()
