% script plot_graph

% visit every node and draw it on the graoph
for ii=1:N
    x1 = LOC(ii,1);
    y1 = LOC(ii,2);
    x_vector = [x1, x1];
    y_vector = [y1, y1];
    plot(x_vector, y_vector, 'ok', 'Linewidth', 5)
    hold on;
end
 
% draw every edge
for ii=1:N
    for jj=1:N
        if (TOP(ii,jj) == 1)
            % Ok, we found an edge (ii,jj)
            x1 = LOC(ii,1);
            x2 = LOC(jj,1);
            x_vector = [x1, x2];
            
            y1 = LOC(ii,2);
            y2 = LOC(jj,2);
            y_vector = [y1, y2];
            
            plot(x_vector, y_vector, 'k');
            hold on;
        end;
    end;
end;