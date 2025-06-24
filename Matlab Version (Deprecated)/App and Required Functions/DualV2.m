% Dual mode CCC by reversing the stationary while keep mobile phase
% written by Hoon Choi
% Loading New SP into a column with reverse flow

%Xtot: mobile phase concentration from classic elution
%Ytot: stationary phase concentration from classic elution
%Col_out: Column outlet proflies for MP and SP respectively
%X: Concentration in MP during dual mode
%Y: Concentration in SP during dual mode


function [Vspan Cout, X, Y] = DualV2(KD, Vc, Sf, F, Vdm, Xcm, Ycm)

P = Sf/(1-Sf);
Vm = Vc*(1-Sf);
Vs = Vc*Sf;
kA = 1./(1+P.*KD); %Retention Factor!



[Ncup el_time comp] = size(Xcm);   %Ccup profile (Ncup,time,species)

vmcup = Vm/Ncup;
vscup = Vs/Ncup;

tCM = el_time;
VCMspan = vmcup.*linspace(1,tCM,tCM); %previous CM elution timestep

dt = vscup/F;
Tau = round(Vdm/vscup);  %elution timestep for DM


X = zeros(Ncup, Tau, comp); % MP concentration
Y = zeros(Ncup, Tau,  comp); %SP Concentration g/L


%take previous profiles from classic elution to set initial boundary
Xin = zeros(Ncup,1,comp);
Yin = zeros(Ncup,1,comp);



for h = 1:comp

    Xin(:,1,h) = Xcm(:,el_time,h);
    Yin(:,1,h) = Ycm(:,el_time,h);       %KD(comp).*Xin(:,1,comp);
    
end


for j = 1:comp  %comp
    
    t=1; %initial condition at t = 1
    
    X(Ncup,1,j) = kA(j)*Xin(Ncup,1,j);
    Y(Ncup,1,j) = KD(j)*X(Ncup,1,j);

    for i = Ncup:-1:2  %calculate from Ncup to 1st cell
        
        X(i-1,t,j) = kA(j)*(Xin(i-1,1,j)+P*Yin(i,1,j));
        Y(i-1,t,j) = KD(j)*X(i-1,t,j);
               
    end
    
              
     for t = 2:Tau % SP reverse elution (dT = Vscup) 
                
         
         % Boundary condition first for Ncup cell
         X(Ncup,t,j) = kA(j)*X(Ncup,t-1,j);
         Y(Ncup,t,j) = KD(j)*X(Ncup,t,j);
         
         %SP reverse elution from [Ncup-1] to 1st cell
         for i = Ncup:-1:2
                
             X(i-1,t,j) = kA(j)*(X(i-1,t-1,j)+P*Y(i,t-1,j));
             Y(i-1,t,j) = KD(j)*X(i-1,t,j);

         end
         
     end

     %Combine concentration profiles into Xtot & Ytot from CM to EECCC
          Xtot = [Xcm  X];
          Ytot = [Ycm  Y];
     

          %make elution time and volume matrix for EECCC 
          tspan = linspace(1, Tau, Tau);
          Vdm = vscup.*tspan;
          Vdm = VCMspan(end) + Vdm;

          Vspan = [VCMspan  Vdm];  %total elution volume
          
            %save outlet concentration 
        CoutDM = [];
         for h = 1:comp
            
                CoutCM (h,:) = Xcm(Ncup,:,h);
            
               for t = 1:Tau
                    
                  CoutDM (h,t) = Y(1,t,h);
               
               end


         end

         Cout = [CoutCM  CoutDM];
              
%           
%           for i = 1:n
%               
%               M(i,:) = Y(1,:,i);   % column outlet is 1st cell in dual mode
%               M(i+n,:)= X(1,:,i);  % Column outlet is 1st cell
%                                          
%           end
%           
%           Col_out = [Vspan; M]';  % [Vol yi  xi] column outlet profiles
%                 


end

          
     
  