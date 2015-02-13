function [alloc_rate, sess_delay] = output( best_flow_orders, TOP, W, N )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

% initialization
alloc_rate = zeros(1,36);
sess_delay = zeros(1,36);
define_flows
Mu = zeros(N,N);
Mu = TOP * 1000;
Lambda 	= zeros(N,N);
% same for this assignment
W = TOP; 
% number of paths routed (max 36 paths will be routed)
num_flows_routed = 0;
current_num_flows_routed = 0;

for i = best_flow_orders
        % obtain the hops from the best path which from src to the dest
        % node
        [HOPs] = path(FLOW(i,1), FLOW(i,2), TOP, W, N );
        path_delay = test_path(HOPs, 800, Lambda, Mu);
        
        if (path_delay <= 0.05) % if path delay is less than 50 milli-seconds
            % route path, and update the paths for which being occupied 
            [path_delay, Lambda] = route_path(HOPs, 800, Lambda, Mu); 
            % update number of flows being routed
            current_num_flows_routed = current_num_flows_routed + 1;
            % update the allocated rate at the specific flow
            alloc_rate(i) = 800;
            sess_delay(i) = path_delay;
        else % the path delay exceeded requirements! 
            % update the allocated rate at the specific flow
            alloc_rate(i) = 0;
            sess_delay(i) = path_delay;
        end
        
        % update to the largest number of flows being routed (36 max)
        if (current_num_flows_routed > num_flows_routed)
            % update
            num_flows_routed = current_num_flows_routed;
        end
    end

end

