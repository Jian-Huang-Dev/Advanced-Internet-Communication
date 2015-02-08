%-------------------------------------------------------------------------------
% 4DN4: sample matlab code for  assignment #1. 
% put the next code into a matlab file called "MAIN_Assignment_1.m'
%-------------------------------------------------------------------------------

clear all;
clc;

N       = 15;
Lambda 	= zeros(N,N);   % create an 8x8 matrix of zeros
Mu        	= zeros(N,N);
Delay  		= zeros(N,N);

% call a matlab script to read in the topology matrix
script_SPRINT_TOPOLOGY

% call a script to plot the graph
figure(1);
clf
set(gca,'FontSize', 15);

plot_graph

% create a lambda and mu matrix with one entry each
Mu = TOP * 1000;

% try routing  the first traffic flow along path [1,2,6]
path = [1, 2, 6];
path_delay = test_path(path, 800, Lambda, Mu);

if (path_delay <= 0.05)
	[path_delay, Lambda] = route_path(path, 800, Lambda, Mu);
	fprintf('\nRouted flow #1 along path: ');
	fprintf('%g ', path);  % this statement prints all the nodes onto one line
	fprintf('\n');               % this statement starts a new line
end;

% route a second path
path = [1,9, 8, 11];
path_delay = test_path(path, 800, Lambda, Mu);

if (path_delay <= 0.05)
	[path_delay, Lambda] = route_path(path, 800, Lambda, Mu);
	fprintf('\nRouted flow #2 along path: ');
	fprintf('%g ', path);  % this statement prints all the nodes onto one line
	fprintf('\n');               % this statement starts a new line
end;


Delay  = find_network_delay(Lambda, Mu);

fprintf('Here is the Lambda matrix  (rates in 1000 pps) \n');
print_matrix ( Lambda/1000 );

fprintf('Here is the Mu matrix  (rates in 1000 pps) \n');
print_matrix ( Mu/1000 );

fprintf('Here is the Delay matrix  (in millisec) \n');
print_matrix ( Delay*1000 );
% the rest is up to you

