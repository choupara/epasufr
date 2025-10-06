import matplotlib.pyplot as plt
import numpy as np

# Data
instances = np.arange(1, 11)
as_values = [264, 380, 392, 528, 1640, 1920, 2828, 4616, 7088, 7152]
projected_atoms = [11, 18, 13, 11, 19, 25, 26, 25, 25, 26]
time_clingo = [0.01, 0.01, 0.01, 0.01, 0.03, 0.03, 0.04, 0.07, 0.11, 0.12]
time_facets = [1.7, 2.51, 2.53, 3.51, 11.93, 10.25, 21.13, 33.72, 47.29, 52.17]

# Create figure with subplots
fig = plt.figure(figsize=(14, 10))

# Plot 1: Execution Time Comparison
ax1 = plt.subplot(2, 2, 1)
ax1.plot(as_values, time_clingo, 'o-', color='#3b82f6', linewidth=2, 
         markersize=6, label='Time Clingo')
ax1.plot(as_values, time_facets, 's-', color='#ef4444', linewidth=2, 
         markersize=6, label='Time Facets Count')
ax1.set_xlabel('#AS', fontsize=11, fontweight='bold')
ax1.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
ax1.set_title('Execution Time Comparison', fontsize=12, fontweight='bold')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3, linestyle='--')

# Plot 2: AS vs Projected Atoms (Bar Chart)
ax2 = plt.subplot(2, 2, 2)
x = np.arange(len(instances))
width = 0.35
bars1 = ax2.bar(x - width/2, as_values, width, label='#AS', color='#8b5cf6')
bars2 = ax2.bar(x + width/2, projected_atoms, width, label='Projected Atoms', color='#10b981')
ax2.set_xlabel('Instance', fontsize=11, fontweight='bold')
ax2.set_ylabel('Count', fontsize=11, fontweight='bold')
ax2.set_title('#AS vs Projected Atoms', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(instances)
ax2.legend()
ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

# Plot 3: Facets Count Time vs #AS
ax3 = plt.subplot(2, 2, 3)
ax3.plot(as_values, time_facets, 'o-', color='#f59e0b', linewidth=2.5, 
         markersize=7, label='Time Facets Count')
ax3.set_xlabel('#AS', fontsize=11, fontweight='bold')
ax3.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
ax3.set_title('Facets Count Time vs #AS', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3, linestyle='--')

# Plot 4: Summary Statistics (Text Box)
ax4 = plt.subplot(2, 2, 4)
ax4.axis('off')
summary_text = f"""
Summary Statistics

Max #AS: {max(as_values)}
Max Projected Atoms: {max(projected_atoms)}
Max Clingo Time: {max(time_clingo)}s
Max Facets Time: {max(time_facets)}s

Min #AS: {min(as_values)}
Min Projected Atoms: {min(projected_atoms)}
Min Clingo Time: {min(time_clingo)}s
Min Facets Time: {min(time_facets)}s

Avg Clingo Time: {np.mean(time_clingo):.3f}s
Avg Facets Time: {np.mean(time_facets):.2f}s
"""
ax4.text(0.1, 0.5, summary_text, fontsize=11, verticalalignment='center',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
ax4.set_title('Summary Statistics', fontsize=12, fontweight='bold')

plt.suptitle('AF_ST Expanded Performance Analysis', fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.show()

# Optional: Create individual high-resolution plots

# Individual Plot 1: Time comparison with dual y-axis
fig2, ax_main = plt.subplots(figsize=(10, 6))
ax_twin = ax_main.twinx()

line1 = ax_main.plot(as_values, time_clingo, 'o-', color='#3b82f6', 
                     linewidth=2, markersize=8, label='Time Clingo')
line2 = ax_twin.plot(as_values, time_facets, 's-', color='#ef4444', 
                     linewidth=2, markersize=8, label='Time Facets Count')

ax_main.set_xlabel('#AS', fontsize=12, fontweight='bold')
ax_main.set_ylabel('Time Clingo (seconds)', fontsize=12, fontweight='bold', color='#3b82f6')
ax_twin.set_ylabel('Time Facets Count (seconds)', fontsize=12, fontweight='bold', color='#ef4444')
ax_main.set_title('Execution Time Comparison (Dual Y-Axis)', fontsize=14, fontweight='bold')

ax_main.tick_params(axis='y', labelcolor='#3b82f6')
ax_twin.tick_params(axis='y', labelcolor='#ef4444')
ax_main.grid(True, alpha=0.3, linestyle='--')

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax_main.legend(lines, labels, loc='upper left')

plt.tight_layout()
plt.show()

# Individual Plot 2: Scatter plot with trend line
fig3, ax = plt.subplots(figsize=(10, 6))
ax.scatter(as_values, time_facets, s=100, color='#f59e0b', 
           alpha=0.6, edgecolors='black', linewidth=1.5, label='Data Points')

# Fit polynomial trend line
z = np.polyfit(as_values, time_facets, 2)
p = np.poly1d(z)
x_trend = np.linspace(min(as_values), max(as_values), 100)
ax.plot(x_trend, p(x_trend), '--', color='#dc2626', linewidth=2, label='Trend Line')

ax.set_xlabel('#AS', fontsize=12, fontweight='bold')
ax.set_ylabel('Time Facets Count (seconds)', fontsize=12, fontweight='bold')
ax.set_title('Facets Count Time Scaling Analysis', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.show()
