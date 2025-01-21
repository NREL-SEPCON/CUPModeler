% EECPC - extrusion mode of CCC by replacing mobile phase with SP
% written by Hoon Choi

% Assume the same flowrate is used
% Turnover time is automatically calculated 
% extrution state: turnover = Ncup, dT = vcup
% Xtot: total MP profiles (CM+EECPC)
% Ytot: total SP profiles (CM+EECPC)
% Cout: elution volume vs. column outlet concentration
% X: MP profiles during EECPC
% Y: SP profiles during EECPC
% Xcm: MP profiles from CM
% Ycm: SP profiles from CM


function [Vspan, Cout, Xtot, Ytot, V_boundary] = ECPC_V1(KD, Vc, Sf, Xcm, Ycm)

P = Sf/(1-Sf); %phase ratio
Vm = Vc*(1-Sf); % MP volume
% Vs = Vc*Sf;
kA = 1./(1+P.*KD); %Retention Factor!

%  Nturn = linspace(0,Tau,t); % number of turnover


[Ncup el_time comp] = size(Xcm);   %Ccup profile (Ncup,time,species)
vmcup = Vm/Ncup;
tCM = el_time;
VCMspan = vmcup.*linspace(1,tCM,tCM); % Vspan for previous CM  

tspan = fix(ceil(Ncup*1.3)); % timespan for MP (Ncup) + SP (Ncup*Sf);x1.3 to give enough elution time
Y = zeros(Ncup, tspan,  comp); %SP Concentration g/L
X = zeros(Ncup, tspan, comp); % MP concentration

%load previous concentration profiles from classic elution to set initial boundary
Xin = zeros(Ncup,1,comp);
Yin = zeros(Ncup,1,comp);


for h = 1:length(KD)
%     X_elution(:,:,comp) = Xcm(:,:,comp); % Keep use the same format (i,t,j)
%     Y_elution(:,:,comp) =  Ycm(:,:,comp);               %KD(comp).*X_elution(:,:,comp);
    Xin(:,1,h) = Xcm(:,el_time,h);
    Yin(:,1,h) = Ycm(:,el_time,h);       %KD(comp).*Xin(:,1,comp);
    
end

Vcell = Vc/Ncup;
% Vmcup = Vm/Ncup;

% n = length(KD);

for j = 1:comp  %comp
    
%EECPC start - displace one cell at a given timestep by new SP

%     t=1; %initial condition at t = 1
    Y(1,1,j) = 0;
    X(1,1,j) = 0;
% Y(1,1,j) = Sf*Yin(1,1,j);


    for i = 2:Ncup
        
        % X(i,1,j) = kA(j)*(Xin(i-1,1,j)+P*Yin(i,1,j));
        % Y(i,1,j) = KD(j)*X(i,1,j);

        X(i,1,j) = Xin(i-1,1,j);
        Y(i,1,j) = Yin(i-1,1,j);

    end

              
     for t = 2:Ncup % MP elution end at Ncup time 
                
          for i = 2:Ncup      
           
% one cell is displaced by SP after one turnover                    
                X(i,t,j) = X(i-1,t-1,j);
                Y(i,t,j) = Y(i-1,t-1,j);
                  
                 
          end
          
         
     end
     

     %save outlet concentration 
         for h = 1:comp
            
                CoutCM (h,:) = Xcm(Ncup,:,h);
            
               for t = 1:tspan
               
                   CoutE(h,t) = Sf*Y(Ncup,t,h)+(1-Sf)*X(Ncup,t,h);
                    
               end
               % 
         end

  end

                  Cout = [CoutCM   CoutE];  % ouput effluent histories


     %Combine concentration profiles into Xtot & Ytot from CM to EECCC
          Xtot = [Xcm  X];
          Ytot = [Ycm  Y];
     
        
          
          diff = tspan; %turnover time step
          texrusion = linspace(1, diff, diff);
          Vextrusion = Vcell.*texrusion;

          V_EECPC = VCMspan(end) + Vextrusion;

          Vspan = [VCMspan   V_EECPC]; %total elution volume
            
          % V_boundary = [VCMspan(end)   VCMspan(end)+Vsweep(end)];
          V_boundary = [VCMspan(end)   Vspan(end)];

end

          
     
  