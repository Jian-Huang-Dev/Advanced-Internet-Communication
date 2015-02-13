%-------------------------------------------------------------------------
% put the next code into a matlab file called ?find_network_delay.m?
% function  find_network_delay() will return the delay matrix 
% Delay(i,j) = delay on link(i,j) in the network
%-------------------------------------------------------------------------
function [Delay]  = find_network_delay(Lambda, Mu)

[rows,cols] = size(Lambda);   % find the # rows and # columns in the Lambda matrix
Delay = zeros(rows,cols);       % initialize the Delay matrix to return zeros

for u = 1:rows
	for v = 1:cols
		%---------------------------------------------------------------
		% if this edge (row,col) exists, then it has a non-zero Mu(row,col)		
		% find the delay; assume that Lambda(row,col) is 0 or positive
		%----------------------------------------------------------------
        if (Lambda(u,v) == 0)
			Delay(u,v)  = 0;
        elseif ( Mu(u,v) > 0 ) && (Lambda(u,v) < Mu(u,v))
			Delay(u,v)  = 1 / ( Mu(u,v) - Lambda(u,v) );
		elseif ( Mu(u,v) > 0 ) && (Lambda(u,v) >= Mu(u,v))
			% according to our delay formula, the M/M/1 queueing delay is infinite
			Delay(u,v) = inf;
		end;
	end;
end;
	
