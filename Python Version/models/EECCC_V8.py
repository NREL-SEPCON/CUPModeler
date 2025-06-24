from numba import jit, prange
import numpy as np


@jit(nopython=True, parallel=True)
def EECCC_V8(KD, Vc, Sf, Xcm, Ycm, extrusion_steps=None):
    """
    EECCC - Extrusion mode of CCC by replacing mobile phase with SP.
    Converted from MATLAB to Python.

    Parameters:
    KD: Distribution coefficient ([Conc_SP]eq/[Conc_MP]eq)
    Vc: Total column volume
    Sf: Stationary factor (volume ratio of [V_SP]/[V_MP])
    Xcm: MP profiles from CM (Ncup x el_time x comp)
    Ycm: SP profiles from CM (Ncup x el_time x comp)

    Returns:
    Vspan: Total elution volume
    Cout: Elution volume vs. column outlet concentration
    Xtot: Total MP profiles (CM + EECCC)
    Ytot: Total SP profiles (CM + EECCC)
    V_boundary: CM and Sweep boundary in terms of elution volume
    """
    P = Sf / (1 - Sf)  # Phase ratio
    Vm = Vc * (1 - Sf)  # MP volume
    Vs = Vc * Sf  # SP volume
    kA = 1 / (1 + P * KD)  # Retention factor

    Ncup, el_time, comp = Xcm.shape  # Cup profile dimensions
    vmcup = Vm / Ncup
    tCM = el_time

    # VCMspan for previous CM
    VCMspan = np.zeros(tCM)
    for i in range(tCM):
        VCMspan[i] = vmcup * (i + 1)

    if extrusion_steps is not None:
        # Convert to integer to avoid typing issues
        # tspan represents the total timesteps for the extrusion phase
        # It should be at least Ncup (for the sweep phase) plus additional extrusion steps
        additional_extrusion_steps = int(extrusion_steps)
        tspan = Ncup + additional_extrusion_steps
    else:
        tspan = int(np.ceil(Ncup * (1 + Sf) * 1.3))

    Y = np.zeros((Ncup, tspan, comp))  # SP concentration
    X = np.zeros((Ncup, tspan, comp))  # MP concentration

    Vcell = Vc / Ncup
    Vmcup = Vm / Ncup

    # Process each component in parallel
    for j in prange(comp):
        # EECCC start - Sweep state
        Y[0, 0, j] = Sf * Ycm[0, el_time - 1, j]
        for i in range(1, Ncup):
            X[i, 0, j] = kA[j] * (Xcm[i - 1, el_time - 1, j] + P * Ycm[i, el_time - 1, j])
            Y[i, 0, j] = KD[j] * X[i, 0, j]

        # MP elution ends at Ncup time
        for t in range(1, Ncup):
            for i in range(1, Ncup):
                if i <= t:
                    # One MP cell is displaced by SP after one turnover
                    Y[i, t, j] = (1 - Sf) * Y[i - 1, t - 1, j] + Sf * Y[i, t - 1, j]
                else:
                    X[i, t, j] = kA[j] * (X[i - 1, t - 1, j] + P * Y[i, t - 1, j])
                    Y[i, t, j] = KD[j] * X[i, t, j]

        # Extrusion start
        for t in range(Ncup, tspan):
            for i in range(1, Ncup):
                Y[i, t, j] = Y[i - 1, t - 1, j]  # Move forward to outlet without mixing

    # Save outlet concentration
    Cout = np.zeros((comp, el_time + tspan))
    for h in range(comp):
        # CM outlet
        for t in range(el_time):
            Cout[h, t] = Xcm[Ncup - 1, t, h]
        # EECCC outlet
        for t in range(tspan):
            if t < Ncup:
                Cout[h, el_time + t] = X[Ncup - 1, t, h]
            else:
                Cout[h, el_time + t] = Y[Ncup - 1, t, h]

    # Combine concentration profiles into Xtot & Ytot from CM to EECCC
    Xtot = np.zeros((Ncup, el_time + tspan, comp))
    Ytot = np.zeros((Ncup, el_time + tspan, comp))

    # Copy CM profiles
    for i in range(Ncup):
        for t in range(el_time):
            for j in range(comp):
                Xtot[i, t, j] = Xcm[i, t, j]
                Ytot[i, t, j] = Ycm[i, t, j]

    # Copy EECCC profiles
    for i in range(Ncup):
        for t in range(tspan):
            for j in range(comp):
                Xtot[i, el_time + t, j] = X[i, t, j]
                Ytot[i, el_time + t, j] = Y[i, t, j]

    # Combine elution volume (Sweep + Extrusion)
    Vsweep = np.zeros(Ncup)
    for i in range(Ncup):
        Vsweep[i] = Vmcup * (i + 1)

    diff = tspan - Ncup
    Vextrusion = np.zeros(diff)

    # For extrusion, each step should advance by the stationary phase volume per cup
    # not the total cell volume, since we're pushing stationary phase
    Vs = Vc * Sf  # Total stationary phase volume
    Vscup = Vs / Ncup  # Stationary phase volume per cup
    for i in range(diff):
        Vextrusion[i] = Vscup * (i + 1) + Vsweep[-1]

    # Make elution volume matrix for EECCC
    V_EECCC = np.zeros(tspan)
    for i in range(Ncup):
        V_EECCC[i] = Vsweep[i] + VCMspan[-1]
    for i in range(diff):
        V_EECCC[Ncup + i] = Vextrusion[i] + VCMspan[-1]

    # Total elution volume
    Vspan = np.zeros(el_time + tspan)
    for i in range(el_time):
        Vspan[i] = VCMspan[i]
    for i in range(tspan):
        Vspan[el_time + i] = V_EECCC[i]

    V_boundary = np.array([VCMspan[-1], VCMspan[-1] + Vsweep[-1]])

    return Vspan, Cout, Xtot, Ytot, V_boundary
