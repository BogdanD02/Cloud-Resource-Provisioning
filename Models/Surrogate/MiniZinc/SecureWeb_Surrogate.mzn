%
% Determines the number of Virtual Machines needed
% for the Secure Web Application.
%
% Created by David Bogdan, bogdan.david02@e-uvt.ro
%
include "Modules/Constraints.mzn";

% ----- DECISION VARIABLES -----
% 
% They denote the number of VMs used by each component
%
var 0..1024: Balancer;
var 0..1024: IDSAgent;
var 0..1024: IDSServer;
var 0..1024: Apache;
var 0..1024: Ngnix;

% ----- PROBLEM-SPECIFIC CONSTRAINTS -----

% Exactly one Balancer has to be instantiated
constraint equalBound(Balancer, 1);

% The total number of Apache and Ngnix instances has to be at least 3
constraint basicAllocation({Balancer, IDSServer, Apache, Ngnix});
constraint lowerBound(Apache + Ngnix, 3);

% Solve
solve minimize Balancer + IDSServer + Apache + Ngnix;