function [Vtot, Ctot, Xtot, Ytot, Tcut, VswDM, VswCM] = MDMV2(Sf, KD, Vc, Ncup, Cfeed, Vinj, Vcm)
% This function calculates elution histories for a given semiprep column
% Inputs:
% Sf - Semiprep column correlation factor
% KD - vector of dissociation constants
% Vc - Column volume (mL)
% Ncup - Number of column cups
% Vinj - Injection volume (mL)
% Cfeed - vector of feed concentration
% F - Flow rate (mL/min)
% Vcm - vector of the elution volume for each step (mL)
% Tcut - timestep at the end of each run


Turn = length (Vcm); % count the number of MDM switchings

Tcut = zeros(1,Turn);
%Calculate volumes
Vcell = Vc / Ncup;  %Cup volume calc
vmcup = Vcell * (1 - Sf);
vscup = Vcell * Sf;



for index = 1:Turn

    if index == 1  % 1st CM start with injection using CUP model
        
%         [Vtot, Ctot, Xcm, Ycm] = CupV3(Sf, KD, Vc, Ncup, Tstep, Cfeed, Vinj);
        [Vtot Ctot Xcm Ycm] = CupV6(Sf, KD, Vc, Ncup, Vcm(index), Cfeed, Vinj);


        Xtot = Xcm;
        Ytot = Ycm;

        Tcut(index) = round(Vcm(index)/vmcup);
        
    elseif mod(index,2) == 0   %2nd, 4th, 6th swtiching CM to DM
        Tstep2 = round(Vcm(index) / vscup); %calculate time step
                Tcut(index) = Tstep2 + Tcut(index-1);

        [Vspan, CoutDM, Xdm, Ydm] = CUP_MDMDM(Sf, KD, Vc, Xcm, Ycm, Tstep2);
        
        Vdm1 = Vtot(end);
        Vspan = Vdm1 + Vspan;
        Vtot = [Vtot Vspan];
        Ctot = [Ctot CoutDM];
        
        Xtot = Xdm;
        Ytot = Ydm;


    elseif mod(index,2) == 1
        
        % Calculate timestep duration for third elution
        Tstep3 = round(Vcm(index) / vmcup);
                Tcut(index) = Tstep3 + Tcut(index-1);

        % calculation for elution peaks for third elution
        [Vspan, CoutCM, Xcm, Ycm] = CUP_MDMCM(Sf, KD, Vc, Xdm, Ydm, Tstep3);
        
        % extend elution volume from the previous elution
        Vcm1 = Vtot(end);
        Vspan = Vcm1 + Vspan;

        % combine the three elution histories
        Vtot = [Vtot Vspan];
        Ctot = [Ctot CoutCM];
     
        Xtot = Xcm;
        Ytot = Ycm;


    end

    
end

        Velute = cumsum(Vcm);
        VswCM= Velute(1:2:Turn);
        VswDM = Velute(2:2:Turn);

end

