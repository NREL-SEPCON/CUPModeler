classdef AppV1 < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                      matlab.ui.Figure
        FileMenu                      matlab.ui.container.Menu
        SaveMenu                      matlab.ui.container.Menu
        OpenMenu                      matlab.ui.container.Menu
        AboutMenu                     matlab.ui.container.Menu
        TabGroup                      matlab.ui.container.TabGroup
        ColumnPropertiesLabel         matlab.ui.control.Label
        CompoundListLabel             matlab.ui.control.Label
        VolumeTimeSwitch              matlab.ui.control.Switch
        AscDescLabel                  matlab.ui.control.Label
        AscDesc                       matlab.ui.control.Switch
        StationaryPhaseSwitch         matlab.ui.control.Switch
        ColumnEfficiencySwitch        matlab.ui.control.Switch
        removeCompound                matlab.ui.control.Button
        addCompound                   matlab.ui.control.Button
        saveCompoundList              matlab.ui.control.Button
        openCompoundList              matlab.ui.control.Button
        saveSwitchTimes               matlab.ui.control.Button
        openSwitchTimes               matlab.ui.control.Button
        compoundList                  matlab.ui.control.Table
        includeInjectionVolCheckbox   matlab.ui.control.CheckBox
        ClassicPeaksCheckbox          matlab.ui.control.CheckBox
        classicModelSumCheckbox       matlab.ui.control.CheckBox
        ExtrusionPeaksCheckbox        matlab.ui.control.CheckBox
        extrusionModelSumCheckbox     matlab.ui.control.CheckBox
        DualPeaksCheckbox             matlab.ui.control.CheckBox
        MultiPeaksCheckbox            matlab.ui.control.CheckBox
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
        NCoefficientA                 matlab.ui.control.NumericEditField
        NCoefficientALabel            matlab.ui.control.Label
        NCoefficientB                 matlab.ui.control.NumericEditField
        NCoefficientBLabel            matlab.ui.control.Label
        NCoefficientC                 matlab.ui.control.NumericEditField
        NCoefficientCLabel            matlab.ui.control.Label
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
        PulseTab                      matlab.ui.container.Tab
        UIAxesPulse                   matlab.ui.control.UIAxes
        ImportPulseTraceButton        matlab.ui.control.Button
        AddPulseNValue                matlab.ui.control.Button
        SavePulseList                 matlab.ui.control.Button
        OpenPulseList                 matlab.ui.control.Button
        PulseSpan                     matlab.ui.control.NumericEditField
        PulseSpanLabel                matlab.ui.control.Label
        PulseProminence               matlab.ui.control.NumericEditField
        PulseProminenceLabel          matlab.ui.control.Label
        PulseBaseline                 matlab.ui.control.NumericEditField
        PulseBaselineLabel            matlab.ui.control.Label
        PulseNTableListLabel          matlab.ui.control.Label
        regressionHeader              matlab.ui.control.Label
        NEquationLabel                matlab.ui.control.Label
        useNButton                    matlab.ui.control.Button
        labelNA                       matlab.ui.control.Label
        labelNB                       matlab.ui.control.Label
        labelNC                       matlab.ui.control.Label
        SfEquationLabel               matlab.ui.control.Label
        useSfButton                   matlab.ui.control.Button
        labelSfA                      matlab.ui.control.Label
        labelSfB                      matlab.ui.control.Label
        PulseNList                    matlab.ui.control.Table
        FindPulsePeaksButton          matlab.ui.control.Button
        dataPreviewTable              matlab.ui.control.Table
        FitTab                        matlab.ui.container.Tab
        UIAxesFit                     matlab.ui.control.UIAxes
        ImportTraceButton             matlab.ui.control.Button
        FitSpan                       matlab.ui.control.NumericEditField
        FitSpanLabel                  matlab.ui.control.Label
        FitProminence                 matlab.ui.control.NumericEditField
        FitProminenceLabel            matlab.ui.control.Label
        FitThreshold                  matlab.ui.control.NumericEditField
        FitThresholdLabel             matlab.ui.control.Label
        FindFitPeaksButton            matlab.ui.control.Button
        ComputeKDValues               matlab.ui.control.Button
        DisplayWithModeling           matlab.ui.control.CheckBox
        Info                          matlab.ui.container.Tab
        InfoTitle                     matlab.ui.control.Label
        InfoVersion                   matlab.ui.control.Label
        InfoCitation                  matlab.ui.control.Label
        cupPaper                      matlab.ui.control.Hyperlink
        InfoCredits                   matlab.ui.control.Label
    end
    
    % Callbacks that handle component events
    methods (Access = private)

        function saveState(app)
            filename = ['Session ' + string(datetime) + '.mat'];
            [filename, directory] = uiputfile('.mat', 'Save session', filename);
            inputsToSave = struct('F', app.FlowRate.Value, ...
                                  'colVol', app.ColumnVolume.Value, ...
                                  'timeVolToggle', app.VolumeTimeSwitch.Value, ...
                                  'AscDesc', app.AscDesc.Value, ...
                                  'SfCoeff', app.StationaryPhaseSwitch.Value,...
                                  'NCoeff', app.ColumnEfficiencySwitch.Value, ...
                                  'compoundList', {app.compoundList.Data}, ...
                                  'injVolChkBx', app.includeInjectionVolCheckbox.Value, ...
                                  'elutionDuration', app.ElutionDuration.Value, ...
                                  'Vd', app.ColumnDeadVolume.Value, ...
                                  'Vinj', app.InjectionVolume.Value, ...
                                  'classicPlot', {getappdata(app.UIAxesClassic, 'rawData')}, ...
                                  'extrusionDuration', app.ExtrusionDuration.Value, ...
                                  'extrusionPlot', {getappdata(app.UIAxesExtrusion, 'rawData')}, ...
                                  'dualDuration', app.DualDuration.Value, ...
                                  'dualPlot', {getappdata(app.UIAxesDual, 'rawData')}, ...
                                  'switchTimeList', {app.SwitchTimeList.Data}, ...
                                  'multiPlot', {getappdata(app.UIAxesMulti, 'rawData')}, ...
                                  'multiPositionPlot', {getappdata(app.UIAxesMultiPosition, 'rawData')}, ...
                                  'PulseNList', {app.PulseNList.Data},...
                                  'pulseSpan', app.PulseSpan.Value, ...
                                  'PulseProminence', app.PulseProminence.Value, ...
                                  'PulseBaseline', app.PulseBaseline.Value, ...
                                  'pulsePlot', app.UIAxesPulse, ...
                                  'FitSpan', app.FitSpan.Value, ...
                                  'FitProminence', app.FitProminence.Value, ...
                                  'FitThreshold', app.FitThreshold.Value, ...
                                  'FitPlot', app.UIAxesFit);

            if string(app.StationaryPhaseSwitch.Value) == 'Set Sf'
                inputsToSave.Sf = app.StationaryPhaseRetention.Value;

            elseif string(app.StationaryPhaseSwitch.Value) == 'Coeff.'
                inputsToSave.SfA = app.SfCoefficientA.Value;
                inputsToSave.SfB = app.SfCoefficientB.Value;
            end

            if string(app.ColumnEfficiencySwitch.Value) == 'Set N'
                inputsToSave.N = app.ColumnEfficiencyN.Value;

            elseif string(app.ColumnEfficiencySwitch.Value) == 'Coeff.'
                inputsToSave.NA = app.NCoefficientA.Value;
                inputsToSave.NB = app.NCoefficientB.Value;
                inputsToSave.NC = app.NCoefficientC.Value;
            end

            save(strcat(directory, filename), 'inputsToSave');
        end

        function loadState(app)
            [filename, directory] = uigetfile('.mat');
            load(strcat(directory, filename));

            if string(inputsToSave.SfCoeff) == 'Set Sf'
                if string(app.StationaryPhaseSwitch.Value) == 'Coeff.'
                    app.StationaryPhaseSwitch.Value = 'Set Sf'
                    app.toggleStationary();
                end
                
                app.StationaryPhaseRetention.Value = inputsToSave.Sf
                
            elseif string(inputsToSave.SfCoeff) == 'Coeff.'
                if string(app.StationaryPhaseSwitch.Value) == 'Set Sf'
                    app.StationaryPhaseSwitch.Value = 'Coeff.'
                    app.toggleStationary();
                end
                
                app.SfCoefficientA.Value = inputsToSave.SfA;
                app.SfCoefficientB.Value = inputsToSave.SfB;
            end
            
            if string(inputsToSave.NCoeff) == 'Set N'
                if string(app.ColumnEfficiencySwitch.Value) == 'Coeff.'
                    app.ColumnEfficiencySwitch.Value = 'Set N'
                    app.toggleEfficiency();
                end
                
                app.ColumnEfficiencyN.Value = inputsToSave.N
                
            elseif string(inputsToSave.NCoeff) == 'Coeff.'
                if string(app.ColumnEfficiencySwitch.Value) == 'Set N'
                    app.ColumnEfficiencySwitch.Value = 'Coeff'
                    app.toggleEfficiency();
                end

                app.NCoefficientA.Value = inputsToSave.NA;
                app.NCoefficientB.Value = inputsToSave.NB;
                app.NCoefficientC.Value = inputsToSave.NC;
            end

            app.FlowRate.Value = inputsToSave.F;
            app.ColumnVolume.Value = inputsToSave.colVol;
            app.VolumeTimeSwitch.Value = inputsToSave.timeVolToggle;
            app.AscDesc.Value = inputsToSave.AscDesc;
            app.includeInjectionVolCheckbox.Value = inputsToSave.injVolChkBx;
            app.compoundList.Data = inputsToSave.compoundList;
            app.ElutionDuration.Value = inputsToSave.elutionDuration;
            app.ColumnDeadVolume.Value = inputsToSave.Vd;
            app.InjectionVolume.Value = inputsToSave.Vinj;
            app.ExtrusionDuration.Value = inputsToSave.extrusionDuration;
            app.DualDuration.Value = inputsToSave.dualDuration;
            app.SwitchTimeList.Data = inputsToSave.switchTimeList;
            app.PulseNList.Data = inputsToSave.PulseNList;
            app.PulseSpan.Value = inputsToSave.pulseSpan;
            app.PulseProminence.Value = inputsToSave.PulseProminence;
            app.PulseBaseline.Value = inputsToSave.PulseBaseline;
            app.UIAxesPulse = inputsToSave.pulsePlot;
            app.FitSpan.Value = inputsToSave.FitSpan;
            app.FitProminence.Value = inputsToSave.FitProminence;
            app.FitThreshold.Value = inputsToSave.FitThreshold;
            app.UIAxesFit = inputsToSave.FitPlot;
            
            plot(app.UIAxesClassic, inputsToSave.classicPlot{1}, inputsToSave.classicPlot{2}, 'linewidth', 2.0);
            plot(app.UIAxesExtrusion, inputsToSave.extrusionPlot{1}, inputsToSave.extrusionPlot{2}, 'linewidth', 2.0);
            plot(app.UIAxesDual, inputsToSave.dualPlot{1}, inputsToSave.dualPlot{2}, 'linewidth', 2.0);
            plot(app.UIAxesMulti, inputsToSave.multiPlot{1}, inputsToSave.multiPlot{2}, 'linewidth', 2.0);
            contourf(app.UIAxesMultiPosition, inputsToSave.multiPositionPlot{1}, inputsToSave.multiPositionPlot{2}, inputsToSave.multiPositionPlot{3}, inputsToSave.multiPositionPlot{4}, 'linecolor', 'none');

        end

        function toggleVolumeTime(app)
            F = app.FlowRate.Value;

            if string(app.VolumeTimeSwitch.Value) == 'Volume'
                app.ElutionDurationLabel.Text = 'Elution Volume';
                app.ElutionDurationLabelUnits.Text = 'mL';

                app.compoundList.ColumnName(4) = {'Elution Vol. (mL)'};

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

            elseif string(app.VolumeTimeSwitch.Value) == 'Time'
                app.ElutionDurationLabel.Text = 'Elution Duration';
                app.ElutionDurationLabelUnits.Text = 'min';

                app.compoundList.ColumnName(4) = {'Ret. Time (min)'};
                
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
            end
            CUPPrediction(app);
        end

        function toggleStationary(app)
            if string(app.StationaryPhaseSwitch.Value) == 'Set Sf'
                
                delete(app.SfCoefficientA);
                delete(app.SfCoefficientALabel);
                delete(app.SfCoefficientB);
                delete(app.SfCoefficientBLabel);
                
                % Create StationaryPhaseRetention
                app.StationaryPhaseRetention = uieditfield(app.UIFigure, 'numeric');
                app.StationaryPhaseRetention.LowerLimitInclusive = 'off';
                app.StationaryPhaseRetention.UpperLimitInclusive = 'off';
                app.StationaryPhaseRetention.Limits = [0 1];
                app.StationaryPhaseRetention.Position = [72 345 51 22];
                app.StationaryPhaseRetention.Value = 0.75;

            elseif string(app.StationaryPhaseSwitch.Value) == 'Coeff.'

                delete(app.StationaryPhaseRetention);

                app.SfCoefficientALabel = uilabel(app.UIFigure);
                app.SfCoefficientALabel.HorizontalAlignment = 'center';
                app.SfCoefficientALabel.WordWrap = 'on';
                app.SfCoefficientALabel.Position = [20 345 20 20];
                app.SfCoefficientALabel.Text = 'A';

                app.SfCoefficientA = uieditfield(app.UIFigure, 'numeric');
                app.SfCoefficientA.LowerLimitInclusive = 'off';
                app.SfCoefficientA.UpperLimitInclusive = 'off';
                app.SfCoefficientA.Position = [40 345 51 22];
                app.SfCoefficientA.Value = 0.9821;

                app.SfCoefficientBLabel = uilabel(app.UIFigure);
                app.SfCoefficientBLabel.HorizontalAlignment = 'center';
                app.SfCoefficientBLabel.WordWrap = 'on';
                app.SfCoefficientBLabel.Position = [100 345 20 20];
                app.SfCoefficientBLabel.Text = 'B';

                app.SfCoefficientB = uieditfield(app.UIFigure, 'numeric');
                app.SfCoefficientB.LowerLimitInclusive = 'off';
                app.SfCoefficientB.UpperLimitInclusive = 'off';
                app.SfCoefficientB.Position = [120 345 51 22];
                app.SfCoefficientB.Value = -0.1426;
            end
        end

        function toggleStationaryAndPlot(app)
            app.toggleStationary();
            app.CUPPrediction();
        end

        function toggleEfficiency(app)
            if string(app.ColumnEfficiencySwitch.Value) == 'Set N'
                
                delete(app.NCoefficientA);
                delete(app.NCoefficientALabel);
                delete(app.NCoefficientB);
                delete(app.NCoefficientBLabel);
                delete(app.NCoefficientC);
                delete(app.NCoefficientCLabel);
                
                % Create ColumnEfficiencyN
                app.ColumnEfficiencyN = uieditfield(app.UIFigure, 'numeric');
                app.ColumnEfficiencyN.UpperLimitInclusive = 'off';
                app.ColumnEfficiencyN.Limits = [1 Inf];
                app.ColumnEfficiencyN.Position = [305 345 51 22];
                app.ColumnEfficiencyN.Value = 400;
                
            elseif string(app.ColumnEfficiencySwitch.Value) == 'Coeff.'
                
                delete(app.ColumnEfficiencyN);
                
                app.NCoefficientALabel = uilabel(app.UIFigure);
                app.NCoefficientALabel.HorizontalAlignment = 'center';
                app.NCoefficientALabel.Position = [205 345 20 20];
                app.NCoefficientALabel.Text = 'A';
                
                app.NCoefficientA = uieditfield(app.UIFigure, 'numeric');
                app.NCoefficientA.Position = [225 345 51 22];
                app.NCoefficientA.Value = 371.239;
                
                app.NCoefficientBLabel = uilabel(app.UIFigure);
                app.NCoefficientBLabel.HorizontalAlignment = 'center';
                app.NCoefficientBLabel.Position = [285 345 20 20];
                app.NCoefficientBLabel.Text = 'B';
                
                app.NCoefficientB = uieditfield(app.UIFigure, 'numeric');
                app.NCoefficientB.Position = [305 345 51 22];
                app.NCoefficientB.Value = -7.2042;
                
                app.NCoefficientCLabel = uilabel(app.UIFigure);
                app.NCoefficientCLabel.HorizontalAlignment = 'center';
                app.NCoefficientCLabel.Position = [365 345 20 20];
                app.NCoefficientCLabel.Text = 'C';
                
                app.NCoefficientC = uieditfield(app.UIFigure, 'numeric');
                app.NCoefficientC.Position = [385 345 51 22];
                app.NCoefficientC.Value = 0.14807;
            end
        end
        
        function toggleEfficiencyAndPlot(app)
            app.toggleEfficiency();
            app.CUPPrediction();
        end

        function addCompoundButtonPushed(app)
            newRowPosition = height(app.compoundList.Data)+1;
            newRowPositionString = num2str(newRowPosition);
            compoundName = {char(append('Compound',' ',newRowPositionString))};
            for i = 1:height(app.compoundList.Data)
                checkedName = app.compoundList.Data(i,1);
                if string(cell2mat(checkedName)) == string(cell2mat(compoundName))
                    compoundName = {convertStringsToChars(string(compoundName) + ' - Rename')};
                end
            end
            app.compoundList.Data(end+1,:) = [compoundName,1,1,0,0];
        end

        function removeCompoundButtonPushed(app)
            if height(app.compoundList.Data) > 1
            app.compoundList.Data(end,:) = [];
            end
        end

        function removeSpecificCompound(app)
            if height(app.compoundList.Data) > 1
                deletedIndex = app.compoundList.Data(:,5);
                for i = 1:height(deletedIndex)
                    if cell2mat(deletedIndex(i)) == 1
                        app.compoundList.Data(i,:) = [];
                    end
                end
            else 
                app.compoundList.Data(1,5) = {false};
            end
        end

        function saveCompounds(app)
            filename = ['Compound List ' + string(datetime) + '.xls'];
            [filename] = uiputfile('.xls', 'Save compound list', filename);
            compoundTableContents = get(app.compoundList, 'Data');
            writecell(compoundTableContents, filename);
        end

        function openCompounds(app)
            [filename] = uigetfile('.xls');
            importedTable = array2table(readcell(filename));
            app.compoundList.Data = table2cell(importedTable);
        end

        function saveSwitchTimeList(app)
            filename = ['Switching Times ' + string(datetime) + '.xls'];
            [filename] = uiputfile('.xls', 'Save switch time list', filename);
            switchTimeTableContents = get(app.SwitchTimeList, 'Data');
            writecell(switchTimeTableContents, filename);
        end

        function openSwitchTimeList(app)
            [filename] = uigetfile('.xls');
            importedTable = array2table(readcell(filename));
            app.SwitchTimeList.Data = table2cell(importedTable);
        end

        function savePulseList(app)
            filename = ['Pulse List ' + string(datetime) + '.xls'];
            [filename] = uiputfile('.xls', 'Save pulse list', filename);
            pulseListTableContents = get(app.PulseNList, 'Data');
            writematrix(pulseListTableContents, filename);
        end

        function openPulseList(app)
            [filename] = uigetfile('.xls');
            app.PulseNList.Data = cell2mat(readcell(filename));
            app.fitCoefficients();
        end

        function addCycleButtonPushed(app)
            newRowPosition = height(app.SwitchTimeList.Data)+1;
            newRowPositionString = num2str(newRowPosition);
            cycleName = {char(append('Cycle',' ',newRowPositionString))};
            app.SwitchTimeList.Data(end+1,:) = [cycleName,5];
        end

        function removeCycleButtonPushed(app)
            app.SwitchTimeList.Data(end,:) = [];
        end

        function importTrace(app)
            identifier = string(gcbo().Tag);
            
            [file,filepath,filter] = uigetfile({'*.*';'*.xls';'*.xlsx'});
            filename = fullfile(filepath,file);
            
            options = detectImportOptions(filename);
            
            dataPreview = preview(filename, options);

            [importedData] = xlsread(filename)';

            cover = uilabel(app.UIFigure, 'Position', [0 0 10000 10000]);

            selectedFields = ColumnSelectPopup(importedData);

            delete(cover);

            if all(selectedFields > 0) && all(floor(selectedFields) == selectedFields)
                X = importedData(selectedFields(1),:);
                Y = importedData(selectedFields(2),:);
                
                if contains(identifier, 'Fit')
                    app.FitSpan.Limits = [2 length(Y)/2];
                    guidata(app.UIAxesFit, [X,Y]);
                    plot(app.UIAxesFit, X, Y, 'linewidth', 2.0);
                elseif contains(identifier, 'Pulse')                
                    guidata(app.UIAxesPulse, [X,Y]);
                    plot(app.UIAxesPulse, X, Y, 'linewidth', 2.0);
                end
            end
        end
        
        function findAndLabelFitPeaks(app)
            plottedData = guidata(app.UIAxesFit);
            dataMidpoint = length(guidata(app.UIAxesFit))/2;
            X = plottedData(1:dataMidpoint);
            Y = smooth(plottedData(dataMidpoint+1:end), app.FitSpan.Value);
            
            plot(app.UIAxesFit, X, Y, 'linewidth', 2.0);
            yline(app.UIAxesFit, app.FitThreshold.Value, '-.r', 'Threshold');
            
            set(0,'DefaultFigureVisible','off');
            findpeaks(Y, X, 'MinPeakProminence', app.FitProminence.Value, 'MinPeakHeight', app.FitThreshold.Value);
            set(0,'DefaultFigureVisible','on');
            ax2 = gca;
            children = findobj(ax2.Children, '-not', 'tag', 'Signal');
            copyobj(children, app.UIAxesFit);
            delete(ax2.Parent);
        end
        
        function [X,Y] = findAndLabelPulsePeaks(app)
            plottedData = guidata(app.UIAxesPulse);
            dataMidpoint = length(guidata(app.UIAxesPulse))/2;
            X = plottedData(1:dataMidpoint);
            Y = smooth(plottedData(dataMidpoint+1:end), app.PulseSpan.Value)-app.PulseBaseline.Value;
            
            plot(app.UIAxesPulse, X, Y, 'linewidth', 2.0);
            yline(app.UIAxesPulse, 0, '-.r');
            [maxY, maxYIndex] = max(Y);
            text(app.UIAxesPulse, X(maxYIndex), maxY*.02, 'Baseline', 'HorizontalAlignment', 'center', 'Color', 'r');
            
            set(0,'DefaultFigureVisible','off');
            findpeaks(Y, X, 'MinPeakProminence', app.PulseProminence.Value);
            set(0,'DefaultFigureVisible','on');
            ax2 = gca;
            Peaks = findobj(ax2.Children, '-not', 'tag', 'Signal');
            copyobj(Peaks, app.UIAxesPulse);
            delete(ax2.Parent);
            
            app.UIAxesPulse.YLim = [-1*max(Y)*0.1 max(Y)*1.1];
        end
        
        function updateCompoundListWithFits(app)
            cla(app.UIAxesFit);
            app.findAndLabelFitPeaks();
            
            [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution elutionTime deadVolume] = computeValues(app);
            
            [Vspan Cout X Y] = CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj);
            
            [Vspan, Cout, Xtot, Ytot, Vbc] = EECCC_V8(KD, Vc, Sf, X, Y);
            
            Vbc = Vbc + deadVolume;
            sweepTime = Vbc(2)/F;
            
            Vm = (1-Sf)*Vc;
            Vs = Sf*Vc;
            
            plottedData = guidata(app.UIAxesFit);
            dataMidpoint = length(guidata(app.UIAxesFit))/2;
            
            X = plottedData(1:dataMidpoint);
            Y = smooth(plottedData(dataMidpoint+1:end), app.FitSpan.Value);
            
            [pks,locs] = findpeaks(Y, 'MinPeakProminence', app.FitProminence.Value, 'MinPeakHeight', app.FitThreshold.Value);
            retentionTimes = X(locs);
            
            solventFrontTime = Vm/F;
            xline(app.UIAxesFit, solventFrontTime, '-.r', 'Solvent Front')

            elutionAndSweepPeakTimesLogical = retentionTimes < sweepTime;
            extrusionPeakTimesLogical = retentionTimes > sweepTime;
            
            elutionAndSweepPeakTimes = retentionTimes(elutionAndSweepPeakTimesLogical);
            extrusionPeakTimes = retentionTimes(extrusionPeakTimesLogical);
            
            elutionAndSweepPartitionCoefficients = ((F*elutionAndSweepPeakTimes)-Vm-(deadVolume/2))/Vs;

            if length(extrusionPeakTimes) > 0
                %extrusionPartitionCoefficients = (Vcm+deadVolume)./(Vc+Vcm+deadVolume-(extrusionPeakTimes*F));
                extrusionPartitionCoefficients = (Vcm)./(Vc+Vcm+deadVolume+(Vinj/2)-(extrusionPeakTimes*F));
            else
                extrusionPartitionCoefficients = [];
            end
            
            partitionCoefficients = [elutionAndSweepPartitionCoefficients extrusionPartitionCoefficients];
            pks = pks(partitionCoefficients > 0);
            retentionTimes = retentionTimes(partitionCoefficients > 0);
            partitionCoefficients = partitionCoefficients(partitionCoefficients > 0);
            
            for i = 1:height(app.compoundList.Data)
                app.removeCompoundButtonPushed()
            end

            for i = 1:length(partitionCoefficients)
                K = partitionCoefficients(i);
                C = pks(i);
                T = retentionTimes(i);

                newRowPositionString = num2str(i);
                compoundName = {char(append('Compound ',newRowPositionString))};

                app.compoundList.Data(i,:) = [compoundName,K,C,T,0];
            end
        end

        function addNValue(app)
            [X,Y] = findAndLabelPulsePeaks(app);

            [pks,locs] = findpeaks(Y, 'MinPeakProminence', app.PulseProminence.Value);
            retentionTimes = X(locs);

            peakHeight = max(Y);
            absolutePeakHeightAt60 = (0.6*peakHeight);

            [crossX, crossY] = polyxpoly(X, Y, [0 max(X)], [absolutePeakHeightAt60, absolutePeakHeightAt60]);

            volumeElutedAt60 = crossX*app.FlowRate.Value;

            WHalf60 = diff(volumeElutedAt60);

            WHalf60 = WHalf60(end);

            Vr = retentionTimes*app.FlowRate.Value;

            NValue = 4*(Vr/WHalf60)*(Vr/WHalf60);

            if string(app.StationaryPhaseSwitch.Value) == 'Set Sf'
                Sf = app.StationaryPhaseRetention.Value;
            elseif string(app.StationaryPhaseSwitch.Value) == "Coeff."
                Sf = app.SfCoefficientA.Value + app.SfCoefficientB.Value*F;
            end

            if length(retentionTimes) == 1
                app.PulseNList.Data(end+1,:) = [app.FlowRate.Value, Sf, NValue,0];
            end

            XPeakInd = find(X > crossX(end-1) & X < crossX(end));

            XPeak = X(XPeakInd(1):XPeakInd(end));
            YPeak = Y(XPeakInd(1):XPeakInd(end))';

            XPeak = [crossX(end-1), XPeak, crossX(end)];
            YPeak = [crossY(end-1), YPeak, crossY(end)];

            patch(app.UIAxesPulse, XPeak, YPeak,'blue','FaceAlpha',.2);

            app.fitCoefficients();
        end

        function removeSpecificNValue(app)
            deletedIndex = app.PulseNList.Data(:,4);
            for i = 1:height(deletedIndex)
                positionCheck = deletedIndex(i);
                if positionCheck == 1
                    app.PulseNList.Data(i,:) = [];
                end
            end
            app.fitCoefficients();
        end

        function fitCoefficients(app)
            flowRates = app.PulseNList.Data(:,1);
            SfValues = app.PulseNList.Data(:,2);
            NValues = app.PulseNList.Data(:,3);

            app.useNButton.Enable = 'off';
            app.useSfButton.Enable = 'off';

            app.labelNA.Text = 'A: ';
            app.labelNB.Text = 'B: ';
            app.labelNC.Text = 'C: ';

            app.labelSfA.Text = 'A: ';
            app.labelSfB.Text = 'B: ';

            if height(app.PulseNList.Data) > 2
                [Ncoeff Nerror] = polyfit(flowRates, NValues, 2);
                [Sfcoeff Sferror] = polyfit(flowRates, SfValues, 1);

                app.labelNA.Text = 'A: ' + string(Ncoeff(3));
                app.labelNB.Text = 'B: ' + string(Ncoeff(2));
                app.labelNC.Text = 'C: ' + string(Ncoeff(1));

                app.labelSfA.Text = 'A: ' + string(Sfcoeff(2));
                app.labelSfB.Text = 'B: ' + string(Sfcoeff(1));

                app.useNButton.Enable = 'on';
                app.useSfButton.Enable = 'on';
            end
        end

        function useNValues(app)
            if string(app.ColumnEfficiencySwitch.Value) == 'Set N'
                app.ColumnEfficiencySwitch.Value = 'Coeff.';
                app.toggleEfficiencyAndPlot();
            end

            A = str2double(extractAfter(app.labelNA.Text, ' '));
            app.NCoefficientA.Value = A;
            B = str2double(extractAfter(app.labelNB.Text, ' '));
            app.NCoefficientB.Value = B;
            C = str2double(extractAfter(app.labelNC.Text, ' '));
            app.NCoefficientC.Value = C;

            app.CUPPrediction();
        end

        function useSfValues(app)
            if string(app.StationaryPhaseSwitch.Value) == 'Set Sf'
                app.StationaryPhaseSwitch.Value = 'Coeff.';
                app.toggleStationaryAndPlot();
            end

            A = str2double(extractAfter(app.labelSfA.Text, ' '));
            app.SfCoefficientA.Value = A;
            B = str2double(extractAfter(app.labelSfB.Text, ' '));
            app.SfCoefficientB.Value = B;

            app.CUPPrediction();
        end

        function [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution elutionTime deadVolume] = computeValues(app)
            F = app.FlowRate.Value;
            if string(app.StationaryPhaseSwitch.Value) == 'Set Sf'
                Sf = app.StationaryPhaseRetention.Value;
            elseif string(app.StationaryPhaseSwitch.Value) == "Coeff."
                Sf = app.SfCoefficientA.Value + app.SfCoefficientB.Value*F;
            end
            KD = cell2mat(app.compoundList.Data(:,2));
            if app.AscDesc.Value == 'Upper'
                KD = 1./KD;
            end
            Vc = app.ColumnVolume.Value;

            if string(app.ColumnEfficiencySwitch.Value) == 'Set N'
                Ncup = app.ColumnEfficiencyN.Value;
            elseif string(app.ColumnEfficiencySwitch.Value) == 'Coeff.'
                Ncup = round(app.NCoefficientA.Value + app.NCoefficientB.Value*F + app.NCoefficientC.Value*F*F);
            end

            C0 = cell2mat(app.compoundList.Data(:,3));
            Vinj = app.InjectionVolume.Value;
            elutionTime = app.ElutionDuration.Value;
            deadVolume = app.ColumnDeadVolume.Value;

            if app.includeInjectionVolCheckbox.Value
                deadVolume = deadVolume + Vinj;
            end

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

        function addRetentionElutionToTable(app, peakPositions)
            for i = 1:length(peakPositions)
                app.compoundList.Data(i,4) = {peakPositions(i)};
            end
        end

        function [compoundNames, peakPositions, peakHeights, maxHeight] = addLabelsToPeaks(app, telute, Cout)
            compoundNames = cellstr(app.compoundList.Data(:,1));
            Cout = Cout';
            maxHeight = max(max(Cout));
            for i = 1:height(compoundNames)
                [peakHeights(i), peakPositions(i)] = max(Cout(:,i));
                peakHeights(i) = peakHeights(i)+(maxHeight*.05);
                peakPositions(i) = round(telute(peakPositions(i)), 2);
            end
        end

       function CUPPrediction(app)
            [F Sf KD Vc Ncup C0 Vinj Vcm Vcup Vmcup dtElution elutionTime deadVolume] = computeValues(app);

            [Vspan Cout X Y] = CupV6(Sf, KD, Vc, Ncup, Vcm, C0, Vinj);
            
            Nturn = Vspan/Vmcup;
            telute = (dtElution).*Nturn;
            
            identifier = string(gcbo().Tag);
            
            if identifier == 'Switch'
                identifier = string(app.TabGroup.SelectedTab.Tag);
                if contains(identifier, 'Info')
                    identifier = 'ClassicExtrusionDualMulti';
                end
            end
            
            if contains(identifier, 'Classic')
                if string(app.VolumeTimeSwitch.Value) == 'Volume'
                    F = 1;
                end
                telute = telute + deadVolume/F;
                setappdata(app.UIAxesClassic, 'rawData', {telute, Cout})
                plot(app.UIAxesClassic, telute, Cout, 'linewidth', 2.0);
                
                [compoundNames, peakPositions, peakHeights, maxHeight] = app.addLabelsToPeaks(telute, Cout);

                if app.classicModelSumCheckbox.Value == 1
                    summedTrace = sum(Cout);
                    hold(app.UIAxesClassic, 'on');
                    plot(app.UIAxesClassic, telute, summedTrace, '-.r', 'linewidth', 1.0);
                    hold(app.UIAxesClassic, 'off');

                    if maxHeight < max(summedTrace)
                        maxHeight = max(summedTrace);
                    end
                end

                if app.ClassicPeaksCheckbox.Value
                    text(app.UIAxesClassic, peakPositions, peakHeights, compoundNames, 'HorizontalAlignment', 'center');
                end

                if app.DisplayWithModeling.Value == 1
                    importedData = guidata(app.UIAxesFit);
                    dataMidpoint = length(guidata(app.UIAxesFit))/2;
                    
                    X = importedData(1:dataMidpoint);
                    Y = importedData(dataMidpoint+1:end);

                    if string(app.VolumeTimeSwitch.Value) == 'Volume'
                        X = X*F;
                    end

                    setappdata(app.UIAxesClassic, 'rawData', {X, Y});
                    
                    hold(app.UIAxesClassic, 'on');
                    plot(app.UIAxesClassic, X, Y, 'black', 'linewidth', 2.0);
                    hold(app.UIAxesClassic, 'off');

                    if maxHeight < max(Y)
                        maxHeight = max(Y);
                    end
                end

                app.UIAxesClassic.XLim = [0 elutionTime];
                app.UIAxesClassic.YLim = [0 maxHeight*1.1];
            end
            
            if contains(identifier, 'Extrusion')
                [Vspan, Cout, Xtot, Ytot, Vbc] = EECCC_V8(KD, Vc, Sf, X, Y);

                Vspan = Vspan + deadVolume;
                Vbc = Vbc + deadVolume;
                
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
                    sweepEndLabel = sprintf(['Extrusion Start\n']) + string(round(sweepTime, 2)) + LinesLabelsUnits;
                end

                setappdata(app.UIAxesExtrusion, 'rawData', {telute, Cout});
                
                plot(app.UIAxesExtrusion, telute, Cout, 'linewidth', 2.0);

                [compoundNames, peakPositions, peakHeights, maxHeight] = app.addLabelsToPeaks(telute, Cout);

                if app.extrusionModelSumCheckbox.Value == 1
                    summedTrace = sum(Cout);
                    hold(app.UIAxesExtrusion, 'on');
                    plot(app.UIAxesExtrusion, telute, summedTrace, '-.r', 'linewidth', 1.0);
                    hold(app.UIAxesExtrusion, 'off');

                    if maxHeight < max(summedTrace)
                        maxHeight = max(summedTrace);
                    end
                end

                if app.DisplayWithModeling.Value == 1
                    importedData = guidata(app.UIAxesFit);
                    dataMidpoint = length(guidata(app.UIAxesFit))/2;
                    
                    X = importedData(1:dataMidpoint);
                    Y = importedData(dataMidpoint+1:end);

                    if string(app.VolumeTimeSwitch.Value) == 'Volume'
                        X = X*F;
                    end
                    
                    hold(app.UIAxesExtrusion, 'on');
                    plot(app.UIAxesExtrusion, X, Y, 'black', 'linewidth', 2.0);
                    hold(app.UIAxesExtrusion, 'off');

                    if maxHeight < max(Y)
                        maxHeight = max(Y);
                    end
                end
                
                if app.ExtrusionLinesCheckbox.Value
                    xline(app.UIAxesExtrusion, columnVolumeExtrudedTime, '-.r', sweepStartLabel);
                    xline(app.UIAxesExtrusion, sweepTime, '--b', sweepEndLabel);
                end

                if app.ExtrusionPeaksCheckbox.Value
                    text(app.UIAxesExtrusion, peakPositions, peakHeights, compoundNames, 'HorizontalAlignment', 'center');
                end

                app.UIAxesExtrusion.XLim = [0 extrusionTime];
                app.UIAxesExtrusion.YLim = [0 maxHeight*1.1];
            end
            
            if contains(identifier, 'Dual')
                Vdm = app.DualDuration.Value;
                dualTime = elutionTime + Vdm + deadVolume;
                
                if string(app.VolumeTimeSwitch.Value) == 'Time'
                    Vdm = Vdm*F;
                    dualTime = elutionTime*F + Vdm + deadVolume;
                end
                
                [Vspan Cout, X, Y] = DualV2(KD, Vc, Sf, F, Vdm, X, Y);

                Vspan = Vspan + deadVolume;
                
                if string(app.VolumeTimeSwitch.Value) == 'Volume'
                    F = 1;
                end
                
                dualSwitchLabel = '';
                
                if app.DualLinesLabelsCheckbox.Value
                    LinesLabelsUnits = ' min';
                    if string(app.VolumeTimeSwitch.Value) == 'Volume'
                        LinesLabelsUnits = ' mL';
                    end
                    dualSwitchLabel = string(round((Vcm+deadVolume)/F, 2)) + LinesLabelsUnits;
                end
                
                telute = Vspan/F;
                stationaryPhaseVolume = dualTime/F;

                setappdata(app.UIAxesDual, 'rawData', {telute, Cout});
                
                plot(app.UIAxesDual, telute, Cout, 'linewidth', 2.0);
                
                if app.DualLinesCheckbox.Value
                    xline(app.UIAxesDual, (Vcm+deadVolume)/F, '-.r', dualSwitchLabel);
                    xline(app.UIAxesDual, stationaryPhaseVolume, '--b');
                end

                [compoundNames, peakPositions, peakHeights, maxHeight] = app.addLabelsToPeaks(telute, Cout);
               
                if app.DualPeaksCheckbox.Value
                    text(app.UIAxesDual, peakPositions, peakHeights, compoundNames, 'HorizontalAlignment', 'center');
                end

                app.UIAxesDual.XLim = [0 stationaryPhaseVolume];
                app.UIAxesDual.YLim = [0 maxHeight*1.1];
            end
            
            if contains(identifier, 'Multi')
                if string(app.VolumeTimeSwitch.Value) == 'Volume'
                    F = 1;
                end
                
                Vcm = [Vcm; cell2mat(app.SwitchTimeList.Data(:,2))*F];
                
                [Vspan, Cout, Xtot, Ytot, Tcut, VswDM, VswCM] = MDMV2(Sf, KD, Vc, Ncup, C0, Vinj, Vcm);
                %[Vx Vy] = MDMrT(Sf, KD, Vc, F, Vcm);

                telute = Vspan + deadVolume;
                VswCM = VswCM+deadVolume;
                VswDM = VswDM+deadVolume;
                
                if string(app.VolumeTimeSwitch.Value) == 'Time'
                    telute = telute/F;
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

                setappdata(app.UIAxesMulti, 'rawData', {telute, Cout});
                
                plot(app.UIAxesMulti, telute, Cout, 'linewidth', 2.0);

                [compoundNames, peakPositions, peakHeights, maxHeight] = app.addLabelsToPeaks(telute, Cout);
                
                app.UIAxesMulti.XLim = [0 telute(end)];
                app.UIAxesMulti.YLim = [0 maxHeight*1.1];
                
                xMatrix = sum(Xtot, 3);
                yAxis = [1:size(xMatrix,1)].*(1/size(xMatrix,1));

                matrixScaler = max(max(xMatrix));
                
                contourSpacing = linspace(0.001*matrixScaler, .05*matrixScaler, 30);

                setappdata(app.UIAxesMultiPosition, 'rawData', {telute, yAxis, xMatrix, contourSpacing});
                
                contourf(app.UIAxesMultiPosition, telute, yAxis, xMatrix, contourSpacing, 'linecolor', 'none');
                
                if app.MultiLinesCheckbox.Value
                    xline(app.UIAxesMulti, VswDM, '-.r', VswDMText);
                    xline(app.UIAxesMulti, VswCM, '-.b', VswCMText);
                    xline(app.UIAxesMultiPosition, VswDM, '-.r', VswDMText);
                    xline(app.UIAxesMultiPosition, VswCM, '-.b', VswCMText);
                end

                if app.MultiPeaksCheckbox.Value
                    text(app.UIAxesMulti, peakPositions, peakHeights, compoundNames, 'HorizontalAlignment', 'center');
                end
                
                app.UIAxesMultiPosition.XLim = [0 telute(end)];
                app.UIAxesMultiPosition.YLim = [0 1];
            end
            
            
            if contains(identifier, 'Export')
                individualCurves = array2table(Cout.', 'VariableNames', app.compoundList.Data(:,1));
                compiledData = [array2table(telute.'), individualCurves];

                inputsToSave = struct('FlowRate', app.FlowRate.Value, ...
                                  'ColumnVolume', app.ColumnVolume.Value, ...
                                  'Monitoring', app.VolumeTimeSwitch.Value, ...
                                  'MobilePhase', app.AscDesc.Value, ...
                                  'SfCoeff', app.StationaryPhaseSwitch.Value,...
                                  'NCoeff', app.ColumnEfficiencySwitch.Value, ...
                                  'ElutionDuration', app.ElutionDuration.Value, ...
                                  'Vd', app.ColumnDeadVolume.Value, ...
                                  'Vinj', app.InjectionVolume.Value, ...
                                  'VinjAddVd', app.includeInjectionVolCheckbox.Value, ...
                                  'ExtrusionDuration', app.ExtrusionDuration.Value, ...
                                  'DualDuration', app.DualDuration.Value);

                if string(app.StationaryPhaseSwitch.Value) == 'Set Sf'
                    inputsToSave.Sf = app.StationaryPhaseRetention.Value;

                elseif string(app.StationaryPhaseSwitch.Value) == 'Coeff.'
                    inputsToSave.SfA = app.SfCoefficientA.Value;
                    inputsToSave.SfB = app.SfCoefficientB.Value;
                end

                if string(app.ColumnEfficiencySwitch.Value) == 'Set N'
                    inputsToSave.N = app.ColumnEfficiencyN.Value;

                elseif string(app.ColumnEfficiencySwitch.Value) == 'Coeff.'
                    inputsToSave.NA = app.NCoefficientA.Value;
                    inputsToSave.NB = app.NCoefficientB.Value;
                    inputsToSave.NC = app.NCoefficientC.Value;
                end

                columnProperties = struct2table(inputsToSave);

                columnProperties = [columnProperties.Properties.VariableNames', struct2cell(inputsToSave)];
                compoundTable = [app.compoundList.ColumnName, app.compoundList.Data']';
                switchingTimes = [app.SwitchTimeList.ColumnName, app.SwitchTimeList.Data']';

                ExportIdentifier = erase(identifier, 'Export');
                filename = [ExportIdentifier + ' ' + app.VolumeTimeSwitch.Value + ' export ' + string(datetime)];

                [filename, directory] = uiputfile('.xlsx', 'Title for exported files?', filename);

                filename = strcat(directory, filename);

                writetable(compiledData, filename);
                writetable(cell2table(columnProperties), filename, 'Sheet', 2, 'WriteVariableNames', false);
                writetable(cell2table(compoundTable(:,1:4)), filename, 'Sheet', 2, 'Range', 'D1', 'WriteVariableNames', false);
                writetable(cell2table(switchingTimes), filename, 'Sheet', 2,'Range', 'I1', 'WriteVariableNames', false);

                [filepath,name,ext] = fileparts(filename);

                filename = strcat(filepath,'/',name,'.pdf');

                exportedPlot = sprintf('app.UIAxes' + ExportIdentifier);
                exportgraphics(eval(exportedPlot), filename, 'ContentType', 'vector');
            end

            app.addRetentionElutionToTable(peakPositions);
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

            % Create FileMenu
            app.FileMenu = uimenu(app.UIFigure);
            app.FileMenu.Text = 'File';

            % Create SaveMenu
            app.SaveMenu = uimenu(app.FileMenu);
            app.SaveMenu.Text = 'Save';
            app.SaveMenu.Accelerator = 'S';
            app.SaveMenu.MenuSelectedFcn = @(src,event) saveState(app);
            
            % Create OpenMenu
            app.OpenMenu = uimenu(app.FileMenu);
            app.OpenMenu.Text = 'Open';
            app.OpenMenu.Accelerator = 'O';
            app.OpenMenu.MenuSelectedFcn = @(src,event) loadState(app);

            % Create AboutMenu
            app.AboutMenu = uimenu(app.FileMenu);
            app.AboutMenu.Text = 'About';
            
            % Create TabGroup
            app.TabGroup = uitabgroup(app.UIFigure);
            app.TabGroup.Position = [725 0 717 500];

            % Create ElutionDurationLabelUnits
            app.ElutionDurationLabelUnits = uilabel(app.UIFigure);
            app.ElutionDurationLabelUnits.HorizontalAlignment = 'center';
            app.ElutionDurationLabelUnits.WordWrap = 'on';
            app.ElutionDurationLabelUnits.Position = [487 416 34 22];
            app.ElutionDurationLabelUnits.Text = 'min';
            
            % Create FlowRateLabelUnits
            app.FlowRateLabelUnits = uilabel(app.UIFigure);
            app.FlowRateLabelUnits.HorizontalAlignment = 'right';
            app.FlowRateLabelUnits.Position = [123 416 46 22];
            app.FlowRateLabelUnits.Text = 'mL/min';
            
            % Create FlowRateLabel
            app.FlowRateLabel = uilabel(app.UIFigure);
            app.FlowRateLabel.HorizontalAlignment = 'center';
            app.FlowRateLabel.WordWrap = 'on';
            app.FlowRateLabel.Position = [26 413 48 28];
            app.FlowRateLabel.Text = 'Flow Rate';
            
            % Create FlowRate
            app.FlowRate = uieditfield(app.UIFigure, 'numeric');
            app.FlowRate.LowerLimitInclusive = 'off';
            app.FlowRate.Limits = [0 Inf];
            app.FlowRate.RoundFractionalValues = 'off';
            app.FlowRate.Position = [73 416 51 22];
            app.FlowRate.Value = 5;
            
            % Create ColumnVolumeLabelUnits
            app.ColumnVolumeLabelUnits = uilabel(app.UIFigure);
            app.ColumnVolumeLabelUnits.HorizontalAlignment = 'right';
            app.ColumnVolumeLabelUnits.Position = [310 416 25 22];
            app.ColumnVolumeLabelUnits.Text = 'mL';
            
            % Create ColumnVolumeLabel
            app.ColumnVolumeLabel = uilabel(app.UIFigure);
            app.ColumnVolumeLabel.HorizontalAlignment = 'center';
            app.ColumnVolumeLabel.WordWrap = 'on';
            app.ColumnVolumeLabel.Position = [204 411 65 33];
            app.ColumnVolumeLabel.Text = 'Column Volume';
            
            % Create ColumnVolume
            app.ColumnVolume = uieditfield(app.UIFigure, 'numeric');
            app.ColumnVolume.LowerLimitInclusive = 'off';
            app.ColumnVolume.Limits = [0 Inf];
            app.ColumnVolume.RoundFractionalValues = 'off';
            app.ColumnVolume.Position = [268 416 44 22];
            app.ColumnVolume.Value = 81;
            
            % Create ElutionDurationLabel
            app.ElutionDurationLabel = uilabel(app.UIFigure);
            app.ElutionDurationLabel.HorizontalAlignment = 'center';
            app.ElutionDurationLabel.WordWrap = 'on';
            app.ElutionDurationLabel.Position = [378 413 55 30];
            app.ElutionDurationLabel.Text = 'Elution Duration';
            
            % Create ElutionDuration
            app.ElutionDuration = uieditfield(app.UIFigure, 'numeric');
            app.ElutionDuration.Position = [437 416 51 22];
            app.ElutionDuration.Value = 60;
            
            % Create InjectionVolumeLabelUnits
            app.InjectionVolumeLabelUnits = uilabel(app.UIFigure);
            app.InjectionVolumeLabelUnits.HorizontalAlignment = 'right';
            app.InjectionVolumeLabelUnits.Position = [656 416 25 22];
            app.InjectionVolumeLabelUnits.Text = 'mL';
            
            % Create InjectionVolumeLabel
            app.InjectionVolumeLabel = uilabel(app.UIFigure);
            app.InjectionVolumeLabel.HorizontalAlignment = 'center';
            app.InjectionVolumeLabel.WordWrap = 'on';
            app.InjectionVolumeLabel.Position = [550 413 65 30];
            app.InjectionVolumeLabel.Text = 'Injection Volume';
            
            % Create InjectionVolume
            app.InjectionVolume = uieditfield(app.UIFigure, 'numeric');
            app.InjectionVolume.LowerLimitInclusive = 'off';
            app.InjectionVolume.Limits = [0 Inf];
            app.InjectionVolume.Position = [614 416 44 22];
            app.InjectionVolume.Value = 1;
            
            % Create StationaryPhaseRetentionLabel
            app.StationaryPhaseRetentionLabel = uilabel(app.UIFigure);
            app.StationaryPhaseRetentionLabel.HorizontalAlignment = 'center';
            app.StationaryPhaseRetentionLabel.WordWrap = 'on';
            app.StationaryPhaseRetentionLabel.Position = [10 350 180 57];
            app.StationaryPhaseRetentionLabel.Text = 'Stationary Phase Retention';
            
            % Create StationaryPhaseRetention
            app.StationaryPhaseRetention = uieditfield(app.UIFigure, 'numeric');
            app.StationaryPhaseRetention.LowerLimitInclusive = 'off';
            app.StationaryPhaseRetention.UpperLimitInclusive = 'off';
            app.StationaryPhaseRetention.Limits = [0 1];
            app.StationaryPhaseRetention.Position = [72 345 51 22];
            app.StationaryPhaseRetention.Value = 0.75;

            % Create StationaryPhaseSwitch
            app.StationaryPhaseSwitch = uiswitch(app.UIFigure, 'slider', 'ValueChangedFcn',@(src,event) toggleStationaryAndPlot(app));
            app.StationaryPhaseSwitch.Items = {'Set Sf', 'Coeff.'};
            app.StationaryPhaseSwitch.Position = [75 320 45 20];
            app.StationaryPhaseSwitch.Value = 'Set Sf';
            app.StationaryPhaseSwitch.Tag = 'Switch';
            set(app.StationaryPhaseSwitch, 'Tooltip', 'Coefficients must be obtained from pulse tests for each solvent system at various flow rates.')
            
            % Create ColumnEfficiencyNLabel
            app.ColumnEfficiencyNLabel = uilabel(app.UIFigure);
            app.ColumnEfficiencyNLabel.HorizontalAlignment = 'center';
            app.ColumnEfficiencyNLabel.WordWrap = 'on';
            app.ColumnEfficiencyNLabel.Position = [230 350 200 57];
            app.ColumnEfficiencyNLabel.Text = 'Column Efficiency (N)';
            
            % Create ColumnEfficiencySwitch
            app.ColumnEfficiencySwitch = uiswitch(app.UIFigure, 'slider', 'ValueChangedFcn',@(src,event) toggleEfficiencyAndPlot(app));
            app.ColumnEfficiencySwitch.Items = {'Set N', 'Coeff.'};
            app.ColumnEfficiencySwitch.Position = [308 320 45 20];
            app.ColumnEfficiencySwitch.Value = 'Set N';
            app.ColumnEfficiencySwitch.Tag = 'Switch';
            set(app.ColumnEfficiencySwitch, 'Tooltip', 'Coefficients must be obtained from pulse tests for each solvent system at various flow rates.')
            
            % Create ColumnEfficiencyN
            app.ColumnEfficiencyN = uieditfield(app.UIFigure, 'numeric');
            app.ColumnEfficiencyN.UpperLimitInclusive = 'off';
            app.ColumnEfficiencyN.Limits = [1 Inf];
            app.ColumnEfficiencyN.Position = [305 345 51 22];
            app.ColumnEfficiencyN.Value = 400;

            % Create ColumnDeadVolumeLabelUnits
            app.ColumnDeadVolumeLabelUnits = uilabel(app.UIFigure);
            app.ColumnDeadVolumeLabelUnits.HorizontalAlignment = 'center';
            app.ColumnDeadVolumeLabelUnits.WordWrap = 'on';
            app.ColumnDeadVolumeLabelUnits.Position = [640 350 24 14];
            app.ColumnDeadVolumeLabelUnits.Text = 'mL';
            
            % Create ColumnDeadVolumeLabel
            app.ColumnDeadVolumeLabel = uilabel(app.UIFigure);
            app.ColumnDeadVolumeLabel.HorizontalAlignment = 'center';
            app.ColumnDeadVolumeLabel.WordWrap = 'on';
            app.ColumnDeadVolumeLabel.Position = [545 362 150 34];
            app.ColumnDeadVolumeLabel.Text = 'Column Dead Volume';
            
            % Create ColumnDeadVolume
            app.ColumnDeadVolume = uieditfield(app.UIFigure, 'numeric');
            app.ColumnDeadVolume.Limits = [0 Inf];
            app.ColumnDeadVolume.Position = [592 345 45 22];

            %Create includeInjectionVolCheckbox
            app.includeInjectionVolCheckbox = uicheckbox(app.UIFigure,...
                'Text', 'Include Inj. Vol.?',...
                'Value', 1,...
                'Position', [568 322 120 15]);
            
            % Create UITable
            initialRows = {'Compound 1' 1 1 0 0; 'Compound 2' 2 1 0 0};
            app.compoundList = uitable(app.UIFigure,'CellEdit',@(src,event) removeSpecificCompound(app), ...
                "ColumnName",{'Compound'; 'KD'; 'Conc. (g/L)'; 'Ret. Time (min)'; 'Delete?'}, ...
                "ColumnFormat",{'char' [] [] [] 'logical'}, ...
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

            % Create saveCompoundList
            app.saveCompoundList = uibutton(app.UIFigure,'ButtonPushedFcn',@(src,event) saveCompounds(app));
            app.saveCompoundList.Position = [17 140 40 25];
            app.saveCompoundList.Text = 'Save';

            % Create openCompoundList
            app.openCompoundList = uibutton(app.UIFigure,'ButtonPushedFcn',@(src,event) openCompounds(app));
            app.openCompoundList.Position = [17 107 40 25];
            app.openCompoundList.Text = 'Open';

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
            app.VolumeTimeSwitch.Position = [475 325 45 20];
            app.VolumeTimeSwitch.Orientation = 'vertical';
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
            app.UIAxesClassic.Position = [8 10 695 430];

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

            %Create ClassicPeaksCheckbox
            app.ClassicPeaksCheckbox = uicheckbox(app.ClassicElutionTab,...
                'Text', 'Peak Labels?',...
                'Value', 1,...
                'Position', [460 450 102 15]);

            %Create classicModelSumCheckbox
            app.classicModelSumCheckbox = uicheckbox(app.ClassicElutionTab,...
                'Text', 'Sum?',...
                'Value', 0,...
                'Position', [240 450 60 15]);

            % Create ElutionExtrusionTab
            app.ElutionExtrusionTab = uitab(app.TabGroup);
            app.ElutionExtrusionTab.Title = 'Elution-Extrusion';
            app.ElutionExtrusionTab.Tag = 'ExtrusionPlot';

            % Create UIAxesExtrusion
            app.UIAxesExtrusion = uiaxes(app.ElutionExtrusionTab);
            xlabel(app.UIAxesExtrusion, 'Elution Time')
            ylabel(app.UIAxesExtrusion, 'Concentration')
            zlabel(app.UIAxesExtrusion, 'Z')
            app.UIAxesExtrusion.Position = [8 10 695 430];

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

            %Create extrusionModelSumCheckbox
            app.extrusionModelSumCheckbox = uicheckbox(app.ElutionExtrusionTab,...
                'Text', 'Sum?',...
                'Value', 0,...
                'Position', [240 450 60 15]);

            %Create ExtrusionPeaksCheckbox
            app.ExtrusionPeaksCheckbox = uicheckbox(app.ElutionExtrusionTab,...
                'Text', 'Peak Labels?',...
                'Value', 1,...
                'Position', [460 450 102 15]);

            %Create ExtrusionLinesCheckbox
            app.ExtrusionLinesCheckbox = uicheckbox(app.ElutionExtrusionTab,...
                'Text', 'Lines?',...
                'Value', 1,...
                'Position', [560 450 102 15]);

            %Create ExtrusionLinesLabelsCheckbox
            app.ExtrusionLinesLabelsCheckbox = uicheckbox(app.ElutionExtrusionTab,...
                'Text', 'Labels?',...
                'Value', 1,...
                'Position', [620 450 102 15]);

            % Create dualModeTab
            app.dualModeTab = uitab(app.TabGroup);
            app.dualModeTab.Title = 'Dual Mode';
            app.dualModeTab.Tag = 'DualPlot';

            % Create UIAxesDual
            app.UIAxesDual = uiaxes(app.dualModeTab);
            xlabel(app.UIAxesDual, 'Elution Time')
            ylabel(app.UIAxesDual, 'Concentration')
            zlabel(app.UIAxesDual, 'Z')
            app.UIAxesDual.Position = [8 10 695 430];

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

            % Create DualDurationLabel
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

            %Create DualPeaksCheckbox
            app.DualPeaksCheckbox = uicheckbox(app.dualModeTab,...
                'Text', 'Peak Labels?',...
                'Value', 1,...
                'Position', [460 450 102 15]);

            %Create DualLinesCheckbox
            app.DualLinesCheckbox = uicheckbox(app.dualModeTab,...
                'Text', 'Lines?',...
                'Value', 1,...
                'Position', [560 450 102 15]);

            %Create DualLinesLabelsCheckbox
            app.DualLinesLabelsCheckbox = uicheckbox(app.dualModeTab,...
                'Text', 'Labels?',...
                'Value', 1,...
                'Position', [620 450 102 15]);

            % Create MultipleDualModeTab
            app.MultipleDualModeTab = uitab(app.TabGroup);
            app.MultipleDualModeTab.Title = 'Multiple Dual Mode';
            app.MultipleDualModeTab.Tag = 'MultiPlot';

            % Create UIAxesMulti
            app.UIAxesMulti = uiaxes(app.MultipleDualModeTab);
            xlabel(app.UIAxesMulti, 'Elution Time')
            ylabel(app.UIAxesMulti, 'Concentration')
            zlabel(app.UIAxesMulti, 'Z')
            app.UIAxesMulti.Position = [8 230 695 210];

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

            % Create saveSwitchTimes
            app.saveSwitchTimes = uibutton(app.MultipleDualModeTab,'ButtonPushedFcn',@(src,event) saveSwitchTimeList(app));
            app.saveSwitchTimes.Position = [11 62 25 25];
            app.saveSwitchTimes.Text = 'S';

            % Create openSwitchTimes
            app.openSwitchTimes = uibutton(app.MultipleDualModeTab,'ButtonPushedFcn',@(src,event) openSwitchTimeList(app));
            app.openSwitchTimes.Position = [11 29 25 25];
            app.openSwitchTimes.Text = 'O';

            %Create MultiPeaksCheckbox
            app.MultiPeaksCheckbox = uicheckbox(app.MultipleDualModeTab,...
                'Text', 'Peak Labels?',...
                'Value', 1,...
                'Position', [460 450 102 15]);

            %Create MultiLinesCheckbox
            app.MultiLinesCheckbox = uicheckbox(app.MultipleDualModeTab,...
                'Text', 'Lines?',...
                'Value', 1,...
                'Position', [560 450 102 15]);

            %Create MultiLinesLabelsCheckbox
            app.MultiLinesLabelsCheckbox = uicheckbox(app.MultipleDualModeTab,...
                'Text', 'Labels?',...
                'Value', 1,...
                'Position', [620 450 102 15]);

            % Create PulseTab
            app.PulseTab = uitab(app.TabGroup);
            app.PulseTab.Title = 'Pulse Test';
            app.PulseTab.Tag = 'Pulse';

            % Create ImportPulseTraceButton
            app.ImportPulseTraceButton = uibutton(app.PulseTab, 'ButtonPushedFcn',@(src,event) importTrace(app));
            app.ImportPulseTraceButton.Position = [40 445 68 23];
            app.ImportPulseTraceButton.Text = 'Import';
            app.ImportPulseTraceButton.Tag = 'ImportPulse';

            % Create UIAxesPulse
            app.UIAxesPulse = uiaxes(app.PulseTab);
            xlabel(app.UIAxesPulse, 'Elution Time')
            ylabel(app.UIAxesPulse, 'Concentration')
            zlabel(app.UIAxesPulse, 'Z')
            app.UIAxesPulse.Position = [8 10 450 430];

            % Create FindPulsePeaksButton
            app.FindPulsePeaksButton = uibutton(app.PulseTab, 'ButtonPushedFcn',@(src,event) findAndLabelPulsePeaks(app));
            app.FindPulsePeaksButton.Position = [415 445 68 23];
            app.FindPulsePeaksButton.Text = 'Find Peaks';
            app.FindPulsePeaksButton.Tag = 'FindPulse';

            % Create AddPulseNValue
            app.AddPulseNValue = uibutton(app.PulseTab, 'ButtonPushedFcn',@(src,event) addNValue(app));
            app.AddPulseNValue.Position = [490 445 68 23];
            app.AddPulseNValue.Text = 'Add N';
            app.AddPulseNValue.Tag = 'AddN';

            % Create SavePulseList
            app.SavePulseList = uibutton(app.PulseTab, 'ButtonPushedFcn',@(src,event) savePulseList(app));
            app.SavePulseList.Position = [606 445 40 23];
            app.SavePulseList.Text = 'Save';
            app.SavePulseList.Tag = 'saveN';

            % Create OpenPulseList
            app.OpenPulseList = uibutton(app.PulseTab, 'ButtonPushedFcn',@(src,event) openPulseList(app));
            app.OpenPulseList.Position = [653 445 40 23];
            app.OpenPulseList.Text = 'Open';
            app.OpenPulseList.Tag = 'OpenN';

            % Create PulseSpanLabel
            app.PulseSpanLabel = uilabel(app.PulseTab);
            app.PulseSpanLabel.HorizontalAlignment = 'right';
            app.PulseSpanLabel.Position = [120 445 30 22];
            app.PulseSpanLabel.Text = 'Span';

            % Create PulseSpan
            app.PulseSpan = uieditfield(app.PulseTab, 'numeric');
            app.PulseSpan.Position = [155 445 29 22];
            app.PulseSpan.Value = 40;
            app.PulseSpan.RoundFractionalValues = 1;
            app.PulseSpan.Limits = [2 1000];

            % Create PulseProminenceLabel
            app.PulseProminenceLabel = uilabel(app.PulseTab);
            app.PulseProminenceLabel.HorizontalAlignment = 'right';
            app.PulseProminenceLabel.Position = [197 445 65 22];
            app.PulseProminenceLabel.Text = 'Prominence';

            % Create PulseProminence
            app.PulseProminence = uieditfield(app.PulseTab, 'numeric');
            app.PulseProminence.Position = [267 445 29 22];
            app.PulseProminence.Value = 5;

            % Create PulseBaselineLabel
            app.PulseBaselineLabel = uilabel(app.PulseTab);
            app.PulseBaselineLabel.HorizontalAlignment = 'right';
            app.PulseBaselineLabel.Position = [297 445 65 22];
            app.PulseBaselineLabel.Text = 'Baseline';

            % Create PulseBaseline
            app.PulseBaseline = uieditfield(app.PulseTab, 'numeric');
            app.PulseBaseline.Position = [367 445 29 22];
            app.PulseBaseline.Value = 5;

            % Create PulseNTableListLabel
            app.PulseNTableListLabel = uilabel(app.PulseTab);
            app.PulseNTableListLabel.HorizontalAlignment = 'center';
            app.PulseNTableListLabel.FontSize = 18;
            app.PulseNTableListLabel.FontWeight = 'bold';
            app.PulseNTableListLabel.Position = [515 412 137 24];
            app.PulseNTableListLabel.Text = 'Pulse Test List';

            % Create PulseNTable
            app.PulseNList = uitable(app.PulseTab,'CellEdit',@(src,event) removeSpecificNValue(app), ...
                "ColumnWidth",{82, 44, 58, 50}, ...
                "ColumnName",{'Flow Rate'; 'Sf'; 'N'; 'Del?'}, ...
                "ColumnFormat",{[] [] [] 'logical'});
            app.PulseNList.RowName = {};
            addStyle(app.PulseNList, tableStyle);
            app.PulseNList.ColumnSortable = true;
            app.PulseNList.ColumnEditable = true;
            app.PulseNList.Position = [473 204 220 200];

            % Create regressionHeader
            app.regressionHeader = uilabel(app.PulseTab);
            app.regressionHeader.HorizontalAlignment = 'left';
            app.regressionHeader.FontSize = 12;
            app.regressionHeader.Position = [475 175 137 24];
            app.regressionHeader.Text = 'Regressions:';

            % Create NEquationLabel
            app.NEquationLabel = uilabel(app.PulseTab);
            app.NEquationLabel.HorizontalAlignment = 'left';
            app.NEquationLabel.FontSize = 12;
            app.NEquationLabel.Interpreter = 'latex';
            app.NEquationLabel.Position = [475 150 150 24];
            app.NEquationLabel.Text = '$N = A + BF + CF^2$';
            set(app.NEquationLabel, 'Tooltip', 'B coefficient is typically negative.')
            
            % Create useNButton
            app.useNButton = uibutton(app.PulseTab, 'ButtonPushedFcn',@(src,event) useNValues(app));
            app.useNButton.Position = [625 150 68 23];
            app.useNButton.Text = 'Use Values';
            app.useNButton.Tag = 'UseN';
            
            % Create labelNA
            app.labelNA = uilabel(app.PulseTab);
            app.labelNA.HorizontalAlignment = 'left';
            app.labelNA.FontSize = 12;
            app.labelNA.Position = [475 120 150 24];
            app.labelNA.Text = 'A: ';
            
            % Create labelNB
            app.labelNB = uilabel(app.PulseTab);
            app.labelNB.HorizontalAlignment = 'left';
            app.labelNB.FontSize = 12;
            app.labelNB.Position = [550 120 150 24];
            app.labelNB.Text = 'B: ';
            
            % Create labelNC
            app.labelNC = uilabel(app.PulseTab);
            app.labelNC.HorizontalAlignment = 'left';
            app.labelNC.FontSize = 12;
            app.labelNC.Position = [625 120 150 24];
            app.labelNC.Text = 'C: ';
            
            % Create SfEquationLabel
            app.SfEquationLabel = uilabel(app.PulseTab);
            app.SfEquationLabel.HorizontalAlignment = 'left';
            app.SfEquationLabel.FontSize = 12;
            app.SfEquationLabel.Interpreter = 'latex';
            app.SfEquationLabel.Position = [475 85 150 24];
            app.SfEquationLabel.Text = '$S_{f} = A + BF$';
            set(app.SfEquationLabel, 'Tooltip', 'B coefficient is typically negative.')

            % Create useSfButton
            app.useSfButton = uibutton(app.PulseTab, 'ButtonPushedFcn',@(src,event) useSfValues(app));
            app.useSfButton.Position = [625 85 68 23];
            app.useSfButton.Text = 'Use Values';
            app.useSfButton.Tag = 'UseSf';

            % Create labelSfA
            app.labelSfA = uilabel(app.PulseTab);
            app.labelSfA.HorizontalAlignment = 'left';
            app.labelSfA.FontSize = 12;
            app.labelSfA.Position = [475 55 150 24];
            app.labelSfA.Text = 'A: ';

            % Create labelSfB
            app.labelSfB = uilabel(app.PulseTab);
            app.labelSfB.HorizontalAlignment = 'left';
            app.labelSfB.FontSize = 12;
            app.labelSfB.Position = [550 55 150 24];
            app.labelSfB.Text = 'B: ';

            % Create FittingTab
            app.FitTab = uitab(app.TabGroup);
            app.FitTab.Title = 'Trace Fitting';
            app.FitTab.Tag = 'Fit';

            % Create UIAxesFit
            app.UIAxesFit = uiaxes(app.FitTab);
            xlabel(app.UIAxesFit, 'Elution Time')
            ylabel(app.UIAxesFit, 'Concentration')
            zlabel(app.UIAxesFit, 'Z')
            app.UIAxesFit.Position = [8 10 695 430];
            
            % Create ImportTraceButton
            app.ImportTraceButton = uibutton(app.FitTab, 'ButtonPushedFcn',@(src,event) importTrace(app));
            app.ImportTraceButton.Position = [40 445 68 23];
            app.ImportTraceButton.Text = 'Import';
            app.ImportTraceButton.Tag = 'ImportFit';

            % Create FitSpanLabel
            app.FitSpanLabel = uilabel(app.FitTab);
            app.FitSpanLabel.HorizontalAlignment = 'right';
            app.FitSpanLabel.Position = [120 445 30 22];
            app.FitSpanLabel.Text = 'Span';

            % Create FitSpan
            app.FitSpan = uieditfield(app.FitTab, 'numeric');
            app.FitSpan.Position = [155 445 29 22];
            app.FitSpan.Value = 20;
            app.FitSpan.RoundFractionalValues = 1;
            app.FitSpan.Limits = [2 1000];

            % Create FitProminenceLabel
            app.FitProminenceLabel = uilabel(app.FitTab);
            app.FitProminenceLabel.HorizontalAlignment = 'right';
            app.FitProminenceLabel.Position = [197 445 65 22];
            app.FitProminenceLabel.Text = 'Prominence';

            % Create FitProminence
            app.FitProminence = uieditfield(app.FitTab, 'numeric');
            app.FitProminence.Position = [267 445 29 22];
            app.FitProminence.Value = 5;

            % Create FitThresholdLabel
            app.FitThresholdLabel = uilabel(app.FitTab);
            app.FitThresholdLabel.HorizontalAlignment = 'right';
            app.FitThresholdLabel.Position = [297 445 65 22];
            app.FitThresholdLabel.Text = 'Threshold';

            % Create FitThreshold
            app.FitThreshold = uieditfield(app.FitTab, 'numeric');
            app.FitThreshold.Position = [367 445 29 22];
            app.FitThreshold.Value = 5;

            % Create FindFitPeaksButton
            app.FindFitPeaksButton = uibutton(app.FitTab, 'ButtonPushedFcn',@(src,event) findAndLabelFitPeaks(app));
            app.FindFitPeaksButton.Position = [415 445 68 23];
            app.FindFitPeaksButton.Text = 'Find Peaks';
            app.FindFitPeaksButton.Tag = 'FindFit';

            % Create ComputeKDValues
            app.ComputeKDValues = uibutton(app.FitTab, 'ButtonPushedFcn',@(src,event) updateCompoundListWithFits(app));
            app.ComputeKDValues.Position = [490 445 68 23];
            app.ComputeKDValues.Text = 'Send KDs';
            app.ComputeKDValues.Tag = 'SendFit';

            %Create DisplayWithModelingCheckbox
            app.DisplayWithModeling = uicheckbox(app.FitTab,...
                'Text', 'Overlay on Models?',...
                'Value', 0,...
                'Position', [570 449 130 15]);
            set(app.DisplayWithModeling, 'Tooltip', 'Currently only displays on Classic or Elution-Extrusion models.')
            
            % Create appInfoTab
            app.Info = uitab(app.TabGroup);
            app.Info.Title = 'App Info';
            app.Info.Tag = 'Info';

            app.InfoTitle = uilabel(app.Info);
            app.InfoTitle.HorizontalAlignment = 'center';
            app.InfoTitle.FontSize = 24;
            app.InfoTitle.FontWeight = 'bold';
            app.InfoTitle.Position = [140 320 500 50];
            app.InfoTitle.Text = 'CUP Modeler';

            app.InfoVersion = uilabel(app.Info);
            app.InfoVersion.HorizontalAlignment = 'center';
            app.InfoVersion.FontSize = 18;
            app.InfoVersion.Position = [140 305 500 25];
            app.InfoVersion.Text = 'Version 1.0';

            app.InfoCitation = uilabel(app.Info);
            app.InfoCitation.HorizontalAlignment = 'center';
            app.InfoCitation.FontSize = 12;
            app.InfoCitation.Position = [85 270 500 20];
            app.InfoCitation.Text = 'To learn more, ';
            
            app.InfoCredits = uilabel(app.Info);
            app.InfoCredits.HorizontalAlignment = 'center';
            app.InfoCredits.FontSize = 12;
            app.InfoCredits.Position = [140 250 500 20];
            app.InfoCredits.Text = 'Mathematical modeling by Hoon Choi. Interface by Manar Alherech.';

            app.cupPaper = uihyperlink(app.Info);
            app.cupPaper.Text = 'check out our work.';
            app.cupPaper.URL = 'https://www.sciencedirect.com/science/article/pii/S1383586621020347';
            app.cupPaper.Position = [375 270 300 20];
            
            app.AscDescLabel = uilabel(app.UIFigure);
            app.AscDescLabel.HorizontalAlignment = 'center';
            app.AscDescLabel.FontSize = 12;
            app.AscDescLabel.Position = [665 190 50 30];
            app.AscDescLabel.Text = 'Mobile Phase';
            app.AscDescLabel.WordWrap = 'on';

            % Create Switch
            app.AscDesc = uiswitch(app.UIFigure, 'slider', 'ValueChangedFcn',@(src,event) CUPPrediction(app));
            app.AscDesc.Items = {'Lower', 'Upper'};
            app.AscDesc.Position = [680 120 45 20];
            app.AscDesc.Orientation = 'vertical';
            app.AscDesc.Value = 'Lower';
            app.AscDesc.Tag = 'Switch';
            
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