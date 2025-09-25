#!/usr/bin/python3
import math
import numpy as np
import matplotlib.pyplot as plt

def compute_maxCP(natoms):
    """Theoretical maximum CP"""
    return natoms*(natoms-1) + natoms*(natoms-3)/2 + 6*natoms - 23

def castor_implementation(x):
    """Square root with exponential decay"""
    return 50*np.sqrt(x)*(1 - np.exp(-x/50))

def rodrigez_implementation(x):
    return 256*x

# Precompute anchor values for continuity
f1_at_59 = 59*(59-1)/2 + 59/2 + 59/3
f2_at_136 = f1_at_59 + 500*math.erf((136 - 59)/50)

def compute_maxCP_smooth(natoms, k1=0.1, D3=50, C=50, D=5):
    """Smooth version of compute_maxCP with blended transitions"""
    # Stage curves
    f1 = natoms*(natoms-1)/2 + natoms/2 + natoms/3
    f2 = f1_at_59 + 500*math.erf((natoms - 59)/50)
    f3 = f2_at_136 + C*math.log1p(max(natoms - 136, 0)/D)

    # First transition: logistic around 59
    w1 = 1.0/(1.0 + math.exp(-k1*(natoms - 59)))
    mid = (1 - w1)*f1 + w1*f2

    # Second transition: arcsin-based smoothstep in [136, 136+D3]
    x = natoms - 136
    if x <= 0:
        w2 = 0.0
    elif x >= D3:
        w2 = 1.0
    else:
        u = 2*x/D3 - 1
        w2 = (math.asin(u) + math.pi/2) / math.pi

    return int((1 - w2)*mid + w2*f3)

def modified_sqrt_function(x):
    """Modified square root function"""
    return 5*np.sqrt(100*x)*(1 - np.exp(-x))

def create_plot(use_log_scale=False):
    """Create the growth functions comparison plot"""
    # Generate input values
    x_vals = np.linspace(1, 600, 600)
    
    # Calculate function values [in MB]
    theoretical = [26*compute_maxCP(x)/1024 for x in x_vals]
    smooth_vals = [26*compute_maxCP_smooth(x)/1024 for x in x_vals]
    castor_vals = [26*castor_implementation(x)/1024 for x in x_vals]
    mod_sqrt_vals = [26*int(modified_sqrt_function(x))/1024 for x in x_vals]
    rodriguez_vals = [27*rodrigez_implementation(x)/1024 for x in x_vals]

    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot all functions
    plt.plot(x_vals, theoretical, 'b-', linewidth=2, label='Limit of maxCP')
    plt.plot(x_vals, castor_vals, 'g-', linewidth=2, label='Current Implementation')
    plt.plot(x_vals, rodriguez_vals, 'c-', linewidth=2, label='Original Implementation')
    plt.plot(x_vals, smooth_vals, 'r-', linewidth=2, label='Function defined by parts')
    plt.plot(x_vals, mod_sqrt_vals, 'm-', linewidth=2, label='√n function with exponential decay')
    
    # Set scale
    plt.yscale('log')
    plt.ylabel("maxCP in MB (log scale)", fontsize=18, fontweight='bold')
    plt.title("Allocation memory comparison (Log Scale)", fontsize=20, fontweight='bold')
    
    plt.xlabel("number of atoms", fontsize=18, fontweight='bold')
    plt.xlim(-10, 600)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='lower right', frameon=True, fancybox=True, shadow=True,
           fontsize=18, framealpha=0.9)
    
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.tight_layout()
    return plt

# Main execution
if __name__ == "__main__":
    # Create log scale plot
    plot2 = create_plot(use_log_scale=True)
    plt.savefig('memory_optimisation_curve.pdf')

