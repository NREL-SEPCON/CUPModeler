from numba import jit, prange
import numpy as np


@jit(nopython=True, parallel=True)
def CUP_MDMDM(Sf, KD, Vc, Xcup, Ycup, Tstep):
    """
    Dual mode CCC by reversing the stationary phase while keeping the mobile phase.
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
    Cout - Effluent history (concentration at the outlet)
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

    Cout = np.zeros((comp, Tstep))  # Initialize effluent history

    # Process each component in parallel
    for j in prange(comp):
        # Initial condition at t = 0
        X[Ncup - 1, 0, j] = kA[j] * Xcup[Ncup - 1, el_time - 1, j]
        Y[Ncup - 1, 0, j] = KD[j] * X[Ncup - 1, 0, j]

        # Calculate for the first time step
        for i in range(Ncup - 1, 0, -1):
            X[i - 1, 0, j] = kA[j] * (Xcup[i - 1, el_time - 1, j] + P * Ycup[i, el_time - 1, j])
            Y[i - 1, 0, j] = KD[j] * X[i - 1, 0, j]

        # Calculate solute movement for t = 1 to Tstep-1
        for t in range(1, Tstep):
            # Boundary condition for the last cell
            X[Ncup - 1, t, j] = kA[j] * X[Ncup - 1, t - 1, j]
            Y[Ncup - 1, t, j] = KD[j] * X[Ncup - 1, t, j]

            # Column calculation - SP moving from [Ncup-1] to the first cell
            for i in range(Ncup - 1, 0, -1):
                X[i - 1, t, j] = kA[j] * (X[i - 1, t - 1, j] + P * Y[i, t - 1, j])
                Y[i - 1, t, j] = KD[j] * X[i - 1, t, j]

        # Effluent history (concentration at the outlet)
        for t in range(Tstep):
            Cout[j, t] = Y[0, t, j]

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
        Vspan[t] = Vscup * (t + 1)

    return Vspan, Cout, Xtot, Ytot
