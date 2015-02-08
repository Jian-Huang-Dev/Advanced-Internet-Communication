%------------------------------------------------------------
% put the next code into a function file called ?Script_SPRINT_TOPOLOGY?
% The matlab file called ?Script_SPRINT_TOPOLOGY? will define the network.
% Here is the SPRINT Topology matrix
% TOP(i,j) == 1 means the edge (i,j) exists
%------------------------------------------------------------

N = 15 
 
TOP = zeros(N,N);
TOP(1,[2,4,9,13]) = ones(1,4);
TOP(2,[1,3,6]) = [1,1,1,];
TOP(3,[2,4,5,14])    = ones(1,4);
TOP(4,[1,3,5,6,7])    = ones(1,5);
TOP(5,[3,4,8]) = [1,1,1];
TOP(6,[2,4,7,9])   = ones(1,4);
TOP(7,[4,6,8,9])   = ones(1,4);
TOP(8,[5,7,9,11,13,15])      = ones(1,6);
TOP(9,[1,6,7,8,10,12,11])   = ones(1,7);
TOP(10,[9,13])   =  ones(1,2);
TOP(11,[8,9,12,14,15])   = ones(1,5);
TOP(12,[9,11,13,14])   = ones(1,4);
TOP(13,[1,10,8,12,14])   = ones(1,5);
TOP(14,[3,11,12,13,15])   = ones(1,5);
TOP(15,[8,11,14])   = ones(1,3);

%---------------------------------------------
% Here is the SPRINT location matrix
% LOC(i, 1:2)  equals the (x,y) locations of node i
% this is useful if you want to draw the graph in matlab
%----------------------------------------------
global LOC;
LOC = zeros(N, 2);

LOC(1,1:2) = [2,16];
LOC(2,1:2) = [1.8,14];
LOC(3,1:2) = [1.6,10.5];
LOC(4,1:2) = [2.8, 11.6];
LOC(5,1:2) = [3.2, 9.5];
LOC(6,1:2) = [4,14];
LOC(7,1:2) = [5.8, 13];
LOC(8,1:2) = [7.3, 8.8];
LOC(9,1:2) = [8.5, 14.5];
LOC(10,1:2) = [10.2, 13.2];
LOC(11,1:2) = [10.6, 10.5];
LOC(12,1:2) = [12.5, 17.4];
LOC(13,1:2) = [13.2, 15.5];
LOC(14,1:2) = [12.3, 12.8];
LOC(15,1:2) = [12.5, 9.1];
 

