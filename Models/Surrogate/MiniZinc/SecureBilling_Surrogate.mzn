%
% Determines the number of Virtual Machines needed
% for the Secure Billing Mail Service.
%
% Created by David Bogdan, bogdan.david02@e-uvt.ro
%


% ----- DECISION VARIABLES -----
% 
% They denote the number of VMs used by each component
%
var 0..1024: SecurityManager;
var 0..1024: Gateway;
var 0..1024: CodingService;
var 0..1024: SQLServer;
var 0..1024: LoadBalancer;

% Create bound constraints
predicate lowerBound(var int: compID, int: bound) = compID >= bound;
predicate upperBound(var int: compID, int: bound) = compID <= bound;
predicate equalBound(var int: compID, int: bound) = compID == bound;
predicate equalBound(var int: compID1, var int: compID2) = compID1 == compID2;
    
% Create the basic allocation
predicate basicAllocation(var set of int: components) =
    forall(i in components)(i >= 1);
    
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
constraint basicAllocation({SecurityManager, Gateway, CodingService, SQLServer, LoadBalancer});

constraint equalBound(CodingService, 1);
constraint equalBound(LoadBalancer, 1);

solve minimize SecurityManager + Gateway + CodingService + SQLServer + LoadBalancer;