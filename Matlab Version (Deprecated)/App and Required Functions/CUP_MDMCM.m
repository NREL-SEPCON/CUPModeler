%input parameters are as follows. (SP - stationary phase, MP - mobile phase
% Sf = stationary factor = volume ratio of [V_SP]/[V_C]
% P = phase ratio = Vsp/Vmp = Sf/(1-Sf)
% KD = Distribution coefficient ([Conc_SP]eq/[Conc_MP]eq)
% Ncup = number of column efficiency 
% Tau = number of turnover time (iterations)
% Celution = give elution histories of eluent
% X = MP concentration profiles in cells -> using it to EECCC/dual mode
% Y = SP concentration profiles in cells -> collect for EECCC/dual mode
% Vcell = Vc/Ncup ; Vmcup = Vcell/(1-Sf)
% loading column profiles from MDM_DM: X, Y,  Sf, KD, Vc, tau_MP 
% print out column profiles: X, Y, Vspan (elution volume)



function [Vspan, Cout, Xtot, Ytot] = CUP_MDMCM(Sf, KD, Vc, Xcup, Ycup, Tstep)


[Ncup el_time comp] = size(Xcup);   %Ccup profile (Ncup,time,species)


Y = zeros(Ncup, Tstep,  comp); %SP Concentration g/L
X = zeros(Ncup, Tstep, comp); % MP concentration

%take previous profiles from classic elution to set initial boundary

Xin = zeros(Ncup,1,comp);
Yin = zeros(Ncup,1,comp);

P = Sf/(1-Sf);
Vm = Vc*(1-Sf);
Vs = Vc*Sf;
kA = 1./(1+P.*KD); %Retention Factor

Vcell = Vc/Ncup;
Vmcup = Vm/Ncup;
Vscup = Vs/Ncup;


%loading for cell calculation

    Xin(:,1,:) = Xcup(:,el_time,:);
    Yin(:,1,:) = Ycup(:,el_time,:);       %KD(comp).*Xin(:,1,comp);
    


for j = 1:comp
    
    %      %initial condition at t = 1; time = 1
            X(1,1,:) = kA(j)*(P*Yin(1,1,j));  %from previous run
            Y(1,1,:) = KD(j)*X(1,1,j);

      for i = 2:Ncup  %time = 1; calculate from 1st to Ncup cell 
        
            X(i,1,j) = kA(j)*(Xin(i-1,1,j)+P*Yin(i,1,j));
            Y(i,1,j) = KD(j)*X(i,1,j);
                   
      end


      %MB calculation
    for t = 2:Tstep

        % Boundary condition first for 1st cell
        X(1,t,j) = kA(j)*(P*Y(1,t-1,j));
        Y(1,t,j) = KD(j)*X(1,t,j);
        

   %column calculation - MP moving from 1st to Ncup cell
        for i = 2:Ncup

            X(i,t,j) = kA(j)*(X(i-1,t-1,j)+P*Y(i,t-1,j));
            Y(i,t,j) = KD(j)*X(i,t,j);
                        
        end
    end
    
   %Outlet concentration
       Cout(j,:) = X(Ncup, :,j); %elution histrory at the end of total system

end

 %Combine concentration profiles into Xtot & Ytot combining previous runs with CM

     Xtot = [Xcup  X];
     Ytot = [Ycup  Y];

    tspan = linspace(1, Tstep, Tstep);
    Vspan = Vmcup*tspan; % number of turnover


end

