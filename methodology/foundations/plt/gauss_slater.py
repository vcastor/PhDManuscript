#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

def normalize_radial(r, psi):
    # Numerical normalization for radial functions
    # Integral = ∫ |ψ(r)|^2 * 4π r^2 dr
    dr = r[1] - r[0]
    integral = np.sum((psi**2) * 4 * np.pi * r**2) * dr
    return psi / np.sqrt(integral)

# Radial distribution
def radial_distribution(r, psi):
    # return (psi**2)*4*np.pi*r**2
    return 4.0*np.pi*r**2*np.abs(psi)**2

# Slater-type orbital
def slater_1s(r, zeta=1.0):
    N = np.sqrt(zeta**3/np.pi)
    return N * np.exp(-zeta * r)

# GTO primitive
def gto_1s(r, alpha):
    norm = (2*alpha/np.pi)**0.75
    return norm * np.exp(-alpha * r**2)

# Define the radial grid
r = np.linspace(0, 8, 400)

# STO-1G 
alpha_sto1 = [0.270950]
c_sto1 = [1.0]
psi_sto1 = sum(c * gto_1s(r, a) for c, a in zip(c_sto1, alpha_sto1))

# STO-2G 
alpha_sto2 = [0.151623, 0.851819]
c_sto2 = [0.678914, 0.430129]
psi_sto2 = sum(c * gto_1s(r, a) for c, a in zip(c_sto2, alpha_sto2))

# STO-3G
alpha_sto3 = [2.22766, 0.405771, 0.109818]
c_sto3 = [0.154329, 0.535328, 0.444635]
psi_sto3 = sum(c * gto_1s(r, a) for c, a in zip(c_sto3, alpha_sto3))

# 6-31G (from your input)
alpha_631g = [18.73113696, 2.825394365, 0.6401216923]
c_631g     = [0.03349460434, 0.2347269535, 0.8137573261]
alpha_631g_single = [0.1612777588]
c_631g_single     = [1.0]
psi_631g_core = sum(c * gto_1s(r, a) for c, a in zip(c_631g, alpha_631g))
psi_631g_val  = sum(c * gto_1s(r, a) for c, a in zip(c_631g_single, alpha_631g_single))
psi_631g = psi_631g_core + psi_631g_val

# Slater
psi_slater = slater_1s(r, zeta=1.0)

# Normalize the wavefunctions
psi_sto1 = normalize_radial(r, psi_sto1)
psi_sto2 = normalize_radial(r, psi_sto2)
psi_sto3 = normalize_radial(r, psi_sto3)
psi_631g = normalize_radial(r, psi_631g)
psi_slater = normalize_radial(r, psi_slater)

# Plot the wavefunctions
plt.figure(figsize=(8,5))
plt.xlim(0, 4)
plt.plot(r, psi_slater, label="Slater 1s", lw=2)
plt.plot(r, psi_sto1, ':', label="STO-1G", lw=2)
plt.plot(r, psi_sto2, ':', label="STO-2G", lw=2)
plt.plot(r, psi_sto3, ':', label="STO-3G", lw=2)
plt.plot(r, psi_631g, '-.', label="6-31G", lw=2)
plt.xlabel("r (Bohr)", fontsize=16)
plt.ylabel("ψ(r)", fontsize=16)
plt.title("STO vs GTOs (1s Orbital)", fontsize=18)
plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig("gauss_slater_wavef.pdf")

# Plot radial distribution
plt.figure(figsize=(8,5))
plt.xlim(0, 6)
plt.plot(r, radial_distribution(r, psi_slater), label="Slater 1s", lw=2)
plt.plot(r, radial_distribution(r, psi_sto1), ':', label="STO-1G", lw=2)
plt.plot(r, radial_distribution(r, psi_sto2), ':', label="STO-2G", lw=2)
plt.plot(r, radial_distribution(r, psi_sto3), ':', label="STO-3G", lw=2)
plt.plot(r, radial_distribution(r, psi_631g), '-.', label="6-31G", lw=2)
plt.xlabel("r (Bohr)", fontsize=16)
plt.ylabel("4πr²|ψ(r)|²", fontsize=16)
plt.title("Radial Distribution Functions", fontsize=18)
plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig("gauss_slater_radial.pdf")

