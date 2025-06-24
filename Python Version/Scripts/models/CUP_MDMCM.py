from numba import jit, prange
import numpy as np


@jit(nopython=True, parallel=True)
def CUP_MDMCM(Sf, KD, Vc, Xcup, Ycup, Tstep):
    """
    This function calculates elution histories and concentration profiles for a given column.

    Inputs:
    Sf - Stationary factor (volume ratio of [V_SP]/[V_C])
    KD - Array of distribution coefficients ([Conc_SP]eq/[Conc_MP]eq)
    Vc - Column volume (mL)
    Xcup - MP concentration profiles in cells (Ncup, el_time, comp)
    Ycup - SP concentration profiles in cells (Ncup, el_time, comp)
    Tstep - Number of turnover time (iterations)

    Outputs:
    Vspan - Elution volume span
    Cout - Outlet concentration
    Xtot - Combined MP concentration profiles
    Ytot - Combined SP concentration profiles
    """
    # Extract dimensions from Xcup
    Ncup, el_time, comp = Xcup.shape

    # Initialize concentration arrays
    Y = np.zeros((Ncup, Tstep, comp))  # SP concentration (g/L)
    X = np.zeros((Ncup, Tstep, comp))  # MP concentration

    P = Sf / (1 - Sf)
    Vm = Vc * (1 - Sf)
    Vs = Vc * Sf
    kA = 1.0 / (1 + P * KD)  # Retention factor

    Vcell = Vc / Ncup
    Vmcup = Vm / Ncup
    Vscup = Vs / Ncup

    Cout = np.zeros((comp, Tstep))  # Initialize outlet concentration

    # Process each component in parallel
    for j in prange(comp):
        # Initial condition at t = 0
        X[0, 0, j] = kA[j] * (P * Ycup[0, el_time - 1, j])  # From previous run
        Y[0, 0, j] = KD[j] * X[0, 0, j]

        # Calculate for the first time step
        for i in range(1, Ncup):
            X[i, 0, j] = kA[j] * (Xcup[i - 1, el_time - 1, j] + P * Ycup[i, el_time - 1, j])
            Y[i, 0, j] = KD[j] * X[i, 0, j]

        # Mass balance calculation for subsequent time steps
        for t in range(1, Tstep):
            # Boundary condition for the first cell
            X[0, t, j] = kA[j] * (P * Y[0, t - 1, j])
            Y[0, t, j] = KD[j] * X[0, t, j]

            # Column calculation - MP moving from the first to the last cell
            for i in range(1, Ncup):
                X[i, t, j] = kA[j] * (X[i - 1, t - 1, j] + P * Y[i, t - 1, j])
                Y[i, t, j] = KD[j] * X[i, t, j]

        # Outlet concentration
        for t in range(Tstep):
            Cout[j, t] = X[Ncup - 1, t, j]

    # Combine concentration profiles into Xtot and Ytot
    Xtot = np.zeros((Ncup, el_time + Tstep, comp))
    Ytot = np.zeros((Ncup, el_time + Tstep, comp))

    # Copy original profiles
    for i in range(Ncup):
        for t in range(el_time):
            for j in range(comp):
                Xtot[i, t, j] = Xcup[i, t, j]
                Ytot[i, t, j] = Ycup[i, t, j]

    # Copy new profiles
    for i in range(Ncup):
        for t in range(Tstep):
            for j in range(comp):
                Xtot[i, el_time + t, j] = X[i, t, j]
                Ytot[i, el_time + t, j] = Y[i, t, j]

    # Calculate elution volume span
    Vspan = np.zeros(Tstep)
    for t in range(Tstep):
        Vspan[t] = Vmcup * (t + 1)

    return Vspan, Cout, Xtot, Ytot
