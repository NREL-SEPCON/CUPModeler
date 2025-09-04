from numba import jit, prange
import numpy as np

@jit(nopython=True, parallel=True)
def DualV2(KD, Vc, Sf, F, Vdm, Xcm, Ycm):
    """
    Parameters:
    KD: Distribution coefficient ([Conc_SP]eq/[Conc_MP]eq)
    Vc: Total column volume
    Sf: Stationary factor (volume ratio of [V_SP]/[V_MP])
    F: Flow rate
    Vdm: Elution volume for dual mode
    Xcm: MP profiles from classic elution (Ncup x el_time x comp)
    Ycm: SP profiles from classic elution (Ncup x el_time x comp)

    Returns:
    Vspan: Total elution volume
    Cout: Column outlet profiles for MP and SP
    X: Concentration in MP during dual mode
    Y: Concentration in SP during dual mode
    """
    P = Sf / (1 - Sf)
    Vm = Vc * (1 - Sf)
    Vs = Vc * Sf
    kA = 1 / (1 + P * KD)  # Retention factor

    Ncup, el_time, comp = Xcm.shape  # Cup profile dimensions
    vmcup = Vm / Ncup
    vscup = Vs / Ncup

    tCM = el_time
    VCMspan = np.zeros(tCM)
    for i in range(tCM):
        VCMspan[i] = vmcup * (i + 1)  # Previous CM elution timestep

    dt = vscup / F
    Tau = int(round(Vdm / vscup))  # Elution timestep for dual mode

    X = np.zeros((Ncup, Tau, comp))  # MP concentration
    Y = np.zeros((Ncup, Tau, comp))  # SP concentration

    # Process each component in parallel
    for j in prange(comp):
        # Initial condition at t = 0
        X[Ncup - 1, 0, j] = kA[j] * Xcm[Ncup - 1, el_time - 1, j]
        Y[Ncup - 1, 0, j] = KD[j] * X[Ncup - 1, 0, j]

        # Calculate from Ncup to 1st cell for t=0
        for i in range(Ncup - 1, 0, -1):
            X[i - 1, 0, j] = kA[j] * (Xcm[i - 1, el_time - 1, j] + P * Ycm[i, el_time - 1, j])
            Y[i - 1, 0, j] = KD[j] * X[i - 1, 0, j]

        # SP reverse elution (dT = Vscup)
        for t in range(1, Tau):
            # Boundary condition for Ncup cell
            X[Ncup - 1, t, j] = kA[j] * X[Ncup - 1, t - 1, j]
            Y[Ncup - 1, t, j] = KD[j] * X[Ncup - 1, t, j]

            # SP reverse elution from [Ncup-1] to 1st cell
            for i in range(Ncup - 1, 0, -1):
                X[i - 1, t, j] = kA[j] * (X[i - 1, t - 1, j] + P * Y[i, t - 1, j])
                Y[i - 1, t, j] = KD[j] * X[i - 1, t, j]

    # Combine concentration profiles into Xtot & Ytot from CM to dual mode
    Xtot = np.zeros((Ncup, el_time + Tau, comp))
    Ytot = np.zeros((Ncup, el_time + Tau, comp))

    # Copy CM profiles
    for i in range(Ncup):
        for t in range(el_time):
            for j in range(comp):
                Xtot[i, t, j] = Xcm[i, t, j]
                Ytot[i, t, j] = Ycm[i, t, j]

    # Copy dual mode profiles
    for i in range(Ncup):
        for t in range(Tau):
            for j in range(comp):
                Xtot[i, el_time + t, j] = X[i, t, j]
                Ytot[i, el_time + t, j] = Y[i, t, j]

    # Make elution time and volume matrix for dual mode
    Vdm_span = np.zeros(Tau)
    for i in range(Tau):
        Vdm_span[i] = vscup * (i + 1) + VCMspan[-1]

    # Total elution volume
    Vspan = np.zeros(el_time + Tau)
    for i in range(el_time):
        Vspan[i] = VCMspan[i]
    for i in range(Tau):
        Vspan[el_time + i] = Vdm_span[i]

    # Save outlet concentration
    Cout = np.zeros((comp, el_time + Tau))
    for h in range(comp):
        # CM outlet
        for t in range(el_time):
            Cout[h, t] = Xcm[Ncup - 1, t, h]
        # DM outlet
        for t in range(Tau):
            Cout[h, el_time + t] = Y[0, t, h]

    return Vspan, Cout, X, Y
