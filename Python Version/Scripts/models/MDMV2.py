import numpy as np
from .CupV6 import CupV6
from .CUP_MDMDM import CUP_MDMDM
from .CUP_MDMCM import CUP_MDMCM


def MDMV2(Sf, KD, Vc, Ncup, Cfeed, Vinj, Vcm):
    """
    This function calculates elution histories for a given semiprep column.

    Parameters:
    Sf: Semiprep column correlation factor
    KD: Vector of dissociation constants
    Vc: Column volume (mL)
    Ncup: Number of column cups
    Cfeed: Vector of feed concentration
    Vinj: Injection volume (mL)
    Vcm: Vector of the elution volume for each step (mL)

    Returns:
    Vtot: Total elution volume
    Ctot: Total elution concentration
    Xtot: Total MP profiles
    Ytot: Total SP profiles
    Tcut: Timestep at the end of each run
    VswDM: Switching volumes for DM
    VswCM: Switching volumes for CM
    """
    Turn = len(Vcm)  # Count the number of MDM switchings
    Tcut = np.zeros(Turn)

    # Calculate volumes
    Vcell = Vc / Ncup  # Cup volume
    vmcup = Vcell * (1 - Sf)
    vscup = Vcell * Sf

    # Initialize arrays as None to start
    Vtot = None
    Ctot = None
    Xtot = None
    Ytot = None

    n_components = len(KD)  # Number of components

    for index in range(Turn):
        if index == 0:  # 1st CM start with injection using CUP model
            Vspan, Cout, Xcm, Ycm, _ = CupV6(Sf, KD, Vc, Ncup, Vcm[index], Cfeed, Vinj)

            # Initialize arrays with the first set of values
            Vtot = Vspan.copy()
            Ctot = Cout.copy()
            Xtot = Xcm.copy()
            Ytot = Ycm.copy()

            Tcut[index] = round(Vcm[index] / vmcup)

        elif index % 2 == 1:  # 2nd, 4th, 6th switching CM to DM
            Tstep2 = round(Vcm[index] / vscup)  # Calculate time step
            Tcut[index] = Tstep2 + Tcut[index - 1]

            Vspan, CoutDM, Xdm, Ydm = CUP_MDMDM(Sf, KD, Vc, Xcm, Ycm, Tstep2)

            # Add offset for Vspan based on the last value of Vtot
            Vdm1 = Vtot[-1]
            Vspan = Vspan + Vdm1

            # Concatenate arrays
            Vtot = np.append(Vtot, Vspan[1:])  # Skip the first point which would be duplicate

            # Ensure CoutDM has same number of components as Ctot
            if CoutDM.shape[0] != Ctot.shape[0]:
                print(f"Warning: Component dimension mismatch - CoutDM: {CoutDM.shape}, Ctot: {Ctot.shape}")

            # Concatenate along the time axis (axis 1)
            Ctot = np.hstack((Ctot, CoutDM[:, 1:]))

            # Store for next iteration
            Xtot = Xdm.copy()
            Ytot = Ydm.copy()

        elif index % 2 == 0:  # 3rd, 5th, 7th switching DM to CM
            Tstep3 = round(Vcm[index] / vmcup)  # Calculate timestep duration
            Tcut[index] = Tstep3 + Tcut[index - 1]

            Vspan, CoutCM, Xcm, Ycm = CUP_MDMCM(Sf, KD, Vc, Xdm, Ydm, Tstep3)

            # Add offset for Vspan based on the last value of Vtot
            Vcm1 = Vtot[-1]
            Vspan = Vspan + Vcm1

            # Concatenate arrays
            Vtot = np.append(Vtot, Vspan[1:])  # Skip the first point which would be duplicate

            # Ensure CoutCM has same number of components as Ctot
            if CoutCM.shape[0] != Ctot.shape[0]:
                print(f"Warning: Component dimension mismatch - CoutCM: {CoutCM.shape}, Ctot: {Ctot.shape}")

            # Concatenate along the time axis (axis 1)
            Ctot = np.hstack((Ctot, CoutCM[:, 1:]))

            # Store for next iteration
            Xtot = Xcm.copy()
            Ytot = Ycm.copy()

    Velute = np.cumsum(Vcm)
    VswCM = Velute[::2]  # Switching volumes for CM
    VswDM = Velute[1::2] if len(Velute) > 1 else []  # Switching volumes for DM

    return Vtot, Ctot, Xtot, Ytot, Tcut, VswDM, VswCM
