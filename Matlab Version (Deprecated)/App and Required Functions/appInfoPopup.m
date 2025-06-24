function appInfoPopup()
    appInfoFig = uifigure('Name','App Info', 'Position', [500 400 500 250]);
    
    uibutton(appInfoFig, 'Text', 'Close', 'Position', [230 22 50 25], 'ButtonPushedFcn', @onClick);

    app.InfoTitle = uilabel(appInfoFig);
    app.InfoTitle.HorizontalAlignment = 'center';
    app.InfoTitle.FontSize = 24;
    app.InfoTitle.FontWeight = 'bold';
    app.InfoTitle.Position = [130 170 250 50];
    app.InfoTitle.Text = 'CUP Modeler';

    app.InfoVersion = uilabel(appInfoFig);
    app.InfoVersion.HorizontalAlignment = 'center';
    app.InfoVersion.FontSize = 18;
    app.InfoVersion.Position = [130 155 250 25];
    app.InfoVersion.Text = 'Version 1.0';

    app.InfoCitation = uilabel(appInfoFig);
    app.InfoCitation.HorizontalAlignment = 'center';
    app.InfoCitation.FontSize = 12;
    app.InfoCitation.Position = [75 120 250 20];
    app.InfoCitation.Text = 'To learn more, ';
    
    app.InfoCredits = uilabel(appInfoFig);
    app.InfoCredits.HorizontalAlignment = 'center';
    app.InfoCredits.FontSize = 12;
    app.InfoCredits.Position = [70 100 370 20];
    app.InfoCredits.Text = 'Mathematical modeling by Hoon Choi. Interface by Manar Alherech.';

    app.cupPaper = uihyperlink(appInfoFig);
    app.cupPaper.Text = 'check out our work.';
    app.cupPaper.URL = 'https://www.sciencedirect.com/science/article/pii/S1383586621020347';
    app.cupPaper.Position = [240 120 300 20];
    
    uiwait(appInfoFig);

    function onClick (~,~)
        close(appInfoFig);
    end
end