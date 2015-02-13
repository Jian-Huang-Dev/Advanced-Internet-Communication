%-------------------------------------------------------------------------------
% 4DN4: sample matlab code for  assignment #1. 
% put the next code into a matlab file called "MAIN_Assignment_1.m'
%-------------------------------------------------------------------------------

clear all;
clc;

N = 15; 
Mu = zeros(N,N);

% call a matlab script to read in the topology matrix
script_SPRINT_TOPOLOGY
define_flows

% call a script to plot the graph
% figure(1);
% clf
% set(gca,'FontSize',  15);
% title('Topology graph');
% plot_graph
% 
% figure(2)
% bar3(TOP)
% title('Topology Matrix');
% create a lambda and mu matrix with one entry each
Mu = TOP * 1000;
% same for this assignment
W = TOP; 
% number of paths routed (max 36 paths will be routed)
num_flows_routed = 0;
% number of loops
num_loops = 100;  

for loops = 1 : num_loops
    % initialization
    current_num_flows_routed = 0;
    Lambda 	= zeros(N,N); 
    Delay = zeros(N,N);
    % to obtain a random matrix on the provided flows chart
    rand_flow_orders = randperm(36);
    
    % loop every flow in the define_flow.m file, but in a random manner
    for i = rand_flow_orders
        % obtain the hops from the best path which from src to the dest
        % node
        [HOPs] = path(FLOW(i,1), FLOW(i,2), TOP, W, N );
        path_delay = test_path(HOPs, 800, Lambda, Mu);
        
        if (path_delay <= 0.05) % if path delay is less than 50 milli-seconds
            % route path, and update the paths for which being occupied 
            [path_delay, Lambda] = route_path(HOPs, 800, Lambda, Mu);
            % update number of flows being routed
            current_num_flows_routed = current_num_flows_routed + 1;
        else % the path delay exceeded requirements! 
            % nothing
        end
        
        % update to the largest number of flows being routed (36 max)
        if (current_num_flows_routed > num_flows_routed)
            % update
            num_flows_routed = current_num_flows_routed;
            % record the best flows
            best_flow_orders = rand_flow_orders;
        end
    end
end
    
fprintf('Best number of flows routed: %g\n', num_flows_routed);
% print off the best flow orders
best_orders_of_flows = sym(best_flow_orders)

% print off the paths taken
for i = best_flow_orders
    [HOPs] = path(FLOW(i,1), FLOW(i,2), TOP, W, N );
    fprintf('flow(%g):\n', i);
    HOPs
end

% print off the allocated rate and session delay for each path
[alloc_rate, sess_delay] = output( best_flow_orders, TOP, W, N );
allocated_rate = sym(alloc_rate)
session_delay = sym(sess_delay)

% try routing  the first traffic flow along path [1,2,6]
% path = [1, 2, 6];
% path_delay = test_path(path, 800, Lambda, Mu);
% 
% if (path_delay <= 0.05)
% 	[path_delay, Lambda] = route_path(path, 800, Lambda, Mu)
% 	fprintf('\nRouted flow #1 along path: ');
% 	fprintf('%g ', path);  % this statement prints all the nodes onto one line
% 	fprintf('\n');               % this statement starts a new line
% end;
% 
% % route a second path
% path = [1,9, 8, 11];
% path_delay = test_path(path, 800, Lambda, Mu);
% 
% if (path_delay <= 0.05)
% 	[path_delay, Lambda] = route_path(path, 800, Lambda, Mu);
% 	fprintf('\nRouted flow #2 along path: ');
% 	fprintf('%g ', path);  % this statement prints all the nodes onto one line
% 	fprintf('\n');               % this statement starts a new line
% end;
% 
% Delay  = find_network_delay(Lambda, Mu);
% 
% fprintf('Here is the Lambda matrix  (rates in 1000 pps) \n');
% print_matrix ( Lambda/1000 );
% 
% fprintf('Here is the Mu matrix  (rates in 1000 pps) \n');
% print_matrix ( Mu/1000 );
% 
% fprintf('Here is the Delay matrix  (in millisec) \n');
% print_matrix ( Delay*1000 );
% the rest is up to you

