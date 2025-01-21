function [Vx Vy] = MDMrT(Sf, KD, Vc, F, Vcm)
% This function calculates elution histories for a given semiprep column
% Inputs:
% Sf - Semiprep column correlation factor
% Vc - Column volume (mL)
% F - Flow rate (mL/min)
% Vcm - vector of the elution volume for each step (mL)
% KD - vector of dissociation constants


% slope to calculate the VR solution

Turn = length (Vcm); % count the number of MDM switchings

n = length(KD); %count the number of component
Vy = zeros(Turn,n); %trajectory boundary front (start of injection)
% Vyy = zeros(Turn,n); %trajectory boundary end (end of injection)

for comp = 1:n


    k1 = 1./(1-Sf+Sf*KD(comp));
    k2 = (-1)./(Sf+(1-Sf)/KD(comp));


    for i = 1:Turn

     if Vy(i,comp) >Vc
                break
            end

            if i ==1
                Vy(i,comp) = k1*Vcm(i);
%                 Vyy(i,comp) = k1*(Vcm(i)-Vinj);
    
            elseif mod(i,2) == 0 % DM mode
                Vy(i,comp) = k2*(Vcm(i))+Vy(i-1,comp);
%                 Vyy(i,comp) = k2*(Vcm(i))+Vyy(i-1,comp);
    
            elseif mod(i,2) == 1 %CM mode
                Vy(i,comp) = k1*(Vcm(i))+Vy(i-1,comp); 
%                 Vyy(i,comp) = k1*(Vcm(i))+Vyy(i-1,comp);
   

            end
        
        
%             if Vy(i,comp) >Vc
%                 break
%             end


    end

      
end

Vx = [0 Vcm]';
% Vxx = [Vinj Vcm]';
Vy = [zeros(1,n); Vy];
% Vyy = [zeros(1,n); Vyy];


