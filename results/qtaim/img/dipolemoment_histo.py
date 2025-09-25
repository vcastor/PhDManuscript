#!/usr/bin/python3
import sqlite3
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from collections import defaultdict

# Common style configuration
def setup_plot_style():
    sns.set_style("whitegrid")
    plt.rcParams.update({'font.size': 14})

# Connect to the SQLite database
conn = sqlite3.connect("q_dp_pol.db")
cursor = conn.cursor()

# Get all systems and their number of atoms
cursor.execute("SELECT system, natoms FROM systems WHERE normal_termination = 7 AND aimall = 1")
systems = cursor.fetchall()

# Collect charge differences grouped by element
diffs_tot, diffs_intra, diffs_inter = [], [], []

count_tot_systems = 0
for system, natoms in systems:
    query = f"""SELECT mu_adf_norm, mu_aimall_norm,
                mu_adf_intra_norm, mu_aimall_intra_norm,
                mu_adf_inter_norm, mu_aimall_inter_norm,
                symbol FROM '{system}'"""
    cursor.execute(query)
    rows = cursor.fetchall()

    # Check if there NoneType values in the results
    if any(row is None for row in rows):
        continue

    count_tot_systems += 1 # only the successfull systems
    for mu_adf, mu_aimall, mu_adf_intra, mu_aimall_intra, mu_adf_inter, mu_aimall_inter, symbol in rows:
        if any(x is None for x in [mu_adf, mu_aimall]):
            continue
        diff_tot = mu_adf - mu_aimall
        diffs_tot.append(diff_tot)
        diff_intra = mu_adf_intra - mu_aimall_intra
        diffs_intra.append(diff_intra)
        diff_inter = mu_adf_inter - mu_aimall_inter
        diffs_inter.append(diff_inter)

print(count_tot_systems)
conn.close()

# Convert to numpy arrays for easier handling
diffs_tot = np.array(diffs_tot)
diffs_intra = np.array(diffs_intra)
diffs_inter = np.array(diffs_inter)

# Print statistics
print("=== DIPOLE MOMENT DIFFERENCES STATISTICS ===")
print(f"Total differences - Mean: {np.mean(diffs_tot):.4f}, Std: {np.std(diffs_tot):.4f}, Median: {np.median(diffs_tot):.4f}")
print(f"Intra differences - Mean: {np.mean(diffs_intra):.4f}, Std: {np.std(diffs_intra):.4f}, Median: {np.median(diffs_intra):.4f}")
print(f"Inter differences - Mean: {np.mean(diffs_inter):.4f}, Std: {np.std(diffs_inter):.4f}, Median: {np.median(diffs_inter):.4f}")
print(f"Total data points: {len(diffs_tot)}")

# Set up the plotting style
setup_plot_style()
plt.figure(figsize=(12, 8))

# Define colors (improved palette)
colours = ['#2E86AB', '#A23B72', '#F18F01']  # Blue, Purple, Orange ! COULOUR !
labels  = ['Total', 'Intra-atomic', 'Inter-atomic']

# Plot histograms with transparency and higher resolution
bins = np.linspace(-0.15, 0.15, 120)  # More bins for smoother curves
kde_params = {'bw_adjust': 1.2, 'bw_method': 'silverman'}  # Slightly smoother KDE

sns.histplot(diffs_tot, kde=False, stat="count", alpha=0.4,
             color=colours[0], label=labels[0], bins=bins,
             kde_kws=kde_params)
sns.histplot(diffs_intra, kde=False, stat="count", alpha=0.4,
             color=colours[1], label=labels[1], bins=bins,
             kde_kws=kde_params)
sns.histplot(diffs_inter, kde=False, stat="count", alpha=0.4,
             color=colours[2], label=labels[2], bins=bins,
             kde_kws=kde_params)

# Customize the plot
plt.xlabel("Dipole Moment Difference (ADF - AIMAll) (a.u.)", fontsize=16, fontweight='bold')
plt.ylabel("Count (×10³)", fontsize=16, fontweight='bold')
plt.title("Distribution of Atomic Dipole Moment Differences",
          fontsize=18, fontweight='bold', pad=20)

# Set axis limits and formatting
plt.xlim(-0.15, 0.15)
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x*1e-3:.0f}'))

# Add enhanced legend with highlighted rectangle
plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, 
           fontsize=14, framealpha=0.9)

# Add grid customization
plt.grid(True, alpha=0.3)

# Adjust layout and save
plt.tight_layout()
plt.savefig("histogram_dipole_total.pdf", dpi=300, bbox_inches='tight')

