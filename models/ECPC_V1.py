from numba import jit, prange
import numpy as np


@jit(nopython=True, parallel=True)
def ECPC_V1(KD, Vc, Sf, Xcm, Ycm, extrusion_steps=None):
    """
    Parameters:
    KD: Distribution coefficient ([Conc_SP]eq/[Conc_MP]eq)
    Vc: Total column volume
    Sf: Stationary factor (volume ratio of [V_SP]/[V_MP])
    Xcm: MP profiles from CM (Ncup x el_time x comp)
    Ycm: SP profiles from CM (Ncup x el_time x comp)

    Returns:
    Vspan: Total elution volume
    Cout: Elution volume vs. column outlet concentration
    Xtot: Total MP profiles (CM + ECPC)
    Ytot: Total SP profiles (CM + ECPC)
    V_boundary: CM and extrusion boundary in terms of elution volume
    """
    P = Sf / (1 - Sf)  # Phase ratio
    Vm = Vc * (1 - Sf)  # MP volume
    kA = 1 / (1 + P * KD)  # Retention factor

    Ncup, el_time, comp = Xcm.shape  # Cup profile dimensions
    vmcup = Vm / Ncup
    tCM = el_time

    # VCMspan for previous CM
    VCMspan = np.zeros(tCM)
    for i in range(tCM):
        VCMspan[i] = vmcup * (i + 1)

    if extrusion_steps is not None:
        tspan = int(Ncup + extrusion_steps)
    else:
        tspan = int(np.ceil(Ncup * (1 + Sf) * 1.3))

    Y = np.zeros((Ncup, tspan, comp))  # SP concentration
    X = np.zeros((Ncup, tspan, comp))  # MP concentration

    Vcell = Vc / Ncup

    # Process each component in parallel
    for j in prange(comp):
        # ECPC start - displace one cell at a given timestep by new SP
        Y[0, 0, j] = 0
        X[0, 0, j] = 0

        for i in range(1, Ncup):
            X[i, 0, j] = Xcm[i - 1, el_time - 1, j]
            Y[i, 0, j] = Ycm[i - 1, el_time - 1, j]

        # MP elution ends at Ncup time
        for t in range(1, Ncup):
            for i in range(1, Ncup):
                # One cell is displaced by SP after one turnover
                X[i, t, j] = X[i - 1, t - 1, j]
                Y[i, t, j] = Y[i - 1, t - 1, j]

    # Save outlet concentration
    Cout = np.zeros((comp, el_time + tspan))
    for h in range(comp):
        # CM outlet
        for t in range(el_time):
            Cout[h, t] = Xcm[Ncup - 1, t, h]
        # ECPC outlet
        for t in range(tspan):
            Cout[h, el_time + t] = Sf * Y[Ncup - 1, t, h] + (1 - Sf) * X[Ncup - 1, t, h]

    # Combine concentration profiles into Xtot & Ytot from CM to ECPC
    Xtot = np.zeros((Ncup, el_time + tspan, comp))
    Ytot = np.zeros((Ncup, el_time + tspan, comp))

    # Copy CM profiles
    for i in range(Ncup):
        for t in range(el_time):
            for j in range(comp):
                Xtot[i, t, j] = Xcm[i, t, j]
                Ytot[i, t, j] = Ycm[i, t, j]

    # Copy ECPC profiles
    for i in range(Ncup):
        for t in range(tspan):
            for j in range(comp):
                Xtot[i, el_time + t, j] = X[i, t, j]
                Ytot[i, el_time + t, j] = Y[i, t, j]

    # Combine elution volume
    diff = tspan  # Turnover time step
    Vextrusion = np.zeros(diff)
    for i in range(diff):
        Vextrusion[i] = Vcell * (i + 1) + VCMspan[-1]

    # Total elution volume
    Vspan = np.zeros(el_time + tspan)
    for i in range(el_time):
        Vspan[i] = VCMspan[i]
    for i in range(tspan):
        Vspan[el_time + i] = Vextrusion[i]

    # CM and extrusion boundary
    V_boundary = np.array([VCMspan[-1], Vspan[-1]])

    return Vspan, Cout, Xtot, Ytot, V_boundary
