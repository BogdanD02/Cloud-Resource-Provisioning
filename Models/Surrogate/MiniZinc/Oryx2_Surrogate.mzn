%
% Determines the number of Virtual Machines needed
% for the Oryx2 Application.
%
% Created by David Bogdan, bogdan.david02@e-uvt.ro
%

% ----- DECISION VARIABLES -----
% 
% They denote the number of VMs used by each component
%
var 0..1024: Kafka;
var 0..1024: Zookeeper;
var 0..1024: HDFS_NameNode;
var 0..1024: HDFS_SecondaryNameNode;
var 0..1024: HDFS_DataNode;
var 0..1024: Yarn_ResourceManager;
var 0..1024: Yarn_HistoryService;
var 0..1024: Yarn_NodeManager;
var 0..1024: Spark_HistoryService;
var 0..1024: Spark_Worker;

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

% Collocation
constraint equalBound(HDFS_DataNode, Yarn_NodeManager);
constraint equalBound(HDFS_DataNode, Spark_Worker);

% Basic allocation
constraint basicAllocation({Kafka, Zookeeper, HDFS_NameNode, HDFS_SecondaryNameNode, HDFS_DataNode, Yarn_ResourceManager, Yarn_HistoryService, Yarn_NodeManager, Spark_HistoryService, Spark_Worker});

% Bounds
constraint equalBound(Yarn_HistoryService, 1);
constraint equalBound(Spark_HistoryService, 1);

% Require Provide
constraint requireProvide(Kafka, Zookeeper, 2, 1);

% Solve
solve minimize Kafka + Zookeeper + HDFS_DataNode + HDFS_NameNode + HDFS_SecondaryNameNode + Yarn_HistoryService + Yarn_NodeManager + Yarn_ResourceManager + Spark_HistoryService + Spark_Worker;
