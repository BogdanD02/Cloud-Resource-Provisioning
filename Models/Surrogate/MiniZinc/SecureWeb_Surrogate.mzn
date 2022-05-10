%
% Determines the number of Virtual Machines needed
% for the Secure Web Application.
%
% Created by David Bogdan, bogdan.david02@e-uvt.ro
%

% ----- DECISION VARIABLES -----
% 
% They denote the number of VMs used by each component
%
var 0..1024: Balancer;
var 0..1024: IDSAgent;
var 0..1024: IDSServer;
var 0..1024: Apache;
var 0..1024: Ngnix;

% Create bound constraints
predicate lowerBound(var int: compID, int: bound) = compID >= bound;
predicate upperBound(var int: compID, int: bound) = compID <= bound;
predicate equalBound(var int: compID, int: bound) = compID == bound;
    
% Create the Require-Provide constraint
predicate requireProvide(var int: compID1, var int: compID2, int: InstancesID1, int: InstancesID2) =
    compID1 * InstancesID1 <= compID2 * InstancesID2;
    
% Create Provide constraint
predicate provide(var int: compID1, var int: compID2, int: InstancesID1) =
    compID1 <= compID2 * InstancesID1;

predicate exclusiveDeployment( var int: alphaCompId, var int: betaCompId)
          = (alphaCompId > 0 /\ betaCompId = 0) \/ (alphaCompId = 0 /\ betaCompId > 0);

predicate boundedRequireProvide(var int: compID1, var int: compID2, int: NoInstID2) =
        (compID1 * NoInstID2 - compID2 > 0) /\ (compID1 * NoInstID2 - compID2 <= NoInstID2);

% ----- PROBLEM-SPECIFIC CONSTRAINTS -----

% Exactly one Balancer has to be instantiated
constraint equalBound(Balancer, 1);

% The total number of Apache and Ngnix instances has to be at least 3
constraint lowerBound(Apache + Ngnix, 3);
constraint lowerBound(Ngnix, 1);
constraint lowerBound(IDSServer, 1);
constraint lowerBound(IDSAgent, 1);

% There must be an IDSServer aditional component every 10 IDSAgents ( Pentru fiecare (10) Agenti adaugati, trebuie sa am un server nou )
constraint boundedRequireProvide(IDSServer, IDSAgent, 10);

% Solve
solve minimize Balancer + IDSServer + Apache + Ngnix + IDSAgent;