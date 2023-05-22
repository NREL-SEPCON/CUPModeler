function [Purity integralRanges] = MyAreaCalc(telute, Cout)

    telute = telute';
    Cout = Cout';

    numCompounds = size(Cout, 2);
    
    yareas = zeros(1, numCompounds);
    integralRanges = zeroes(1, numCompounds);
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
        y = Cout(:, i);
        
        % Find the indices where the signal is above the baseline
        ind = find(y > Bot);
        
        % Determine the start and end indices for the time range
        startIdx = ind(1);
        endIdx = ind(end);
        
        % Extract the portion of the signal within the defined time range
        yrange = y(Bot:max(y));
        
        % Calculate the peak area within the time range
        yarea = trapz(telute(startIdx:endIdx), yrange);
        edges = [startIdx, endIdx, max(y)];
        integralRanges(i) = edges;
        yareas(i) = yarea;
    end
    
    
    for i = 1:numCompounds
        targetCurve = integralRanges(i);
        targetStartIdx = targetCurve(1);
        targetEndIdx = targetCurve(2);
        
        totalImpurityArea = 0;
        
        for j = 1:numCompounds
            if i == j
                %do nothing
            else
                y = Cout(:, j);
                yrange = y(Bot:max(y));
                totalImpurityArea = totalImpurityArea + trapz(telute(targetStartIdx:targetEndIdx), yrange);

                %{
                currentCurve = integralRanges(j);
                currentStartIdx = targetCurve(1);
                currentEndIdx = targetCurve(2);
                currentTop = targetCurve(3);
                
                if targetEndIdx < currentStartIdx %target peak is totally behind the comparison peak
                    %do nothing
                elseif targetStartIdx > currentEndIdx %target peak is totally after the comparison peak
                    %do nothing
                elseif targetStartIdx < currentStartIdx & targetEndIdx > currentEndIdx %impurity is totally inside target
                    totalImpurityArea = totalImpurityArea + yareas(j);

                elseif targetStartIdx > currentStartIdx & targetEndIdx < currentEndIdx %target is totally inside impurity
                    yrange = y(Bot:currentTop);
                    impurityOverlap = trapz(telute(targetStartIdx:targetEndIdx), yrange);
                    totalImpurityArea = totalImpurityArea + impurityOverlap;

                elseif targetEndIdx > currentStartIdx %impurity co-elutes with tail of target
                    yrange = y(Bot:currentTop);
                    impurityOverlap = trapz(telute(currentStartIdx:targetEndIdx), yrange);
                    totalImpurityArea = totalImpurityArea + impurityOverlap;

                elseif currentEndIdx > targetStartIdx %impurity co-elutes with beginning of target
                    yrange = y(Bot:currentTop);
                    impurityOverlap = trapz(telute(targetStartIdx:currentEndIdx), yrange);
                    totalImpurityArea = totalImpurityArea + impurityOverlap;
                end
                %}
            end
        end

        Purity(i) = (yareas(i) / (yareas(i) + totalImpurityArea)) * 100;
    end

end