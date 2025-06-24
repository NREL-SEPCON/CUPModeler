% Dual mode CCC by reversing the stationary while keep mobile phase
% written by Hoon Choi 03/10/23
% Loading New SP into a column with reverse flow in MDM mode

%input parameters are as follows. (SP - stationary phase, MP - mobile phase
% Sf = stationary factor = volume ratio of [V_SP]/[V_C]
% P = phase ratio = Vsp/Vmp = Sf/(1-Sf)
% KD = Distribution coefficient ([Conc_SP]eq/[Conc_MP]eq)
% Ncup = number of column efficiency 
% Tau = number of turnover time (iterations)
% C0 = injection concentration
% Celution = give elution histories of eluent
% X = MP concentration profiles in cells -> using it to EECCC/dual mode
% Y = SP concentration profiles in cells -> collect for EECCC/dual mode
% Vcell = Vc/Ncup ; Vmcup = Vcell/(1-Sf)
% time step is to move a vmcup but Vextra is divided into Vcell; Tstep = Vscup/F

% loading column profiles from MDM_CM: X, Y,tau_SP, KD, Sf, Vc, 
% print out column profiles: X, Y, Cdin, Cdout, Vspan (elution volume)


function [Vspan, Cout, Xtot, Ytot] = CUP_MDMDM(Sf, KD, Vc, Xcup, Ycup, Tstep)


[Ncup el_time comp] = size(Xcup);   %Ccup profile (Ncup,time,species)

% tspan = fix(ceil(Ncup*(1+Sf)*1.1)); % timespan for MP (Ncup) + SP (Ncup*Sf);1.1 to give enough elution time
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
    
    

for j = 1:comp  %comp

%      %initial condition at t = 1; time = 1      
      
        X(Ncup,1,j) = kA(j)*Xin(Ncup,1,j);
        Y(Ncup,1,j) = KD(j)*X(Ncup,1,j);


         for i = Ncup:-1:2  %time = 1; calculate from Ncup to 1st cell - initial boundary of column
        
            X(i-1,1,j) = kA(j)*(Xin(i-1,1,j)+P*Yin(i,1,j));
            Y(i-1,1,j) = KD(j)*X(i-1,1,j);
                   
        end
    

% calculate solute movement from t =2 

      for t = 2: Tstep  % SP reverse elution (dT = Vscup) 
           
             % Boundary condition first for Ncup cell
             X(Ncup,t,j) = kA(j)*X(Ncup,t-1,j);  %from previous run
             Y(Ncup,t,j) = KD(j)*X(Ncup,t,j);
             

             %column calculation - SP moving from [Ncup-1] to 1st cell
             for i = Ncup:-1:2
                    
                 X(i-1,t,j) = kA(j)*(X(i-1,t-1,j)+P*Y(i,t-1,j));
                 Y(i-1,t,j) = KD(j)*X(i-1,t,j);
    
             end
         
      end         % MB calculation end

        
          %Effluent history = first dead volume cell for the entire time step
        Cout(j,:) = Y(1, :,j); %effluent history at the end of system

end

       %Combine concentration profiles into Xtot & Ytot 
          Xtot = [Xcup  X];
          Ytot = [Ycup  Y];


          %make elution time and volume matrix
          tspan = linspace(1, Tstep, Tstep);
          Vspan = Vscup.*tspan;

end

          
     
  