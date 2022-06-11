%
% Determines the number of Virtual Machines needed
% for the Secure Billing Mail Service.
%
% Created by David Bogdan, bogdan.david02@e-uvt.ro
%
include "Modules/Constraints.mzn";

% ----- DECISION VARIABLES -----
% 
% They denote the number of VMs used by each component
%
var 0..1024: SecurityManager;
var 0..1024: Gateway;
var 0..1024: CodingService;
var 0..1024: SQLServer;
var 0..1024: LoadBalancer;

% ----- PROBLEM-SPECIFIC CONSTRAINTS -----
constraint basicAllocation({SecurityManager, Gateway, CodingService, SQLServer, LoadBalancer});

constraint equalBound(CodingService, 1);
constraint equalBound(LoadBalancer, 1);

solve minimize SecurityManager + Gateway + CodingService + SQLServer + LoadBalancer;