classdef AppV1 < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                      matlab.ui.Figure
        TabGroup                      matlab.ui.container.TabGroup
        ExperimentDetailsTab          matlab.ui.container.Tab
        ColumnPropertiesLabel         matlab.ui.control.Label
        CompoundListLabel             matlab.ui.control.Label
        removeCompound                matlab.ui.control.Button
        addCompound                   matlab.ui.control.Button
        UITable                       matlab.ui.control.Table
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
        StationaryPhaseRetentionLabel  matlab.ui.control.Label
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
        MultipleDualModeTab           matlab.ui.container.Tab
        CycleDurations                matlab.ui.control.EditField
        CycleDurationsLabel           matlab.ui.control.Label
        ExportButtonMulti             matlab.ui.control.Button
        PlotButtonMulti               matlab.ui.control.Button
        UIAxesMultiPosition           matlab.ui.control.UIAxes
        UIAxesMulti                   matlab.ui.control.UIAxes
    end

    % Callbacks that handle component events
    methods (Access = private)

        % Callback function: not associated with a component
        function addCompoundButtonPushed(app)
            newRowPosition = height(app.UITable.Data)+1;
            newRowPositionString = num2str(newRowPosition);
            compoundName = {char(append('Compound',' ',newRowPositionString))};
            app.UITable.Data(end+1,:) = [compoundName,1,1,1];
        end

        % Callback function: not associated with a component
        function removeCompoundButtonPushed(app)
            %get(app.UITable.Data, 'KD')
            if height(app.UITable.Data) > 2
            app.UITable.Data(end,:) = []; % Delete Last Row
            end
        end

        function [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution] = computeValues(app)
            F = app.FlowRate.Value;
            Sf = app.StationaryPhaseRetention.Value;
            KD = cell2mat(app.UITable.Data(:,2));
            Vc = app.ColumnVolume.Value;
            Ncup = app.ColumnEfficiencyN.Value;
            C0 = cell2mat(app.UITable.Data(:,3));
            Vinj = app.InjectionVolume.Value;

            Vcm = Vc*(1-Sf+Sf*KD(end))*1.5;
            Vcup = Vc/Ncup;
            Vmcup = Vcup*(1-Sf);
            dtElution = Vmcup/F;
        end

       function plotClassicalPrediction(app)

            [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution] = computeValues(app);

            [Vspan Cout X Y] = CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj);

            Nturn = Vspan/Vmcup;
            telute = (dtElution).*Nturn;

            plot(app.UIAxesClassic, telute, Cout);
            %main function here for plotting
        end

        function plotExtrusionPrediction(app)

            [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution] = computeValues(app);

            [Vspan Cout X Y] = CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj);
            Xcm = X;
            Ycm = Y;
            [Vspan2, Cout, Xtot, Ytot] = EECCC_V7(KD, Vc, Sf, Xcm, Ycm);

            Nturn = Vspan2/Vmcup;
            telute = (dtElution).*Nturn;

            plot(app.UIAxesExtrusion, telute, Cout);
        end

        function exportPlotExcel(app)

            [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution] = computeValues(app);

            [Vspan Cout X Y] = CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj);

            Nturn = Vspan/Vmcup;
            telute = (dtElution).*Nturn;

            filename = 'export.xlsx';
            individualCurves = array2table(Cout.', 'VariableNames', app.UITable.Data(:,1));
            compiledData = [array2table(telute.'), individualCurves];

            writetable(compiledData, filename);
        end

    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            
            % Create UIFigure and hide until all components are created
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.Position = [100 100 716 510];
            app.UIFigure.Name = 'MATLAB App';
            
            % Create TabGroup
            app.TabGroup = uitabgroup(app.UIFigure);
            app.TabGroup.Position = [0 1 717 511];
            
            % Create ExperimentDetailsTab
            app.ExperimentDetailsTab = uitab(app.TabGroup);
            app.ExperimentDetailsTab.Title = 'Experiment Details';
            % Create ElutionDurationLabelUnits
            app.ElutionDurationLabelUnits = uilabel(app.ExperimentDetailsTab);
            app.ElutionDurationLabelUnits.HorizontalAlignment = 'center';
            app.ElutionDurationLabelUnits.WordWrap = 'on';
            app.ElutionDurationLabelUnits.Position = [487 406 34 22];
            app.ElutionDurationLabelUnits.Text = 'min';
            
            % Create FlowRateLabelUnits
            app.FlowRateLabelUnits = uilabel(app.ExperimentDetailsTab);
            app.FlowRateLabelUnits.HorizontalAlignment = 'right';
            app.FlowRateLabelUnits.Position = [123 406 46 22];
            app.FlowRateLabelUnits.Text = 'mL/min';
            
            % Create FlowRateLabel
            app.FlowRateLabel = uilabel(app.ExperimentDetailsTab);
            app.FlowRateLabel.HorizontalAlignment = 'center';
            app.FlowRateLabel.WordWrap = 'on';
            app.FlowRateLabel.Position = [26 403 48 28];
            app.FlowRateLabel.Text = 'Flow Rate';
            
            % Create FlowRate
            app.FlowRate = uieditfield(app.ExperimentDetailsTab, 'numeric');
            app.FlowRate.LowerLimitInclusive = 'off';
            app.FlowRate.Limits = [0 Inf];
            app.FlowRate.RoundFractionalValues = 'on';
            app.FlowRate.Position = [73 406 51 22];
            app.FlowRate.Value = 1;
            
            % Create ColumnVolumeLabelUnits
            app.ColumnVolumeLabelUnits = uilabel(app.ExperimentDetailsTab);
            app.ColumnVolumeLabelUnits.HorizontalAlignment = 'right';
            app.ColumnVolumeLabelUnits.Position = [319 406 25 22];
            app.ColumnVolumeLabelUnits.Text = 'mL';
            
            % Create ColumnVolumeLabel
            app.ColumnVolumeLabel = uilabel(app.ExperimentDetailsTab);
            app.ColumnVolumeLabel.HorizontalAlignment = 'center';
            app.ColumnVolumeLabel.WordWrap = 'on';
            app.ColumnVolumeLabel.Position = [213 401 65 33];
            app.ColumnVolumeLabel.Text = 'Column Volume';
            
            % Create ColumnVolume
            app.ColumnVolume = uieditfield(app.ExperimentDetailsTab, 'numeric');
            app.ColumnVolume.LowerLimitInclusive = 'off';
            app.ColumnVolume.Limits = [0 Inf];
            app.ColumnVolume.RoundFractionalValues = 'on';
            app.ColumnVolume.Position = [277 406 44 22];
            app.ColumnVolume.Value = 81;
            
            % Create ElutionDurationLabel
            app.ElutionDurationLabel = uilabel(app.ExperimentDetailsTab);
            app.ElutionDurationLabel.HorizontalAlignment = 'center';
            app.ElutionDurationLabel.WordWrap = 'on';
            app.ElutionDurationLabel.Position = [378 403 55 30];
            app.ElutionDurationLabel.Text = 'Elution Duration';
            
            % Create ElutionDuration
            app.ElutionDuration = uieditfield(app.ExperimentDetailsTab, 'numeric');
            app.ElutionDuration.Position = [437 406 51 22];
            
            % Create InjectionVolumeLabelUnits
            app.InjectionVolumeLabelUnits = uilabel(app.ExperimentDetailsTab);
            app.InjectionVolumeLabelUnits.HorizontalAlignment = 'right';
            app.InjectionVolumeLabelUnits.Position = [656 406 25 22];
            app.InjectionVolumeLabelUnits.Text = 'mL';
            
            % Create InjectionVolumeLabel
            app.InjectionVolumeLabel = uilabel(app.ExperimentDetailsTab);
            app.InjectionVolumeLabel.HorizontalAlignment = 'center';
            app.InjectionVolumeLabel.WordWrap = 'on';
            app.InjectionVolumeLabel.Position = [550 403 65 30];
            app.InjectionVolumeLabel.Text = 'Injection Volume';
            
            % Create InjectionVolume
            app.InjectionVolume = uieditfield(app.ExperimentDetailsTab, 'numeric');
            app.InjectionVolume.LowerLimitInclusive = 'off';
            app.InjectionVolume.Limits = [0 Inf];
            app.InjectionVolume.Position = [614 406 44 22];
            app.InjectionVolume.Value = 1;
            
            % Create StationaryPhaseRetentionLabel
            app.StationaryPhaseRetentionLabel = uilabel(app.ExperimentDetailsTab);
            app.StationaryPhaseRetentionLabel.HorizontalAlignment = 'center';
            app.StationaryPhaseRetentionLabel.WordWrap = 'on';
            app.StationaryPhaseRetentionLabel.Position = [73 316 96 57];
            app.StationaryPhaseRetentionLabel.Text = 'Stationary Phase Retention';
            
            % Create StationaryPhaseRetention
            app.StationaryPhaseRetention = uieditfield(app.ExperimentDetailsTab, 'numeric');
            app.StationaryPhaseRetention.LowerLimitInclusive = 'off';
            app.StationaryPhaseRetention.UpperLimitInclusive = 'off';
            app.StationaryPhaseRetention.Limits = [0 1];
            app.StationaryPhaseRetention.Position = [180 333 51 22];
            app.StationaryPhaseRetention.Value = 0.75;
            
            % Create ColumnDeadVolumeLabelUnits
            app.ColumnDeadVolumeLabelUnits = uilabel(app.ExperimentDetailsTab);
            app.ColumnDeadVolumeLabelUnits.HorizontalAlignment = 'center';
            app.ColumnDeadVolumeLabelUnits.WordWrap = 'on';
            app.ColumnDeadVolumeLabelUnits.Position = [407 338 24 14];
            app.ColumnDeadVolumeLabelUnits.Text = 'mL';
            
            % Create ColumnDeadVolumeLabel
            app.ColumnDeadVolumeLabel = uilabel(app.ExperimentDetailsTab);
            app.ColumnDeadVolumeLabel.HorizontalAlignment = 'center';
            app.ColumnDeadVolumeLabel.WordWrap = 'on';
            app.ColumnDeadVolumeLabel.Position = [260 328 89 34];
            app.ColumnDeadVolumeLabel.Text = 'Column Dead Volume';
            
            % Create ColumnDeadVolume
            app.ColumnDeadVolume = uieditfield(app.ExperimentDetailsTab, 'numeric');
            app.ColumnDeadVolume.Limits = [0 Inf];
            app.ColumnDeadVolume.Position = [358 334 44 22];
            
            % Create ColumnEfficiencyNLabel
            app.ColumnEfficiencyNLabel = uilabel(app.ExperimentDetailsTab);
            app.ColumnEfficiencyNLabel.HorizontalAlignment = 'center';
            app.ColumnEfficiencyNLabel.WordWrap = 'on';
            app.ColumnEfficiencyNLabel.Position = [473 331 91 28];
            app.ColumnEfficiencyNLabel.Text = 'Column Efficiency (N)';
            
            % Create ColumnEfficiencyN
            app.ColumnEfficiencyN = uieditfield(app.ExperimentDetailsTab, 'numeric');
            app.ColumnEfficiencyN.UpperLimitInclusive = 'off';
            app.ColumnEfficiencyN.Limits = [1 Inf];
            app.ColumnEfficiencyN.Position = [578 334 51 22];
            app.ColumnEfficiencyN.Value = 400;
            
            % Create UITable
            initialRows = {'Compound 1' 1 1 1; 'Compound 2' 1 1 1};
            app.UITable = uitable(app.ExperimentDetailsTab, ...
                "ColumnName",{'Compound'; 'KD'; 'Conc. (g/L)'; 'Draw'}, ...
                "ColumnFormat",{'char' [] [] 'logical'}, ...
                "Data",initialRows);
            app.UITable.RowName = {};
            app.UITable.ColumnSortable = true;
            app.UITable.ColumnEditable = true;
            app.UITable.Position = [73 12 585 255];

            % Create addCompound
            app.addCompound = uibutton(app.ExperimentDetailsTab,'ButtonPushedFcn',@(src,event) addCompoundButtonPushed(app));
            app.addCompound.Position = [27 242 23 25];
            app.addCompound.Text = '+';

            % Create removeCompound
            app.removeCompound = uibutton(app.ExperimentDetailsTab,'ButtonPushedFcn',@(src,event) removeCompoundButtonPushed(app));
            app.removeCompound.Position = [26 209 25 25];
            app.removeCompound.Text = '-';

            % Create CompoundListLabel
            app.CompoundListLabel = uilabel(app.ExperimentDetailsTab);
            app.CompoundListLabel.HorizontalAlignment = 'center';
            app.CompoundListLabel.FontSize = 18;
            app.CompoundListLabel.FontWeight = 'bold';
            app.CompoundListLabel.Position = [291 286 137 24];
            app.CompoundListLabel.Text = 'Compound List';

            % Create ColumnPropertiesLabel
            app.ColumnPropertiesLabel = uilabel(app.ExperimentDetailsTab);
            app.ColumnPropertiesLabel.HorizontalAlignment = 'center';
            app.ColumnPropertiesLabel.FontSize = 18;
            app.ColumnPropertiesLabel.FontWeight = 'bold';
            app.ColumnPropertiesLabel.Position = [276 450 166 24];
            app.ColumnPropertiesLabel.Text = 'Column Properties';

            % Create ClassicElutionTab
            app.ClassicElutionTab = uitab(app.TabGroup);
            app.ClassicElutionTab.Title = 'Classic Elution';

            % Create UIAxesClassic
            app.UIAxesClassic = uiaxes(app.ClassicElutionTab);
            xlabel(app.UIAxesClassic, 'Elution Time')
            ylabel(app.UIAxesClassic, 'Concentration')
            zlabel(app.UIAxesClassic, 'Z')
            app.UIAxesClassic.Position = [8 143 695 301];

            % Create PlotButtonClassic
            app.PlotButtonClassic = uibutton(app.ClassicElutionTab, 'ButtonPushedFcn',@(src,event) plotClassicalPrediction(app));
            app.PlotButtonClassic.Position = [297 450 68 23];
            app.PlotButtonClassic.Text = 'Plot';

            % Create ExportButtonClassic
            app.ExportButtonClassic = uibutton(app.ClassicElutionTab, 'ButtonPushedFcn',@(src,event) exportPlotExcel(app));
            app.ExportButtonClassic.Position = [372 450 68 23];
            app.ExportButtonClassic.Text = 'Export';

            % Create ElutionExtrusionTab
            app.ElutionExtrusionTab = uitab(app.TabGroup);
            app.ElutionExtrusionTab.Title = 'Elution-Extrusion';

            % Create UIAxesExtrusion
            app.UIAxesExtrusion = uiaxes(app.ElutionExtrusionTab);
            xlabel(app.UIAxesExtrusion, 'Elution Time')
            ylabel(app.UIAxesExtrusion, 'Concentration')
            zlabel(app.UIAxesExtrusion, 'Z')
            app.UIAxesExtrusion.Position = [8 143 695 301];

            % Create PlotButton_3
            app.PlotButtonExtrusion = uibutton(app.ElutionExtrusionTab, 'ButtonPushedFcn',@(src,event) plotExtrusionPrediction(app));
            app.PlotButtonExtrusion.Position = [297 450 68 23];
            app.PlotButtonExtrusion.Text = 'Plot';

            % Create ExportButtonExtrusion
            app.ExportButtonExtrusion = uibutton(app.ElutionExtrusionTab, 'push');
            app.ExportButtonExtrusion.Position = [372 450 68 23];
            app.ExportButtonExtrusion.Text = 'Export';

            % Create ExtrusionDurationLabel
            app.ExtrusionDurationLabel = uilabel(app.ElutionExtrusionTab);
            app.ExtrusionDurationLabel.HorizontalAlignment = 'right';
            app.ExtrusionDurationLabel.Position = [33 450 104 22];
            app.ExtrusionDurationLabel.Text = 'Extrusion Duration';

            % Create ExtrusionDuration
            app.ExtrusionDuration = uieditfield(app.ElutionExtrusionTab, 'numeric');
            app.ExtrusionDuration.Position = [145 450 29 22];

            % Create ExtrusionDurationLabelUnits
            app.ExtrusionDurationLabelUnits = uilabel(app.ElutionExtrusionTab);
            app.ExtrusionDurationLabelUnits.HorizontalAlignment = 'center';
            app.ExtrusionDurationLabelUnits.Position = [182 450 29 22];
            app.ExtrusionDurationLabelUnits.Text = 'min';

            % Create yield and purity table
            app.yieldAndPurity = uitable(app.ElutionExtrusionTab);
            app.yieldAndPurity.ColumnName = {'Column 1'; 'Column 2'; 'Column 3'; 'Column 4'};
            app.yieldAndPurity.RowName = {};
            app.yieldAndPurity.Position = [49 12 647 122];

            % Create MultipleDualModeTab
            app.MultipleDualModeTab = uitab(app.TabGroup);
            app.MultipleDualModeTab.Title = 'Multiple Dual Mode';

            % Create UIAxesMulti
            app.UIAxesMulti = uiaxes(app.MultipleDualModeTab);
            xlabel(app.UIAxesMulti, 'Elution Time')
            ylabel(app.UIAxesMulti, 'Concentration')
            zlabel(app.UIAxesMulti, 'Z')
            app.UIAxesMulti.Position = [8 263 695 215];

            % Create UIAxesMultiPosition
            app.UIAxesMultiPosition = uiaxes(app.MultipleDualModeTab);
            xlabel(app.UIAxesMultiPosition, 'Elution Time')
            ylabel(app.UIAxesMultiPosition, 'Column Position')
            zlabel(app.UIAxesMultiPosition, 'Z')
            app.UIAxesMultiPosition.Position = [9 57 695 215];

            % Create PlotButton_4
            app.PlotButtonMulti = uibutton(app.MultipleDualModeTab, 'push');
            app.PlotButtonMulti.Position = [553 19 68 23];
            app.PlotButtonMulti.Text = 'Plot';

            % Create ExportButtonMulti
            app.ExportButtonMulti = uibutton(app.MultipleDualModeTab, 'push');
            app.ExportButtonMulti.Position = [628 19 68 23];
            app.ExportButtonMulti.Text = 'Export';

            % Create CycleDurationsLabel
            app.CycleDurationsLabel = uilabel(app.MultipleDualModeTab);
            app.CycleDurationsLabel.HorizontalAlignment = 'right';
            app.CycleDurationsLabel.Position = [44 20 90 22];
            app.CycleDurationsLabel.Text = 'Cycle Durations';

            % Create CycleDurations
            app.CycleDurations = uieditfield(app.MultipleDualModeTab, 'text');
            app.CycleDurations.Position = [149 20 200 22];
            app.CycleDurations.Value = '10 10 10 10 5 5 5';

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