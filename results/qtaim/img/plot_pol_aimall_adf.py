#!/usr/bin/python3
import sqlite3
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Common style configuration
def setup_plot_style():
    sns.set_style("whitegrid")
    plt.rcParams.update({'font.size': 14})

# Connect to the database
conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/polarizability/ML/pol_150.db')
c = conn.cursor()

# Query to know the systems in the database
c.execute('''SELECT system FROM systems''')
systems = c.fetchall()

# Loop for querying the polarisabilities for every system
meanp, lambda1, lambda2, lambda3 = [], [], [], []
for system in systems:
    system = system[0]
    c.execute(f'''SELECT pol_l1_adf, pol_l2_adf, pol_l3_adf, pol_mean_adf,
                         pol_l1_aimall, pol_l2_aimall, pol_l3_aimall, pol_mean_aimall
                  FROM {system}''')
    pols = c.fetchall()
    pols = np.array(pols)
    pols[np.isnan(pols)] = 0
    # Calculate the differences
    if pols.shape[0] > 0:
        diff = pols[:,:4] - pols[:,4:]
        meanp.extend(diff[:,3])
        lambda1.extend(diff[:,0])
        lambda2.extend(diff[:,1])
        lambda3.extend(diff[:,2])

conn.close()

# Convert the lists to NumPy arrays
meanp = np.array(meanp).flatten()
lambda1 = np.array(lambda1).flatten()
lambda2 = np.array(lambda2).flatten()
lambda3 = np.array(lambda3).flatten()

# Print statistics
print("=== POLARIZABILITY DIFFERENCES STATISTICS ===")
print(f"Mean polarisability - Mean: {np.mean(meanp):.4f}, Std: {np.std(meanp):.4f}, Median: {np.median(meanp):.4f}, Count: {len(meanp)}")
print(f"Lambda 1 - Mean: {np.mean(lambda1):.4f}, Std: {np.std(lambda1):.4f}, Median: {np.median(lambda1):.4f}, Count: {len(lambda1)}")
print(f"Lambda 2 - Mean: {np.mean(lambda2):.4f}, Std: {np.std(lambda2):.4f}, Median: {np.median(lambda2):.4f}, Count: {len(lambda2)}")
print(f"Lambda 3 - Mean: {np.mean(lambda3):.4f}, Std: {np.std(lambda3):.4f}, Median: {np.median(lambda3):.4f}, Count: {len(lambda3)}")

# Set up the plotting style
setup_plot_style()

# Create the plot
plt.figure(figsize=(12, 8))

# Define colors (same palette as dipole moments)
colours = ['#2E86AB', '#A23B72', '#F18F01', '#6A994E']  # Blue, Purple, Orange, Green ! COLOUR !
labels = ['Mean', 'λ1', 'λ2', 'λ3']

# Plot histograms with transparency and higher resolution
bins = np.linspace(-5, 5, 100)  # More bins for smoother curves
kde_params = {'bw_adjust': 1.2, 'bw_method': 'silverman'}  # Slightly smoother KDE

sns.histplot(meanp, kde=False, stat="count", alpha=0.4,
             color=colours[0], label=labels[0], bins=bins,
             kde_kws=kde_params)
sns.histplot(lambda1, kde=False, stat="count", alpha=0.4,
             color=colours[1], label=labels[1], bins=bins,
             kde_kws=kde_params)
sns.histplot(lambda2, kde=False, stat="count", alpha=0.4,
             color=colours[2], label=labels[2], bins=bins,
             kde_kws=kde_params)
sns.histplot(lambda3, kde=False, stat="count", alpha=0.4,
             color=colours[3], label=labels[3], bins=bins,
             kde_kws=kde_params)

# Customize the plot
plt.xlabel("Polarisability Difference (ADF - AIMAll) (a.u.)", fontsize=16, fontweight='bold')
plt.ylabel("Count (×10²)", fontsize=16, fontweight='bold')
plt.title("Distribution of Atomic Polarisability Differences",
          fontsize=18, fontweight='bold', pad=20)

# Set axis limits and formatting
plt.xlim(-3.5, 3.5)
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x*1e-2:.0f}'))

# Add enhanced legend with highlighted rectangle
plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True,
           fontsize=14, framealpha=0.9)

# Add grid customization
plt.grid(True, alpha=0.3)

# Adjust layout and save
plt.tight_layout()
plt.savefig("histogram_polarisability.pdf", dpi=300, bbox_inches='tight')

