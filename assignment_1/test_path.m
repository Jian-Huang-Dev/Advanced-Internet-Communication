%--------------------------------------------------------------------
% put the next code into a matlab file called ?test_path.m?
% function ?test_path()? will test if a flow with a requested rate  in 
% packets-per-second can be routed in a network.
% Lambda is a matrix of edge loads (in packets per second)
% Mu is a matrix of edge capacities (in packets per second)
%----------------------------------------------------------------------
function  path_delay = test_path(path, rate, Lambda, Mu)
path_delay = 0;

[r,c] = size(path);

%---------------------------------------------------------------
% path_delay  = sum of the delay on each edge in the path
% the path is a row vector (1 row with several columns).
%----------------------------------------------------------------
for index = 1:(c-1)
     u = path(index);
     v = path(index+1);

	%---------------------------------------------------------------
	% find the delay on this edge in the path
	%----------------------------------------------------------------
	if ( Mu(u,v) > 0 ) && (Mu(u,v) - (Lambda(u,v) + rate) > 0)
		edge_delay = 1/(Mu(u,v) - (Lambda(u,v) + rate));
		path_delay = path_delay + edge_delay;
	else
		% fprintf('cannot route the traffic flow with rate %g along the path!\n');
		path_delay = inf;   % set the delay to infinity
		return;
	end;
end;

