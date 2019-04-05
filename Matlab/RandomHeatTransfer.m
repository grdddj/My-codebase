% SUMMARY
% This script runs a completely random simulation of heat transfer.
% Almost all the parameters are generated randomly, but all the material
% characteristics belong to real elements - this element, however, is also 
% being chosen at random from the metal_properties.csv file. 
% The csv list is generated by the python script, which can be easily
% modified to pull whatever elements and whatever properties we like.
% I chose to include only metals, and keep them in positive temperatures
% (in degrees) and in solid state, so below the melting temperature. 

%POSSIBLE IMPROVEMENTS
% - All the physical properties are temperature-dependent, so inputting a
% function instead of hardcoded value could be interesting idea.
% - I did not spent almost any time tuning the boundary conditions from a
% graphical level, to create some really extraordinary sceneries
% - Allow also for the state change (with latent heat) and support all the
% gases and fluids as well. 
% - Offer a GUI for the user to choose all the parameters and materials.
% - Refine the random behaviour, to make it more "predictable" (however
% strange it sounds)

%PERSONAL NOTICE
% Out of curiosity - as I really enjoyed doing this task - I am thinking of
% doing my Master Thesis on some similar topic, regarding programming 
% in Matlab or any other language (I am eager to learn even C).
% Could we have a small chat about this possibility? If you would be
% willing these days, please write me an email (170549@vutbr.cz), if not, 
% I will certainly contact you after this semester ends :) Thanks in advance. 

%% INITIALISATION
clc
clear all
clf
close all
satan=666; % The most important line of this script (changing it would invalidate the whole code!)

% Initialisating the list of materials from CSV file.  
% I am using the second "readtable", maybe redundantly, but I want to utilise 
% string values (name of elements), and readmatrix does not support that
% somehow, and doing everything with readtable would be boring. (I would be glad for advice here)
materials=readmatrix("metals_properties.csv");
materialsWithNames=readtable("metals_properties.csv");

% Picking the material for the simulation
position=MyRnd(2,length(materials)); % Choosing random material from the list
material=char(table2array(materialsWithNames(position,1))); % Getting the name of the material (with great difficulties)
tempMelt=materials(position,2);
rho=materials(position,3); % Getting the density
cp=materials(position,4); % Getting the heat capacity
lambda=materials(position,5); % Getting the thermal conductivity

% Setting the temperatures
tempMax=MyRnd(0,tempMelt); % Highest possible temperature for this plot (from 0 to tempMelt degrees, unless...)
if tempMax<100 % Defend against small numbers (and give some more chance to the number of the beast)
    if tempMelt>satan
        tempMax=satan;
    else
        tempMax=100;
    end
end
tempMin=MyRnd(0,floor(tempMax/2)); % Lowest possible temperature for this plot (from 0 to half of the tempMax)
InitTemp=MyRnd(tempMin,tempMax); %temperature at zero seconds (choose it somewhere in between)

% Variables to influence the granularity and duration of the result
gridsize=MyRnd(100,1000); %m
dx=gridsize/MyRnd(5,15); %m
dy=dx; %m
tspan=MyRnd(5,50); %s
dt=tspan/MyRnd(1000,5000); %s
dispEveryIthStep=MyRnd(10,50); %higher numbers make simulation and animation run faster since it renders only every ith step

% Setting boundary conditions for each of the side
LB=@(t,y) SetBoundaries(tempMin,tempMax,( MyRnd(tempMin,tempMax/3)*sin(exp(MyRnd(1,10))*pi) - MyRnd(tempMin,tempMax)*cos(exp(MyRnd(1,10))*pi) )); %left (Satan) boundary temperature
RB=@(t,y) SetBoundaries(tempMin,tempMax,( MyRnd(tempMin,tempMax*t)*sin(exp(MyRnd(1,10))*pi+y) - MyRnd(tempMin,tempMax)*cos(exp(MyRnd(1,10))*pi*y) )); %right (Satan) boundary temperature
TB=@(t,x) SetBoundaries(tempMin,tempMax,( MyRnd(tempMin,tempMax*2)*sin(exp(MyRnd(1,10))*pi*t/12) - MyRnd(tempMin,tempMax)*cos(exp(MyRnd(1,10))*pi+x) )); %top (Satan) boundary temperature
BB=@(t,x) SetBoundaries(tempMin,tempMax,( MyRnd(tempMin,tempMax)*sin(exp(MyRnd(1,10))*pi+x) - MyRnd(tempMin,tempMax)*cos(exp(MyRnd(1,10))*pi-x) )); %bottom (Satan) boundary temperature

% Controllers for the script
showSimulation=true; %when set to false the simulation is much faster
saveAnimation=true; %when true the showSimulation is overwriten to true and a gif file is created
saveEveryStep=false; %when set to false the RAM is saved and simulation might be faster
PostProcTempScales=linspace(tempMin,tempMax,300); % Cutting the temperature interval in 300 pieces to generate colour range
% File output name
gifFileName=material + "_" + tempMin + "-" + tempMax +"_from_" + InitTemp + ".gif"; % Having the title corresponding to the chosen material and temperatures
%% MAIN BODY
if satan == 666
    DivGrad=(1/(dx^2))*[0.5 1 0.5;1 -6 1;0.5 1 0.5];
    TempDiffCoef=lambda/(rho*cp); %W/(mK)

    if saveAnimation
        showSimulation=true;
    end

    %create grid
    x=0:dx:gridsize;
    y=0:dy:gridsize;
    [X,Y]=meshgrid(x,y);

    %initialise temperature at InitTemp
    T(:,:,1)=zeros(size(X))+InitTemp;

    %create figure for the plot
    fig=figure;
    set(fig,'units','normalized','OuterPosition',[0 0 0.5 0.9]);
    [~,h]=contourf(X,Y,T(:,:,1),PostProcTempScales);
    set(h,'LineColor','none')
    axis equal
    title('time: 0 seconds' )
    colorbar
    caxis([PostProcTempScales(1) PostProcTempScales(end)])
    xlim([0 x(end)])
    ylim([0 y(end)])
    colormap(jet)

    %loop stuff 
    step=1;
    t=0;
    max_step=ceil(tspan/dt);
    for i=1:max_step
        %calcualtion of next time step
        T(:,1,step)=LB(t,y);
        T(:,end,step)=RB(t,y);
        T(end,:,step)=TB(t,x);
        T(1,:,step)=BB(t,x);
        T(:,:,step+saveEveryStep)=T(:,:,step)+dt*TempDiffCoef*ApllyOperator(T(:,:,step),DivGrad);
        t=t+dt;

        %information drops during simulation + visualisation
        if mod(i,dispEveryIthStep)==0 || i==max_step
            clc
            disp('Good luck replicating my gif!')
            disp(['simulation time: ' char(num2str(t)) ' seconds' ])
            disp(['simulation step: ' char(num2str(i))])
            disp(['simulation progress: ' char(num2str(100*i/ceil(tspan/dt))) ' %'])
            disp(['Material: ' material])
            disp(['Temperature span: ' char(num2str(tempMin)) '-' char(num2str(tempMax))])
            disp(['Initial temperature: ' char(num2str(InitTemp))])
            %visualisation
            if showSimulation || i==max_step
                h.ZData=T(:,:,step+saveEveryStep);
                title(['Material: ' material '. Time: ' char(num2str(t)) ' seconds'])
                pause(0.001)

                %save the animation
                if saveAnimation
                    frame = getframe(fig);
                    im = frame2im(frame);
                    [imind,cm] = rgb2ind(im,256);
                    if i == dispEveryIthStep
                        imwrite(imind,cm,gifFileName,'gif','DelayTime',0.04, 'Loopcount',inf);
                    else
                        imwrite(imind,cm,gifFileName,'gif','DelayTime',0.04,'WriteMode','append');
                    end
                end

            end
        end
        step=step+saveEveryStep;
    end

    %calculate heat flows a draw them
    hold on
    [dTdx,dTdy]=gradient(T);
    qx=-lambda*dTdx;
    qy=-lambda*dTdy;
    q=quiver(x,y,qx,qy);
    q.AutoScaleFactor=4;
    
else
    disp("Looks like the script doesn't work!")
    
end

%% HELPER FUNCTIONS
%%
function R=ApllyOperator(Field,Operator)
    R=zeros(size(Field));
    for i=2:size(Field,1)-1
        for j=2:size(Field,2)-1
            R(i,j)=sum(sum(Field(i-1:i+1,j-1:j+1).*Operator));
        end
    end

end

%%
% Function returning random integer in the specified range
% @param Min: minimum value in the range
% @param Max: maximum value in the range
% @return: integer in range from Min to Max (inclusive)
function R=MyRnd(Min,Max)
    R=Min+floor(rand*(Max-Min+1));
end

%%
% Function keeping the output value of inputted enexpectable 
% function in the specified boundaries
% @param MinVal: minimum output value
% @param MaxVal: maximum output value
% @param Func: the function we want to limit
% @return: the same function that was inputted with boundaries on its output
function R=SetBoundaries(MinVal,MaxVal,Func)
    R=max(MinVal,min(MaxVal,Func));
end
