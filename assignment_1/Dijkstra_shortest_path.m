function [ D, P ] = Dijkstra_shortest_path( src, W )

% get the size of weight matrix
[N, N] = size(W);

D = ones(1, N) * inf;
P = ones(1, N) * inf;

% unvisited nodes
U = ones(1, N);
% src node is visited initiallly
U(src) = 0;
D(1, src) = 0;

end

