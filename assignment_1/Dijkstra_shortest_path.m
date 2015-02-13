%--------------------------------------------------------------------------
% BASIC DIJKSTRA'S SHORTEST PATH
%--------------------------------------------------------------------------
% return vector D,where D(1,j) == shortest distance between (src,j)
% return vecotr P,where P(j) is predecessor node on the shortest
%path from node j to the source
%--------------------------------------------------------------------------


function [D,P] = Dijkstra_shortest_path(src, T, W, N)

D = inf * ones(1,N);

P = inf * ones(1,N);

UV = ones(1,N); %all node labelled unvisited initially

UV(src) = 0; 

D(1,src) = 0;

pass = 1;

v = src;

while pass < 16

    for i = 1:N 
          
        
        if UV(i) == 1 && T(v,i) == 1
            if D(v)+ W(v,i) < D(i)
                D(i) = D(v)+ W(v,i);
                P(i) = v;
            end
        end
        
    end
    
    UV(v) = 0;
    pass = pass + 1; 
    v = Find_Closest_Node(UV,D,N);
    
end

end

function next_node = Find_Closest_Node(UV,D,N)

min_dis = inf;
next_node = 0;

for u = 1:N
    if UV(u) == 1 
        if D(u) < min_dis
            min_dis = D(u);
            next_node = u;
        end
    end
end
end

