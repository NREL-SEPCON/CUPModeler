% EECCC - extrusion mode of CCC by replacing mobile phase with SP
% written by Hoon Choi

% Assume the same flowrate is used
% Turnover time is automatically calculated 
% sweep state: turnover = Ncup, dT = vmcup 
% extrution state: turnover = Ncup*Sf, dT = vcup
% Xtot: total MP profiles (CM+EECCC)
% Ytot: total SP profiles (CM+EECCC)
% Cout: elution volume vs. column outlet concentration
% X: MP profiles during EECCC
% Y: SP profiles during EECCC
% Xcm: MP profiles from CM
% Ycm: SP profiles from CM
% V_boundary: CM, Sweep boundary in terms of elution volume

function [Vspan, Cout, Xtot, Ytot, V_boundary] = EECCC_V8(KD, Vc, Sf, Xcm, Ycm)

P = Sf/(1-Sf); %phase ratio
Vm = Vc*(1-Sf); % MP volume
% Vs = Vc*Sf;
kA = 1./(1+P.*KD); %Retention Factor!

%  Nturn = linspace(0,Tau,t); % number of turnover


[Ncup el_time comp] = size(Xcm);   %Ccup profile (Ncup,time,species)
% X_elution = zeros(Ncup,  el_time,  comp); %Initial MP Concentration g/L   (column , time , species)
% Y_elution = zeros(Ncup, el_time, comp);
vmcup = Vm/Ncup;
tCM = el_time;
VCMspan = vmcup.*linspace(1,tCM,tCM); % Vspan for previous CM  

tspan = fix(ceil(Ncup*(1+Sf)*1.3)); % timespan for MP (Ncup) + SP (Ncup*Sf);x1.3 to give enough elution time
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
Vmcup = Vm/Ncup;

% n = length(KD);

for j = 1:comp  %comp
    
%EECCC start - sweep state

%     t=1; %initial condition at t = 1
    Y(1,1,j) = Sf*Yin(1,1,j);

    for i = 2:Ncup
        
        X(i,1,j) = kA(j)*(Xin(i-1,1,j)+P*Yin(i,1,j));
        Y(i,1,j) = KD(j)*X(i,1,j);
               
    end

              
     for t = 2:Ncup % MP elution end at Ncup time 
                
          for i = 2:Ncup      
           
                if i <= t
% one MP cell is displaced by SP after one turnover                    

                    Y(i,t,j) = (1-Sf)*Y(i-1,t-1,j)+Sf*Y(i,t-1,j);

                 elseif i > t 
                    X(i,t,j) = kA(j)*(X(i-1,t-1,j)+P*Y(i,t-1,j));
                    Y(i,t,j) = KD(j)*X(i,t,j);
                 end
                 
          end
          
         
     end
     
     %Sweep end  where dT = (1-Sf)Vc/Ncup = vmcup
     %%Extrusion start  where dT = Vc/Ncup =vcup
          
     for t = Ncup+1:tspan
     
         for i = 2:Ncup
                
             Y(i,t,j) = Y(i-1,t-1,j); %move forward to outlet without mixing

         end
         
     end

     %save outlet concentration 
         for h = 1:comp
            
                CoutCM (h,:) = Xcm(Ncup,:,h);
            
               for t = 1:tspan
                    if t <= Ncup
                        CoutE(h, t) = X(Ncup,t,h);
                    else
                        CoutE(h,t) = Y(Ncup,t,h);
                    end
                    
               end

          end

                  Cout = [CoutCM   CoutE];  % ouput effluent histories


     %Combine concentration profiles into Xtot & Ytot from CM to EECCC
          Xtot = [Xcm  X];
          Ytot = [Ycm  Y];
     
        
          
          % Combine elution volume (sweep +extrusion)
          
          tsweep = linspace(1, Ncup, Ncup);
          Vsweep = Vmcup.*tsweep;

          diff = tspan - Ncup;      %Sf*Ncup;
          texrusion = linspace(1, diff, diff);
          Vextrusion = Vcell.*texrusion;
          Vextrusion = Vsweep(end)+Vextrusion;
        
           %make elution volume matrix for EECCC 
          V_EECCC = [Vsweep    Vextrusion];

          V_EECCC = VCMspan(end) + V_EECCC;

          Vspan = [VCMspan   V_EECCC]; %total elution volume
            
          V_boundary = [VCMspan(end)   VCMspan(end)+Vsweep(end)];
          


end

          
     
  