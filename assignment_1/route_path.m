%----------------------------------------------------------------------
% put the next code into a function file called ?route_path.m?
% function ?route_path()? will route a traffic flow with a requested rate  in
% packets-per-second in a network. Assume the network can accommodate the path.
% Lambda is a matrix of edge loads (in packets per second)
% Mu is a matrix of edge capacities (in packets per second)
%----------------------------------------------------------------------

function [path_delay, Lambda]  = route_path(path, rate, Lambda, Mu)
path_delay = 0;
[r,c] = size(path);

%---------------------------------------------------------------
% route the traffic flow along the path
% the path is a row vector (1 row with several columns).
%----------------------------------------------------------------
for index =1: (c-1)
    u = path(index);
    v = path(index+ 1);

	%---------------------------------------------------------------
	% ensure that the delay on this edge in the path is finite
	%----------------------------------------------------------------
	if ( Mu(u,v) > 0 ) && (Mu(u,v) > (Lambda(u,v) + rate))
        
		Lambda(u,v) = Lambda(u,v) + rate;
        
		edge_delay = 1/(Mu(u,v) - Lambda(u,v) );
		path_delay = path_delay + edge_delay;
        
        
	else
		fprintf('ERROR: cannot route the  traffic flow along the path! \n');
		path_delay = inf;   % set the delay to infinity
		return;
	end;
end;
