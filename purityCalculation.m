function [Purity integralRanges] = purityCalculation(telute, Cout)

    telute = telute';
    Cout = Cout';

    numCompounds = size(Cout, 2);
    
    integralRanges = repmat({{}}, numCompounds, 1);
    Purity = zeros(1, numCompounds);

    Bot = inf;

    for i = 1:numCompounds
        y = Cout(:, i);

        if 0.005 * max(y) < Bot
            % Find the baseline (Bot) as a percentage of the peak height (1% = 0.01)
            Bot = 0.005 * max(y);
        end
    end

    
    for i = 1:numCompounds
        totalImpurityArea = 0;
        y = Cout(:, i);
        ind = find(y > Bot);
        
        yarea = trapz(telute(ind(1):ind(end)), y(ind(1):ind(end)));

        for j = 1:numCompounds
            if i ~= j
                yImp = Cout(:, j);
                totalImpurityArea = totalImpurityArea + trapz(telute(ind(1):ind(end)), yImp(ind(1):ind(end)));
            end
        end
        compoundPurity = (yarea / (yarea + totalImpurityArea)) * 100;
        Purity(i) = round(compoundPurity, 2);

    end

end