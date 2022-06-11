%
% Determines the number of Virtual Machines needed
% for the Oryx2 Application.
%
% Created by David Bogdan, bogdan.david02@e-uvt.ro
%
include "Modules/Constraints.mzn";

% ----- DECISION VARIABLES -----
% 
% They denote the number of VMs used by each component
%
var 0..1024: Kafka;
var 0..1024: Zookeeper;
var 0..1024: HDFS_NameNode;
var 0..1024: HDFS_SecondaryNameNode;
var 0..1024: Yarn_ResourceManager;
var 0..1024: Yarn_HistoryService;
var 0..1024: Spark_HistoryService;

% ----- PROBLEM-SPECIFIC CONSTRAINTS -----

% Basic allocation
constraint basicAllocation({Kafka, Zookeeper, HDFS_NameNode, HDFS_SecondaryNameNode, Yarn_ResourceManager, Yarn_HistoryService, Spark_HistoryService});

% Bounds
constraint equalBound(Yarn_HistoryService, 1);
constraint equalBound(Spark_HistoryService, 1);

% Require Provide
constraint requireProvide(Kafka, Zookeeper, 2, 1);

% Solve
solve minimize Kafka + Zookeeper + HDFS_NameNode + HDFS_SecondaryNameNode + Yarn_HistoryService + Yarn_ResourceManager + Spark_HistoryService;
