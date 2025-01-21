%PNNL CCC submodel called 'Cup model' Written by Hoon Choi  June 08 2020
%input parameters are as follows. (SP - stationary phase, MP - mobile phase
% Sf = stationary factor = volume ratio of [V_SP]/[V_MP]
% KD = Distribution coefficient ([Conc_SP]eq/[Conc_MP]eq)
% Ncup = number of cup
% Vcm = elution volume to stop Classic elution
% C0 = injection concentration
% Vinj = Number of cups for injection volume
% Celution = give elution histories of eluent
% X = MP concentration profiles in cells -> using it to EECCC/dual mode
% Y = SP concentration profiles in cells -> collect for EECCC/dual mode

function [Vspan Cout X Y] = CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj)

n = length(KD);
P = Sf/(1-Sf); %phase ratio
%KD is the partition coefficient = C[SP]/C[MP]

kA = 1./(1+P.*KD); %Retention Factor
% kB = P.*KD.*kA;
vmcup = Vc/Ncup*(1-Sf);
Ninj = Vinj/vmcup; %number of cells filled by injection
Tau = round(Vcm/vmcup);



X = zeros(Ncup,sum(Tau),n);  % mobile phase concentration matrix C(i,t)
Y = zeros(Ncup,sum(Tau),n);
Cinj = zeros(1,sum(Tau),n); %injection concentration Cin(t)


for j = 1:n  %for each component
    
    for t = 1:Ninj

        Cinj(1,t,j) = C0(j); 

    end
    
% add tail concentration

    Ninj_cup = floor(Ninj);
    Massin = Ninj_cup*vmcup*C0(j);
    diff = (Vinj*C0(j)-Massin)/(Vinj*C0(j)); %mass difference in percentage
    
    if diff >=0.02 
        fprintf('add tail concentration ')
        Vtruncate = vmcup*(Ninj-Ninj_cup);
        Ctail = C0(j)*Vtruncate/vmcup;
        Cinj(1,Ninj_cup+1,j) = Ctail; % additional injection for correcting mass balance
                        %by adding tail concentration to compensate truncate cup volume lost
    end           

    
    
    %initial boundary
    
    X(1,1,j) = kA(j)*Cinj(1,1,j); %initial condition (2)
    Y(1,1,j) = KD(j)*X(1,1,j);
    
    %MB calculation

    for t = 2:Tau

        X(1,t,j) = kA(j)*Cinj(1,t,j)+kA(j)*P*Y(1,t-1,j);
        Y(1,t,j) = KD(j)*X(1,t,j);
        
        for i = 2:Ncup

            X(i,t,j) = kA(j)*(X(i-1,t-1,j)+P*Y(i,t-1,j));
            Y(i,t,j) = KD(j)*X(i,t,j);
            
        end

    end

   %Outlet concentration
   
    Cout(j,:) = X(Ncup,:,j);  %give elution history data
    
end

    Nturn = linspace(0,sum(Tau),t); % number of turnover
    Vspan = vmcup.*Nturn;

end

