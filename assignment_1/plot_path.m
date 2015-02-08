%--------------------------------------------------------------------
% plot_path
%----------------------------------------------------------------------
function  plot_path(path, NEW_COLOR)

global LOC;

persistent LAST_COLOR;
if (isempty(LAST_COLOR))
    LAST_COLOR = 0;
end;

[r,c] = size(path);

color_vector1 = ['r'; 'b'; 'g'; 'k'; 'c'; 'm'];
color_vector2 = ['r--'; 'b--'; 'g--'; 'k--'; 'c--'; 'm--'];
color_vector3 = ['r:'; 'b:'; 'g:'; 'k:'; 'c:'; 'm:'];


if (NEW_COLOR == 1)
    LAST_COLOR = LAST_COLOR + 1;
    if (LAST_COLOR > 18)
        LAST_COLOR = 1;
    end
    if (LAST_COLOR <= 6)
        color_string = color_vector1(LAST_COLOR);
    elseif (LAST_COLOR <= 12)
        color_string = color_vector2(LAST_COLOR-6);
    elseif (LAST_COLOR <= 18)
        color_string = color_vector3(LAST_COLOR-12);
    end;

    fprintf('color = %g, string = %s\n', LAST_COLOR, color_string);
end;



 if (LAST_COLOR <= 6)
        color_string = color_vector1(LAST_COLOR);
    elseif (LAST_COLOR <= 12)
        color_string = color_vector2(LAST_COLOR-6);
    elseif (LAST_COLOR <= 18)
        color_string = color_vector3(LAST_COLOR-12);
    end;
    
%---------------------------------------------------------------
% path_delay  = sum of the delay on each edge in the path
% the path is a row vector (1 row with several columns).
%----------------------------------------------------------------
for index =1:(c-1)
     u = path(index);
     v = path(index+1);

     x1 = LOC(u,1);
     y1 = LOC(u,2);
     x2 = LOC(v,1);
     y2 = LOC(v,2);
    
     
     plot([x1,x2], [y1,y2], color_string, 'LineWidth', 2);
     hold on;
	
end;

