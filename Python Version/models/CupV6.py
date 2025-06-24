from numba import jit, prange
import numpy as np

@jit(nopython=True, parallel=True)
def CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj):
    """
    JIT-compiled version with parallel processing - Complete implementation
    Expected speedup: 10-50x for large problems

    Parameters:
    Sf: Stationary factor (volume ratio of [V_SP]/[V_MP])
    KD: Distribution coefficient ([Conc_SP]eq/[Conc_MP]eq)
    Vc: Total column volume
    Ncup: Number of cups
    Vcm: Elution volume to stop Classic elution
    C0: Injection concentration (array for multiple components)
    Vinj: Injection volume

    Returns:
    Vspan: Volume span
    Cout: Outlet concentration
    X: MP concentration profiles in cells
    Y: SP concentration profiles in cells
    """
    n = len(KD)
    P = Sf / (1 - Sf)  # Phase ratio

    # Retention factor
    kA = 1 / (1 + P * KD)
    vmcup = Vc / Ncup * (1 - Sf)
    Ninj = Vinj / vmcup  # Number of cells filled by injection
    Tau = int(round(Vcm / vmcup))

    # Initialize matrices
    X = np.zeros((Ncup, Tau, n))  # Mobile phase concentration matrix
    Y = np.zeros((Ncup, Tau, n))  # Stationary phase concentration matrix
    Cinj = np.zeros((1, Tau, n))  # Injection concentration

    Cout = np.zeros((n, Tau))  # Outlet concentration

    # Process each component in parallel
    for j in prange(n):
        # Set injection concentration
        Ninj_int = int(Ninj)
        for t in range(min(Ninj_int, Tau)):
            Cinj[0, t, j] = C0[j]

        # Add tail concentration for mass balance correction
        Ninj_cup = int(np.floor(Ninj))
        if Ninj_cup < Tau:
            Massin = Ninj_cup * vmcup * C0[j]
            diff = (Vinj * C0[j] - Massin) / (Vinj * C0[j]) if Vinj * C0[j] > 0 else 0

            if diff >= 0.02:
                Vtruncate = vmcup * (Ninj - Ninj_cup)
                Ctail = C0[j] * Vtruncate / vmcup
                Cinj[0, Ninj_cup, j] = Ctail

        # Initial boundary conditions
        X[0, 0, j] = kA[j] * Cinj[0, 0, j]
        Y[0, 0, j] = KD[j] * X[0, 0, j]

        # Mass balance calculation - time loop
        for t in range(1, Tau):
            # First cup (boundary condition)
            X[0, t, j] = kA[j] * Cinj[0, t, j] + kA[j] * P * Y[0, t - 1, j]
            Y[0, t, j] = KD[j] * X[0, t, j]

            # Remaining cups - vectorized spatial operations
            for i in range(1, Ncup):
                X[i, t, j] = kA[j] * (X[i - 1, t - 1, j] + P * Y[i, t - 1, j])
                Y[i, t, j] = KD[j] * X[i, t, j]

        # Outlet concentration
        for t in range(Tau):
            Cout[j, t] = X[Ncup - 1, t, j]

    # Volume span
    Vspan = np.zeros(Tau)
    for t in range(Tau):
        Vspan[t] = vmcup * t

    return Vspan, Cout, X, Y, vmcup
