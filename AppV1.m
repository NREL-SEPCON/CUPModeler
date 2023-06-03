classdef AppV1 < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                      matlab.ui.Figure
        TabGroup                      matlab.ui.container.TabGroup
        ColumnPropertiesLabel         matlab.ui.control.Label
        CompoundListLabel             matlab.ui.control.Label
        VolumeTimeSwitch              matlab.ui.control.Switch
        StationaryPhaseSwitch         matlab.ui.control.Switch
        removeCompound                matlab.ui.control.Button
        addCompound                   matlab.ui.control.Button
        compoundList                  matlab.ui.control.Table
        yieldAndPurityClassic         matlab.ui.control.Table
        yieldAndPurityExtrusion       matlab.ui.control.Table
        yieldAndPurityDual            matlab.ui.control.Table
        ExtrusionLinesCheckbox        matlab.ui.control.CheckBox
        ExtrusionLinesLabelsCheckbox  matlab.ui.control.CheckBox
        DualLinesCheckbox             matlab.ui.control.CheckBox
        DualLinesLabelsCheckbox       matlab.ui.control.CheckBox
        MultiLinesCheckbox            matlab.ui.control.CheckBox
        MultiLinesLabelsCheckbox      matlab.ui.control.CheckBox
        ElutionDuration               matlab.ui.control.NumericEditField
        ElutionDurationLabel          matlab.ui.control.Label
        ColumnDeadVolume              matlab.ui.control.NumericEditField
        ColumnDeadVolumeLabel         matlab.ui.control.Label
        ColumnDeadVolumeLabelUnits    matlab.ui.control.Label
        ColumnEfficiencyN             matlab.ui.control.NumericEditField
        ColumnEfficiencyNLabel        matlab.ui.control.Label
        InjectionVolume               matlab.ui.control.NumericEditField
        InjectionVolumeLabel          matlab.ui.control.Label
        InjectionVolumeLabelUnits     matlab.ui.control.Label
        StationaryPhaseRetention      matlab.ui.control.NumericEditField
        StationaryPhaseRetentionLabel matlab.ui.control.Label
        SfCoefficientA                matlab.ui.control.NumericEditField
        SfCoefficientALabel           matlab.ui.control.Label
        SfCoefficientB                matlab.ui.control.NumericEditField
        SfCoefficientBLabel           matlab.ui.control.Label
        ColumnVolume                  matlab.ui.control.NumericEditField
        ColumnVolumeLabel             matlab.ui.control.Label
        ColumnVolumeLabelUnits        matlab.ui.control.Label
        FlowRate                      matlab.ui.control.NumericEditField
        FlowRateLabel                 matlab.ui.control.Label
        FlowRateLabelUnits            matlab.ui.control.Label
        ElutionDurationLabelUnits     matlab.ui.control.Label
        ClassicElutionTab             matlab.ui.container.Tab
        ExportButtonClassic           matlab.ui.control.Button
        PlotButtonClassic             matlab.ui.control.Button
        UIAxesClassic                 matlab.ui.control.UIAxes
        ElutionExtrusionTab           matlab.ui.container.Tab
        ExtrusionDurationLabelUnits   matlab.ui.control.Label
        ExtrusionDuration             matlab.ui.control.NumericEditField
        ExtrusionDurationLabel        matlab.ui.control.Label
        ExportButtonExtrusion         matlab.ui.control.Button
        PlotButtonExtrusion           matlab.ui.control.Button
        UIAxesExtrusion               matlab.ui.control.UIAxes
        dualModeTab                   matlab.ui.container.Tab
        DualDurationLabelUnits        matlab.ui.control.Label
        DualDuration                  matlab.ui.control.NumericEditField
        DualDurationLabel             matlab.ui.control.Label
        ExportButtonDual              matlab.ui.control.Button
        PlotButtonDual                matlab.ui.control.Button
        UIAxesDual                    matlab.ui.control.UIAxes
        MultipleDualModeTab           matlab.ui.container.Tab
        ExportButtonMulti             matlab.ui.control.Button
        PlotButtonMulti               matlab.ui.control.Button
        SwitchTimeListLabel           matlab.ui.control.Label
        SwitchTimeList                matlab.ui.control.Table
        removeCycle                   matlab.ui.control.Button
        addCycle                      matlab.ui.control.Button
        UIAxesMultiPosition           matlab.ui.control.UIAxes
        UIAxesMulti                   matlab.ui.control.UIAxes
        Info                          matlab.ui.container.Tab
        InfoTitle                     matlab.ui.control.Label
        InfoVersion                   matlab.ui.control.Label
        InfoCitation                  matlab.ui.control.Label
        InfoCredits                   matlab.ui.control.Label
    end
    
    % Callbacks that handle component events
    methods (Access = private)

        function toggleVolumeTime(app)
            F = app.FlowRate.Value;

            if string(app.VolumeTimeSwitch.Value) == 'Volume'
                app.ElutionDurationLabel.Text = 'Elution Volume';
                app.ElutionDurationLabelUnits.Text = 'mL';

                app.ExtrusionDurationLabel.Text = 'Extrusion Volume';
                app.ExtrusionDurationLabelUnits.Text = 'mL';

                app.DualDurationLabel.Text = 'Dual Mode Volume';
                app.DualDurationLabelUnits.Text = 'mL';

                app.UIAxesClassic.XLabel.String = 'Elution Volume (mL)';
                app.UIAxesExtrusion.XLabel.String = 'Elution Volume (mL)';
                app.UIAxesDual.XLabel.String = 'Elution Volume (mL)';
                app.UIAxesMulti.XLabel.String = 'Elution Volume (mL)';
                app.UIAxesMultiPosition.XLabel.String = 'Elution Volume (mL)';

                app.SwitchTimeList.ColumnName{2} = 'mL';
                app.SwitchTimeListLabel.Text = 'Switch Volumes';

                app.ElutionDuration.Value = app.ElutionDuration.Value*F;
                app.ExtrusionDuration.Value = app.ExtrusionDuration.Value*F;
                app.DualDuration.Value = app.DualDuration.Value*F;

                for i = 1:height(app.SwitchTimeList.Data)
                    app.SwitchTimeList.Data(i,2) = {cell2mat(app.SwitchTimeList.Data(i,2))*F};
                end

                CUPPrediction(app);

            elseif string(app.VolumeTimeSwitch.Value) == 'Time'
                app.ElutionDurationLabel.Text = 'Elution Duration';
                app.ElutionDurationLabelUnits.Text = 'min';
                
                app.ExtrusionDurationLabel.Text = 'Extrusion Duration';
                app.ExtrusionDurationLabelUnits.Text = 'min';
                
                app.DualDurationLabel.Text = 'Dual Mode Duration';
                app.DualDurationLabelUnits.Text = 'min';
                
                app.UIAxesClassic.XLabel.String = 'Elution Duration (min)';
                app.UIAxesExtrusion.XLabel.String = 'Elution Duration (min)';
                app.UIAxesDual.XLabel.String = 'Elution Duration (min)';
                app.UIAxesMulti.XLabel.String = 'Elution Duration (min)';
                app.UIAxesMultiPosition.XLabel.String = 'Elution Duration (min)';
                
                app.SwitchTimeList.ColumnName{2} = 'min';
                app.SwitchTimeListLabel.Text = 'Switch Times';

                app.ElutionDuration.Value = app.ElutionDuration.Value/F;
                app.ExtrusionDuration.Value = app.ExtrusionDuration.Value/F;
                app.DualDuration.Value = app.DualDuration.Value/F;

                for i = 1:height(app.SwitchTimeList.Data)
                    app.SwitchTimeList.Data(i,2) = {cell2mat(app.SwitchTimeList.Data(i,2))/F};
                end

                CUPPrediction(app);
            end
        end
        

        function toggleStationary(app)
            if string(app.StationaryPhaseSwitch.Value) == 'Set Value'
                
                delete(app.SfCoefficientA);
                delete(app.SfCoefficientALabel);
                delete(app.SfCoefficientB);
                delete(app.SfCoefficientBLabel);

                % Create StationaryPhaseRetentionLabel
                app.StationaryPhaseRetentionLabel = uilabel(app.UIFigure);
                app.StationaryPhaseRetentionLabel.HorizontalAlignment = 'center';
                app.StationaryPhaseRetentionLabel.WordWrap = 'on';
                app.StationaryPhaseRetentionLabel.Position = [202 316 96 57];
                app.StationaryPhaseRetentionLabel.Text = 'Stationary Phase Retention';
                
                % Create StationaryPhaseRetention
                app.StationaryPhaseRetention = uieditfield(app.UIFigure, 'numeric');
                app.StationaryPhaseRetention.LowerLimitInclusive = 'off';
                app.StationaryPhaseRetention.UpperLimitInclusive = 'off';
                app.StationaryPhaseRetention.Limits = [0 1];
                app.StationaryPhaseRetention.Position = [300 333 51 22];
                app.StationaryPhaseRetention.Value = 0.75;

            elseif string(app.StationaryPhaseSwitch.Value) == 'Coefficients'

                delete(app.StationaryPhaseRetention);
                delete(app.StationaryPhaseRetentionLabel);

                app.SfCoefficientALabel = uilabel(app.UIFigure);
                app.SfCoefficientALabel.HorizontalAlignment = 'center';
                app.SfCoefficientALabel.WordWrap = 'on';
                app.SfCoefficientALabel.Position = [200 316 20 57];
                app.SfCoefficientALabel.Text = 'A';

                app.SfCoefficientA = uieditfield(app.UIFigure, 'numeric');
                app.SfCoefficientA.LowerLimitInclusive = 'off';
                app.SfCoefficientA.UpperLimitInclusive = 'off';
                app.SfCoefficientA.Limits = [0 1];
                app.SfCoefficientA.Position = [220 333 51 22];
                app.SfCoefficientA.Value = 0.9821;

                app.SfCoefficientBLabel = uilabel(app.UIFigure);
                app.SfCoefficientBLabel.HorizontalAlignment = 'center';
                app.SfCoefficientBLabel.WordWrap = 'on';
                app.SfCoefficientBLabel.Position = [280 316 20 57];
                app.SfCoefficientBLabel.Text = 'B';

                app.SfCoefficientB = uieditfield(app.UIFigure, 'numeric');
                app.SfCoefficientB.LowerLimitInclusive = 'off';
                app.SfCoefficientB.UpperLimitInclusive = 'off';
                app.SfCoefficientB.Limits = [0 1];
                app.SfCoefficientB.Position = [300 333 51 22];
                app.SfCoefficientB.Value = 0.1426;
            end
        end


        function addCompoundButtonPushed(app)
            newRowPosition = height(app.compoundList.Data)+1;
            newRowPositionString = num2str(newRowPosition);
            compoundName = {char(append('Compound',' ',newRowPositionString))};
            app.compoundList.Data(end+1,:) = [compoundName,1,1,0];
        end


        function removeCompoundButtonPushed(app)
            if height(app.compoundList.Data) > 1
            app.compoundList.Data(end,:) = []; % Delete Last Row
            end
        end


        function addCycleButtonPushed(app)
            newRowPosition = height(app.SwitchTimeList.Data)+1;
            newRowPositionString = num2str(newRowPosition);
            cycleName = {char(append('Cycle',' ',newRowPositionString))};
            app.SwitchTimeList.Data(end+1,:) = [cycleName,5];
        end


        function removeCycleButtonPushed(app)
            app.SwitchTimeList.Data(end,:) = []; % Delete Last Row
        end


        function [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution elutionTime] = computeValues(app)
            F = app.FlowRate.Value;
            if string(app.StationaryPhaseSwitch.Value) == 'Set Value'
                Sf = app.StationaryPhaseRetention.Value;
            elseif string(app.StationaryPhaseSwitch.Value) == "Coefficients"
                Sf = app.SfCoefficientA.Value - app.SfCoefficientB.Value*F;
            end
            KD = cell2mat(app.compoundList.Data(:,2));
            Vc = app.ColumnVolume.Value;
            Ncup = app.ColumnEfficiencyN.Value;
            C0 = cell2mat(app.compoundList.Data(:,3));
            Vinj = app.InjectionVolume.Value;
            elutionTime = app.ElutionDuration.Value;

            Vcup = Vc/Ncup;
            Vmcup = Vcup*(1-Sf);
            
            if string(app.VolumeTimeSwitch.Value) == 'Volume'
                dtElution = Vmcup;
                Vcm = elutionTime;
            elseif string(app.VolumeTimeSwitch.Value) == 'Time'
                Vcm = F*elutionTime;
                dtElution = Vmcup/F;
            end
        end

        function addPuritiesToTable(app, Purity)
            for i = 1:length(Purity)
                app.compoundList.Data(i,4) = {Purity(i)};
            end
        end


       function CUPPrediction(app)
            [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution elutionTime] = computeValues(app);

            [Vspan Cout X Y] = CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj);
            
            Nturn = Vspan/Vmcup;
            telute = (dtElution).*Nturn;

            identifier = string(gcbo().Tag);

            if identifier == 'Switch'
                identifier = string(app.TabGroup.SelectedTab.Tag);
            end

            if contains(identifier, 'Classic')
                plot(app.UIAxesClassic, telute, Cout, 'linewidth', 2.0);
                app.UIAxesClassic.XLim = [0 elutionTime];
            end
            
            if contains(identifier, 'Extrusion')
                [Vspan, Cout, Xtot, Ytot, Vbc] = EECCC_V8(KD, Vc, Sf, X, Y);

                if string(app.VolumeTimeSwitch.Value) == 'Volume'
                    F = 1;
                end
                
                telute = Vspan/F;
                columnVolumeExtrudedTime = Vbc(1)/F;
                sweepTime = Vbc(2)/F;
                extrusionTime = app.ExtrusionDuration.Value + elutionTime;

                sweepStartLabel = '';
                sweepEndLabel = '';

                if app.ExtrusionLinesLabelsCheckbox.Value
                    LinesLabelsUnits = ' min';
                    if string(app.VolumeTimeSwitch.Value) == 'Volume'
                        LinesLabelsUnits = ' mL';
                    end
                    sweepStartLabel = sprintf(['Sweep Start\n']) + string(elutionTime) + LinesLabelsUnits;
                    sweepEndLabel = sprintf(['Sweep End\n']) + string(round(sweepTime, 2)) + LinesLabelsUnits;
                end

                plot(app.UIAxesExtrusion, telute, Cout, 'linewidth', 2.0);

                if app.ExtrusionLinesCheckbox.Value
                    xline(app.UIAxesExtrusion, elutionTime, '-.r', sweepStartLabel);
                    xline(app.UIAxesExtrusion, columnVolumeExtrudedTime, '-.r');
                    xline(app.UIAxesExtrusion, sweepTime, '--b', sweepEndLabel);
                end

                app.UIAxesExtrusion.XLim = [0 extrusionTime];
            end
            
            if contains(identifier, 'Dual')
                Vdm = app.DualDuration.Value;
                dualTime = elutionTime + Vdm;
  
                if string(app.VolumeTimeSwitch.Value) == 'Time'
                    Vdm = Vdm*F;
                    dualTime = elutionTime*F + Vdm;
                end
                
                [Vspan Cout, X, Y] = DualV2(KD, Vc, Sf, F, Vdm, X, Y);
                
                if string(app.VolumeTimeSwitch.Value) == 'Volume'
                    F = 1;
                end
                
                dualSwitchLabel = '';
                
                if app.DualLinesLabelsCheckbox.Value
                    LinesLabelsUnits = ' min';
                    if string(app.VolumeTimeSwitch.Value) == 'Volume'
                        LinesLabelsUnits = ' mL';
                    end
                    dualSwitchLabel = string(round(Vcm/F, 2)) + LinesLabelsUnits;
                end

                telute = Vspan/F;
                stationaryPhaseVolume = dualTime/F;

                plot(app.UIAxesDual, telute, Cout, 'linewidth', 2.0);

                if app.DualLinesCheckbox.Value
                    xline(app.UIAxesDual, Vcm/F, '-.r', dualSwitchLabel);
                    xline(app.UIAxesDual, stationaryPhaseVolume, '--b');
                end

                app.UIAxesDual.XLim = [0 stationaryPhaseVolume];
            end

            if contains(identifier, 'Multi')
                if string(app.VolumeTimeSwitch.Value) == 'Volume'
                    F = 1;
                end

                Vcm = [Vcm; cell2mat(app.SwitchTimeList.Data(:,2))*F];

                [Vtot, Ctot, Xtot, Ytot, Tcut, VswDM, VswCM] = MDMV2(Sf, KD, Vc, Ncup, C0, Vinj, Vcm);
                %[Vx Vy] = MDMrT(Sf, KD, Vc, F, Vcm);

                if string(app.VolumeTimeSwitch.Value) == 'Time'
                    Vtot = Vtot/F;
                    VswCM = VswCM/F;
                    VswDM = VswDM/F;
                end

                VswCMText = '';
                VswDMText = '';
                
                if app.MultiLinesLabelsCheckbox.Value
                    LinesLabelsUnits = ' min';
                    if string(app.VolumeTimeSwitch.Value) == 'Volume'
                        LinesLabelsUnits = ' mL';
                    end
                    VswCMText = string(round(VswCM, 2)) + LinesLabelsUnits;
                    VswDMText = string(round(VswDM, 2)) + LinesLabelsUnits;
                end

                plot(app.UIAxesMulti, Vtot, Ctot, 'linewidth', 2.0);
                
                app.UIAxesMulti.XLim = [0 Vtot(end)];
                app.UIAxesMulti.YLim = [0 Inf];
                
                xMatrix = sum(Xtot, 3);
                yAxis = [1:size(xMatrix,1)].*(1/size(xMatrix,1));
                
                contourSpacing = linspace(0.005, .1, 30);
                
                contourf(app.UIAxesMultiPosition, Vtot, yAxis, xMatrix, contourSpacing, 'linecolor', 'none');
                
                if app.MultiLinesCheckbox.Value
                    xline(app.UIAxesMulti, VswDM, '-.r', VswDMText);
                    xline(app.UIAxesMulti, VswCM, '-.b', VswCMText);
                    xline(app.UIAxesMultiPosition, VswDM, '-.r', VswDMText);
                    xline(app.UIAxesMultiPosition, VswCM, '-.b', VswCMText);
                end

                app.UIAxesMultiPosition.XLim = [0 Vtot(end)];
                app.UIAxesMultiPosition.YLim = [0 1];

                telute = Vtot;
                Cout = Ctot;

            end


            if contains(identifier, 'Export')
                ExportIdentifier = erase(identifier, 'Export');

                filename = [ExportIdentifier + ' ' + app.VolumeTimeSwitch.Value + ' export ' + string(datetime)];
                individualCurves = array2table(Cout.', 'VariableNames', app.compoundList.Data(:,1));
                compiledData = [array2table(telute.'), individualCurves];

                writetable(compiledData, [filename + '.xlsx']);

                exportedPlot = sprintf('app.UIAxes' + ExportIdentifier)
                exportgraphics(eval(exportedPlot), [filename + '.pdf'], 'ContentType', 'vector');
            end

            %[Purity, integralRanges] = purityCalculation(telute, Cout);
            %app.addPuritiesToTable(Purity);

        end
    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            
            % Create UIFigure and hide until all components are created
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.Position = [40 250 1440 500];
            app.UIFigure.Name = 'CUP Modeler';
            
            % Create TabGroup
            app.TabGroup = uitabgroup(app.UIFigure);
            app.TabGroup.Position = [725 0 717 500];

            % Create ElutionDurationLabelUnits
            app.ElutionDurationLabelUnits = uilabel(app.UIFigure);
            app.ElutionDurationLabelUnits.HorizontalAlignment = 'center';
            app.ElutionDurationLabelUnits.WordWrap = 'on';
            app.ElutionDurationLabelUnits.Position = [487 406 34 22];
            app.ElutionDurationLabelUnits.Text = 'min';
            
            % Create FlowRateLabelUnits
            app.FlowRateLabelUnits = uilabel(app.UIFigure);
            app.FlowRateLabelUnits.HorizontalAlignment = 'right';
            app.FlowRateLabelUnits.Position = [123 406 46 22];
            app.FlowRateLabelUnits.Text = 'mL/min';
            
            % Create FlowRateLabel
            app.FlowRateLabel = uilabel(app.UIFigure);
            app.FlowRateLabel.HorizontalAlignment = 'center';
            app.FlowRateLabel.WordWrap = 'on';
            app.FlowRateLabel.Position = [26 403 48 28];
            app.FlowRateLabel.Text = 'Flow Rate';
            
            % Create FlowRate
            app.FlowRate = uieditfield(app.UIFigure, 'numeric');
            app.FlowRate.LowerLimitInclusive = 'off';
            app.FlowRate.Limits = [0 Inf];
            app.FlowRate.RoundFractionalValues = 'off';
            app.FlowRate.Position = [73 406 51 22];
            app.FlowRate.Value = 5;
            
            % Create ColumnVolumeLabelUnits
            app.ColumnVolumeLabelUnits = uilabel(app.UIFigure);
            app.ColumnVolumeLabelUnits.HorizontalAlignment = 'right';
            app.ColumnVolumeLabelUnits.Position = [319 406 25 22];
            app.ColumnVolumeLabelUnits.Text = 'mL';
            
            % Create ColumnVolumeLabel
            app.ColumnVolumeLabel = uilabel(app.UIFigure);
            app.ColumnVolumeLabel.HorizontalAlignment = 'center';
            app.ColumnVolumeLabel.WordWrap = 'on';
            app.ColumnVolumeLabel.Position = [213 401 65 33];
            app.ColumnVolumeLabel.Text = 'Column Volume';
            
            % Create ColumnVolume
            app.ColumnVolume = uieditfield(app.UIFigure, 'numeric');
            app.ColumnVolume.LowerLimitInclusive = 'off';
            app.ColumnVolume.Limits = [0 Inf];
            app.ColumnVolume.RoundFractionalValues = 'off';
            app.ColumnVolume.Position = [277 406 44 22];
            app.ColumnVolume.Value = 81;
            
            % Create ElutionDurationLabel
            app.ElutionDurationLabel = uilabel(app.UIFigure);
            app.ElutionDurationLabel.HorizontalAlignment = 'center';
            app.ElutionDurationLabel.WordWrap = 'on';
            app.ElutionDurationLabel.Position = [378 403 55 30];
            app.ElutionDurationLabel.Text = 'Elution Duration';
            
            % Create ElutionDuration
            app.ElutionDuration = uieditfield(app.UIFigure, 'numeric');
            app.ElutionDuration.Position = [437 406 51 22];
            app.ElutionDuration.Value = 60;
            
            % Create InjectionVolumeLabelUnits
            app.InjectionVolumeLabelUnits = uilabel(app.UIFigure);
            app.InjectionVolumeLabelUnits.HorizontalAlignment = 'right';
            app.InjectionVolumeLabelUnits.Position = [656 406 25 22];
            app.InjectionVolumeLabelUnits.Text = 'mL';
            
            % Create InjectionVolumeLabel
            app.InjectionVolumeLabel = uilabel(app.UIFigure);
            app.InjectionVolumeLabel.HorizontalAlignment = 'center';
            app.InjectionVolumeLabel.WordWrap = 'on';
            app.InjectionVolumeLabel.Position = [550 403 65 30];
            app.InjectionVolumeLabel.Text = 'Injection Volume';
            
            % Create InjectionVolume
            app.InjectionVolume = uieditfield(app.UIFigure, 'numeric');
            app.InjectionVolume.LowerLimitInclusive = 'off';
            app.InjectionVolume.Limits = [0 Inf];
            app.InjectionVolume.Position = [614 406 44 22];
            app.InjectionVolume.Value = 1;
            
            % Create StationaryPhaseRetentionLabel
            app.StationaryPhaseRetentionLabel = uilabel(app.UIFigure);
            app.StationaryPhaseRetentionLabel.HorizontalAlignment = 'center';
            app.StationaryPhaseRetentionLabel.WordWrap = 'on';
            app.StationaryPhaseRetentionLabel.Position = [202 316 96 57];
            app.StationaryPhaseRetentionLabel.Text = 'Stationary Phase Retention';
            
            % Create StationaryPhaseRetention
            app.StationaryPhaseRetention = uieditfield(app.UIFigure, 'numeric');
            app.StationaryPhaseRetention.LowerLimitInclusive = 'off';
            app.StationaryPhaseRetention.UpperLimitInclusive = 'off';
            app.StationaryPhaseRetention.Limits = [0 1];
            app.StationaryPhaseRetention.Position = [300 333 51 22];
            app.StationaryPhaseRetention.Value = 0.75;

            % Create Switch
            app.StationaryPhaseSwitch = uiswitch(app.UIFigure, 'slider', 'ValueChangedFcn',@(src,event) toggleStationary(app));
            app.StationaryPhaseSwitch.Items = {'Set Value', 'Coefficients'};
            app.StationaryPhaseSwitch.Position = [70 338 45 20];
            app.StationaryPhaseSwitch.Value = 'Set Value';
            set(app.StationaryPhaseSwitch, 'Tooltip', 'Coefficients must be obtained from the literature for each solvent system. In this setting, Sf = A - (B x flowrate)')

            % Create ColumnDeadVolumeLabelUnits
            app.ColumnDeadVolumeLabelUnits = uilabel(app.UIFigure);
            app.ColumnDeadVolumeLabelUnits.HorizontalAlignment = 'center';
            app.ColumnDeadVolumeLabelUnits.WordWrap = 'on';
            app.ColumnDeadVolumeLabelUnits.Position = [677 338 24 14];
            app.ColumnDeadVolumeLabelUnits.Text = 'mL';
            
            % Create ColumnDeadVolumeLabel
            app.ColumnDeadVolumeLabel = uilabel(app.UIFigure);
            app.ColumnDeadVolumeLabel.HorizontalAlignment = 'center';
            app.ColumnDeadVolumeLabel.WordWrap = 'on';
            app.ColumnDeadVolumeLabel.Position = [530 328 89 34];
            app.ColumnDeadVolumeLabel.Text = 'Column Dead Volume';
            
            % Create ColumnDeadVolume
            app.ColumnDeadVolume = uieditfield(app.UIFigure, 'numeric');
            app.ColumnDeadVolume.Limits = [0 Inf];
            app.ColumnDeadVolume.Position = [628 334 44 22];
            
            % Create UITable
            initialRows = {'Compound 1' 1 1 0; 'Compound 2' 2 1 0};
            app.compoundList = uitable(app.UIFigure, ...
                "ColumnName",{'Compound'; 'KD'; 'Conc. (g/L)'; 'Purity (%)'}, ...
                "ColumnFormat",{'char' [] [] []}, ...
                "Data",initialRows);
            app.compoundList.RowName = {};
            tableStyle = uistyle("HorizontalAlignment","center");
            addStyle(app.compoundList, tableStyle);
            app.compoundList.ColumnSortable = true;
            app.compoundList.ColumnEditable = true;
            app.compoundList.Position = [73 12 585 255];

            % Create addCompound
            app.addCompound = uibutton(app.UIFigure,'ButtonPushedFcn',@(src,event) addCompoundButtonPushed(app));
            app.addCompound.Position = [27 242 25 25];
            app.addCompound.Text = '+';

            % Create removeCompound
            app.removeCompound = uibutton(app.UIFigure,'ButtonPushedFcn',@(src,event) removeCompoundButtonPushed(app));
            app.removeCompound.Position = [26 209 25 25];
            app.removeCompound.Text = '-';

            % Create CompoundListLabel
            app.CompoundListLabel = uilabel(app.UIFigure);
            app.CompoundListLabel.HorizontalAlignment = 'center';
            app.CompoundListLabel.FontSize = 18;
            app.CompoundListLabel.FontWeight = 'bold';
            app.CompoundListLabel.Position = [291 286 137 24];
            app.CompoundListLabel.Text = 'Compound List';

            % Create ColumnPropertiesLabel
            app.ColumnPropertiesLabel = uilabel(app.UIFigure);
            app.ColumnPropertiesLabel.HorizontalAlignment = 'center';
            app.ColumnPropertiesLabel.FontSize = 18;
            app.ColumnPropertiesLabel.FontWeight = 'bold';
            app.ColumnPropertiesLabel.Position = [276 460 166 24];
            app.ColumnPropertiesLabel.Text = 'Column Properties';

            % Create Switch
            app.VolumeTimeSwitch = uiswitch(app.UIFigure, 'slider', 'ValueChangedFcn',@(src,event) toggleVolumeTime(app));
            app.VolumeTimeSwitch.Items = {'Time', 'Volume'};
            app.VolumeTimeSwitch.Position = [420 338 45 20];
            app.VolumeTimeSwitch.Value = 'Time';
            app.VolumeTimeSwitch.Tag = 'Switch';

            % Create ClassicElutionTab
            app.ClassicElutionTab = uitab(app.TabGroup);
            app.ClassicElutionTab.Title = 'Classic Elution';
            app.ClassicElutionTab.Tag = 'ClassicPlot';

            % Create UIAxesClassic
            app.UIAxesClassic = uiaxes(app.ClassicElutionTab);
            xlabel(app.UIAxesClassic, 'Elution Time')
            ylabel(app.UIAxesClassic, 'Concentration')
            zlabel(app.UIAxesClassic, 'Z')
            app.UIAxesClassic.Position = [8 143 695 301];

            % Create PlotButtonClassic
            app.PlotButtonClassic = uibutton(app.ClassicElutionTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.PlotButtonClassic.Position = [297 445 68 23];
            app.PlotButtonClassic.Text = 'Plot';
            app.PlotButtonClassic.Tag = 'ClassicPlot';

            % Create ExportButtonClassic
            app.ExportButtonClassic = uibutton(app.ClassicElutionTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.ExportButtonClassic.Position = [372 445 68 23];
            app.ExportButtonClassic.Text = 'Export';
            app.ExportButtonClassic.Tag = 'ClassicExport';

            % Create ElutionExtrusionTab
            app.ElutionExtrusionTab = uitab(app.TabGroup);
            app.ElutionExtrusionTab.Title = 'Elution-Extrusion';
            app.ElutionExtrusionTab.Tag = 'ExtrusionPlot';

            % Create UIAxesExtrusion
            app.UIAxesExtrusion = uiaxes(app.ElutionExtrusionTab);
            xlabel(app.UIAxesExtrusion, 'Elution Time')
            ylabel(app.UIAxesExtrusion, 'Concentration')
            zlabel(app.UIAxesExtrusion, 'Z')
            app.UIAxesExtrusion.Position = [8 143 695 301];

            % Create PlotButton_3
            app.PlotButtonExtrusion = uibutton(app.ElutionExtrusionTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.PlotButtonExtrusion.Position = [297 445 68 23];
            app.PlotButtonExtrusion.Text = 'Plot';
            app.PlotButtonExtrusion.Tag = 'ExtrusionPlot';

            % Create ExportButtonExtrusion
            app.ExportButtonExtrusion = uibutton(app.ElutionExtrusionTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.ExportButtonExtrusion.Position = [372 445 68 23];
            app.ExportButtonExtrusion.Text = 'Export';
            app.ExportButtonExtrusion.Tag = 'ExtrusionExport';

            % Create ExtrusionDurationLabel
            app.ExtrusionDurationLabel = uilabel(app.ElutionExtrusionTab);
            app.ExtrusionDurationLabel.HorizontalAlignment = 'right';
            app.ExtrusionDurationLabel.Position = [49 445 104 22];
            app.ExtrusionDurationLabel.Text = 'Extrusion Duration';

            % Create ExtrusionDuration
            app.ExtrusionDuration = uieditfield(app.ElutionExtrusionTab, 'numeric');
            app.ExtrusionDuration.Position = [165 445 29 22];

            % Create ExtrusionDurationLabelUnits
            app.ExtrusionDurationLabelUnits = uilabel(app.ElutionExtrusionTab);
            app.ExtrusionDurationLabelUnits.HorizontalAlignment = 'center';
            app.ExtrusionDurationLabelUnits.Position = [200 445 29 22];
            app.ExtrusionDurationLabelUnits.Text = 'min';


            %Create ExtrusionLinesCheckbox
            app.ExtrusionLinesCheckbox = uicheckbox(app.ElutionExtrusionTab,...
                'Text', 'Lines?',...
                'Value', 1,...
                'Position', [550 450 102 15]);

            %Create ExtrusionLinesLabelsCheckbox
            app.ExtrusionLinesLabelsCheckbox = uicheckbox(app.ElutionExtrusionTab,...
                'Text', 'Labels?',...
                'Value', 1,...
                'Position', [610 450 102 15]);

            % Create dualModeTab
            app.dualModeTab = uitab(app.TabGroup);
            app.dualModeTab.Title = 'Dual Mode';
            app.dualModeTab.Tag = 'DualPlot';

            % Create UIAxesDual
            app.UIAxesDual = uiaxes(app.dualModeTab);
            xlabel(app.UIAxesDual, 'Elution Time')
            ylabel(app.UIAxesDual, 'Concentration')
            zlabel(app.UIAxesDual, 'Z')
            app.UIAxesDual.Position = [8 143 695 301];

            % Create PlotButton_3
            app.PlotButtonDual = uibutton(app.dualModeTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.PlotButtonDual.Position = [297 445 68 23];
            app.PlotButtonDual.Text = 'Plot';
            app.PlotButtonDual.Tag = 'DualPlot';

            % Create ExportButtDualDurationLabelonDual
            app.ExportButtonDual = uibutton(app.dualModeTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.ExportButtonDual.Position = [372 445 68 23];
            app.ExportButtonDual.Text = 'Export';
            app.ExportButtonDual.Tag = 'DualExport';

            % Create 
            app.DualDurationLabel = uilabel(app.dualModeTab);
            app.DualDurationLabel.HorizontalAlignment = 'right';
            app.DualDurationLabel.Position = [40 445 120 22];
            app.DualDurationLabel.Text = 'Dual Mode Duration';

            % Create DualDuration
            app.DualDuration = uieditfield(app.dualModeTab, 'numeric');
            app.DualDuration.Position = [165 445 29 22];

            % Create DualDurationLabelUnits
            app.DualDurationLabelUnits = uilabel(app.dualModeTab);
            app.DualDurationLabelUnits.HorizontalAlignment = 'center';
            app.DualDurationLabelUnits.Position = [200 445 29 22];
            app.DualDurationLabelUnits.Text = 'min';

            % Create yield and purity table for classic mode
            app.yieldAndPurityClassic = uitable(app.ClassicElutionTab);
            app.yieldAndPurityClassic.ColumnName = {'Compound'; 'Start'; 'End'; 'Yield'; 'Purity'};
            app.yieldAndPurityClassic.RowName = {};
            app.yieldAndPurityClassic.Position = [49 12 647 122];
            
            % Create yield and purity table for Elution Extrusion
            app.yieldAndPurityExtrusion = uitable(app.ElutionExtrusionTab);
            app.yieldAndPurityExtrusion.ColumnName = {'Compound'; 'Start'; 'End'; 'Yield'; 'Purity'};
            app.yieldAndPurityExtrusion.RowName = {};
            app.yieldAndPurityExtrusion.Position = [49 12 647 122];

            % Create yield and purity table for Dual Mode
            app.yieldAndPurityDual = uitable(app.dualModeTab);
            app.yieldAndPurityDual.ColumnName = {'Compound'; 'Start'; 'End'; 'Yield'; 'Purity'};
            app.yieldAndPurityDual.RowName = {};
            app.yieldAndPurityDual.Position = [49 12 647 122];

            %Create DualLinesCheckbox
            app.DualLinesCheckbox = uicheckbox(app.dualModeTab,...
                'Text', 'Lines?',...
                'Value', 1,...
                'Position', [550 450 102 15]);

            %Create DualLinesLabelsCheckbox
            app.DualLinesLabelsCheckbox = uicheckbox(app.dualModeTab,...
                'Text', 'Labels?',...
                'Value', 1,...
                'Position', [610 450 102 15]);

            % Create MultipleDualModeTab
            app.MultipleDualModeTab = uitab(app.TabGroup);
            app.MultipleDualModeTab.Title = 'Multiple Dual Mode';
            app.MultipleDualModeTab.Tag = 'MultiPlot';

            % Create UIAxesMulti
            app.UIAxesMulti = uiaxes(app.MultipleDualModeTab);
            xlabel(app.UIAxesMulti, 'Elution Time')
            ylabel(app.UIAxesMulti, 'Concentration')
            zlabel(app.UIAxesMulti, 'Z')
            app.UIAxesMulti.Position = [8 229 695 215];

            % Create UIAxesMultiPosition
            app.UIAxesMultiPosition = uiaxes(app.MultipleDualModeTab);
            xlabel(app.UIAxesMultiPosition, 'Elution Time')
            ylabel(app.UIAxesMultiPosition, 'Column Position')
            zlabel(app.UIAxesMultiPosition, 'Z')
            app.UIAxesMultiPosition.Position = [200 10 495 215];

            % Create PlotButton_4
            app.PlotButtonMulti = uibutton(app.MultipleDualModeTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.PlotButtonMulti.Position = [297 445 68 23];
            app.PlotButtonMulti.Text = 'Plot';
            app.PlotButtonMulti.Tag = 'MultiPlot';

            % Create ExportButtonMulti
            app.ExportButtonMulti = uibutton(app.MultipleDualModeTab, 'ButtonPushedFcn',@(src,event) CUPPrediction(app));
            app.ExportButtonMulti.Position = [372 445 68 23];
            app.ExportButtonMulti.Text = 'Export';
            app.ExportButtonMulti.Tag = 'MultiExport';

            % Create SwitchTimeLabel
            app.SwitchTimeListLabel = uilabel(app.MultipleDualModeTab);
            app.SwitchTimeListLabel.HorizontalAlignment = 'center';
            app.SwitchTimeListLabel.FontSize = 18;
            app.SwitchTimeListLabel.FontWeight = 'bold';
            app.SwitchTimeListLabel.Position = [48 210 137 24];
            app.SwitchTimeListLabel.Text = 'Switch Times';

            % Create UITable
            initialRows = {'Cycle 1' 10; 'Cycle 2' 5};
            app.SwitchTimeList = uitable(app.MultipleDualModeTab, ...
                "ColumnName",{'Iteration'; 'min'}, ...
                "ColumnFormat",{'char' []}, ...
                "ColumnWidth",{75 73}, ...
                "Data",initialRows);
            app.SwitchTimeList.RowName = {};
            addStyle(app.SwitchTimeList, tableStyle);
            app.SwitchTimeList.ColumnSortable = true;
            app.SwitchTimeList.ColumnEditable = true;
            app.SwitchTimeList.Position = [42 20 150 180];

            % Create addCycle
            app.addCycle = uibutton(app.MultipleDualModeTab,'ButtonPushedFcn',@(src,event) addCycleButtonPushed(app));
            app.addCycle.Position = [11 142 25 25];
            app.addCycle.Text = '+';

            % Create removeCycle
            app.removeCycle = uibutton(app.MultipleDualModeTab,'ButtonPushedFcn',@(src,event) removeCycleButtonPushed(app));
            app.removeCycle.Position = [11 109 25 25];
            app.removeCycle.Text = '-';

            % Create appInfoTab
            app.Info = uitab(app.TabGroup);
            app.Info.Title = 'App Info';

            %Create MultiLinesCheckbox
            app.MultiLinesCheckbox = uicheckbox(app.MultipleDualModeTab,...
                'Text', 'Lines?',...
                'Value', 1,...
                'Position', [550 450 102 15]);

            %Create MultiLinesLabelsCheckbox
            app.MultiLinesLabelsCheckbox = uicheckbox(app.MultipleDualModeTab,...
                'Text', 'Labels?',...
                'Value', 1,...
                'Position', [610 450 102 15]);

            % Create ColumnEfficiencyNLabel
            app.ColumnEfficiencyNLabel = uilabel(app.Info);
            app.ColumnEfficiencyNLabel.HorizontalAlignment = 'center';
            app.ColumnEfficiencyNLabel.WordWrap = 'on';
            app.ColumnEfficiencyNLabel.Position = [73 501 91 28];
            app.ColumnEfficiencyNLabel.Text = 'Column Efficiency (N)';
            
            % Create ColumnEfficiencyN
            app.ColumnEfficiencyN = uieditfield(app.Info, 'numeric');
            app.ColumnEfficiencyN.UpperLimitInclusive = 'off';
            app.ColumnEfficiencyN.Limits = [1 Inf];
            app.ColumnEfficiencyN.Position = [78 504 51 22];
            app.ColumnEfficiencyN.Value = 400;

            app.InfoTitle = uilabel(app.Info);
            app.InfoTitle.HorizontalAlignment = 'center';
            app.InfoTitle.FontSize = 24;
            app.InfoTitle.FontWeight = 'bold';
            app.InfoTitle.Position = [140 320 500 50];
            app.InfoTitle.Text = 'CUP Modeler (Temporary Name)';

            app.InfoVersion = uilabel(app.Info);
            app.InfoVersion.HorizontalAlignment = 'center';
            app.InfoVersion.FontSize = 18;
            app.InfoVersion.Position = [140 290 500 50];
            app.InfoVersion.Text = 'Version 0.1 alpha';

            app.InfoCitation = uilabel(app.Info);
            app.InfoCitation.HorizontalAlignment = 'center';
            app.InfoCitation.FontSize = 12;
            app.InfoCitation.Position = [140 270 500 50];
            app.InfoCitation.Text = 'To learn more, check out <insert citation details here>';

            app.InfoCredits = uilabel(app.Info);
            app.InfoCredits.HorizontalAlignment = 'center';
            app.InfoCredits.FontSize = 12;
            app.InfoCredits.Position = [140 250 500 50];
            app.InfoCredits.Text = 'Mathematical Modeling by Hoon Choi, Interface by Manar Alherech';
            
            % Show the figure after all components are created
            app.UIFigure.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = AppV1

            % Create UIFigure and components
            createComponents(app)

            % Register the app with App Designer
            registerApp(app, app.UIFigure)

            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)

            % Delete UIFigure when app is deleted
            delete(app.UIFigure)
        end
    end
end