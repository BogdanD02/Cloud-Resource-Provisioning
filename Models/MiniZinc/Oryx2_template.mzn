/*
 * Oryx2 model for MiniZinc
 * ---------------------------------
 *
 * @author 
 *    David Bogdan
 *    bogdan.david02@e-uvt.ro
 */

/***********************************
 ****                           ****
 ****      EXTERNAL MODULES     ****
 ****                           ****
 ***********************************/
include "Modules/GeneralVariables.mzn";
include "Modules/GeneralConstraints.mzn";


/***********************************
 ****                           ****
 ****        CONSTANTS          ****
 ****                           ****
 ***********************************/
int: Kafka = 1;
int: Zookeeper = 2;
int: HDFS_NameNode = 3;
int: HDFS_SecondaryNameNode = 4;
int: HDFS_DataNode = 5;
int: Yarn_ResourceManager = 6;
int: Yarn_HistoryService = 7;
int: Yarn_NodeManager = 8;
int: Spark_Worker = 9;
int: Spark_HistoryService = 10; 


/***********************************
 ****                           ****
 ****      MODELING PROBLEM     ****
 ****                           ****
 ***********************************/
constraint basicAllocation(AssignmentMatrix, {}, S, VM);
constraint occupancy(AssignmentMatrix, OccupancyVector, NoComponents, VM);
constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM);
constraint link(VMSpecs, VMPrice, OccupancyVector, VMType, Price, VMOffers, VM);

% Problem-specific constraints
constraint colocation(AssignmentMatrix, {HDFS_DataNode, Spark_Worker, Yarn_NodeManager}, VM);

constraint conflict(AssignmentMatrix, {Zookeeper}, VM, Kafka);
constraint conflict(AssignmentMatrix, {HDFS_SecondaryNameNode, Yarn_ResourceManager}, VM, HDFS_NameNode);
constraint conflict(AssignmentMatrix, {HDFS_SecondaryNameNode, Yarn_HistoryService}, VM, Yarn_ResourceManager);

constraint requireProvide(AssignmentMatrix, VM, Kafka, Zookeeper, 2, 1);

constraint fullDeployment(AssignmentMatrix, {}, VM, NoComponents, HDFS_DataNode);

constraint equalBound(AssignmentMatrix, VM, Yarn_HistoryService, 1);
constraint equalBound(AssignmentMatrix, VM, Spark_HistoryService, 1);


/***********************************
 ****                           ****
 ****      SOLVING PROBLEM      ****
 ****                           ****
 ***********************************/ 
solve minimize sum(k in 1..VM)(Price[k]);
