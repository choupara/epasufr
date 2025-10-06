import matplotlib.pyplot as plt
import numpy as np

# Data
instances = np.arange(1, 11)
as_values = [264, 380, 392, 528, 1640, 1920, 2828, 4616, 7088, 7152]
projected_atoms = [11, 18, 13, 11, 19, 25, 26, 25, 25, 26]
time_clingo = [0.01, 0.01, 0.01, 0.01, 0.03, 0.03, 0.04, 0.07, 0.11, 0.12]
time_facets = [1.7, 2.51, 2.53, 3.51, 11.93, 10.25, 21.13, 33.72, 47.29, 52.17]

# Figure 1: Execution Time Comparison
fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(as_values, time_clingo, 'o-', color='#3b82f6', linewidth=2, 
         markersize=8, label='Time Clingo')
ax1.plot(as_values, time_facets, 's-', color='#ef4444', linewidth=2, 
         markersize=8, label='Time Facets Count')
ax1.set_xlabel('#AS', fontsize=12, fontweight='bold')
ax1.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
ax1.set_title('Execution Time Comparison', fontsize=14, fontweight='bold')
ax1.legend(loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('execution_time_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# Figure 2: AS vs Projected Atoms (Bar Chart)
fig2, ax2 = plt.subplots(figsize=(10, 6))
x = np.arange(len(instances))
width = 0.35
bars1 = ax2.bar(x - width/2, as_values, width, label='#AS', color='#8b5cf6')
bars2 = ax2.bar(x + width/2, projected_atoms, width, label='Projected Atoms', color='#10b981')
ax2.set_xlabel('Instance', fontsize=12, fontweight='bold')
ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
ax2.set_title('#AS vs Projected Atoms', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(instances)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig('as_vs_projected_atoms.png', dpi=300, bbox_inches='tight')
plt.show()

# Figure 3: Facets Count Time vs #AS
fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.plot(as_values, time_facets, 'o-', color='#f59e0b', linewidth=2.5, 
         markersize=8, label='Time Facets Count')
ax3.set_xlabel('#AS', fontsize=12, fontweight='bold')
ax3.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
ax3.set_title('Facets Count Time vs #AS', fontsize=14, fontweight='bold')
ax3.legend(fontsize=11)
ax3.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('facets_time_vs_as.png', dpi=300, bbox_inches='tight')
plt.show()

# Additional individual high-resolution plots

# Figure 4: Time comparison with dual y-axis
fig4, ax_main = plt.subplots(figsize=(10, 6))
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
plt.savefig('time_comparison_dual_axis.png', dpi=300, bbox_inches='tight')
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
plt.savefig('facets_scaling_analysis.png', dpi=300, bbox_inches='tight')
plt.show()