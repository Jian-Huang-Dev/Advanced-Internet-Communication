%-------------------------------------------------------------------------------
% This function will return all the hops (include source and destination
% nodes from the best shortest path
%-
function [HOPs] = path(src, dst, TOP, W, N )

% use part A's function to find the predecessor node and distance
[D,P] = Dijkstra_shortest_path (src, TOP, W, N);
dist = D(dst);
% total hops is equal to the nuber of edges plus 1
total_hops = dist + 1;
% initialize a matrix to hold the elements of hops
HOPs = zeros(1,total_hops);
% the last node of the matrix is the destination node
HOPs(total_hops)=dst;

i = total_hops;

% while the predecessor node is not the node itself (infinity)
while P(dst) ~= inf
    % update the destination node 
    % follow the precessor route back to the source
    dst=P(dst);
    % in descending order
    % put first element as the source node, while the destination node at
    % the last
    i = i - 1;
    HOPs(i) = dst;
    
end