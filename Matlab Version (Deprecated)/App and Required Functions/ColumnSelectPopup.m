function userInput = ColumnSelectPopup(importedData)
    userInput = [];
    columnSelectFig = uifigure('Name','Column Selection', 'Position', [300 250 1000 500]);

    dataPreviewTable = uitable(columnSelectFig);

    dataPreviewTable.Position = [20 75 960 400];
    dataPreviewTable.ColumnWidth = '1x';
    
    uilabel(columnSelectFig, 'Text', 'X Data (Time)', 'Position', [323 23 100 25]);
    xColumn = uieditfield(columnSelectFig, 'numeric', 'RoundFractionalValues', 1, 'Limits', [1 Inf], 'AllowEmpty', 0, 'Value', 1, 'Position', [400 25 22 20]);
    
    uilabel(columnSelectFig, 'Text', 'Y Data (Abs.)', 'Position', [435 23 100 25]);
    yColumn = uieditfield(columnSelectFig, 'numeric', 'RoundFractionalValues', 1, 'Limits', [1 Inf], 'AllowEmpty', 0, 'Value', 2, 'Position', [512 25 22 20]);
    
    uibutton(columnSelectFig, 'Text', 'Select', 'Position', [550 22 50 25], 'ButtonPushedFcn', @onSubmit);
    
    dataPreviewTable.Data = importedData';
    
    uiwait(columnSelectFig);

    function onSubmit (~,~)
        userInput = [xColumn.Value, yColumn.Value];
        close(columnSelectFig);
    end
end