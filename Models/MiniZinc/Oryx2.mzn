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
include "Modules/Formalization2/GeneralVariables.mzn";
include "Modules/Formalization2/GeneralConstraints.mzn";


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
constraint basicAllocation(AssignmentMatrix, VM, VMOffers, NoComponents, {});
constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM, VMOffers);

% Problem-specific constraints
constraint colocation(AssignmentMatrix, VM, VMOffers, {HDFS_DataNode, Spark_Worker, Yarn_NodeManager});

constraint conflict(AssignmentMatrix, VM, VMOffers, Kafka, {Zookeeper});
constraint conflict(AssignmentMatrix, VM, VMOffers, HDFS_NameNode, {HDFS_SecondaryNameNode, Yarn_ResourceManager});
constraint conflict(AssignmentMatrix, VM, VMOffers, Yarn_ResourceManager, {HDFS_SecondaryNameNode, Yarn_HistoryService});

constraint requireProvide(AssignmentMatrix, VM, VMOffers, Kafka, Zookeeper, 2, 1);
constraint fullDeployment(AssignmentMatrix, VM, VMOffers, NoComponents, HDFS_DataNode, {});

constraint equalBound(AssignmentMatrix, VM, VMOffers, {Yarn_HistoryService}, 1);
constraint equalBound(AssignmentMatrix, VM, VMOffers, {Spark_HistoryService}, 1);


/***********************************
 ****                           ****
 ****      SOLVING PROBLEM      ****
 ****                           ****
 ***********************************/ 
constraint linkedTypes(AssignmentMatrix, VMType, VM, VMOffers, NoComponents);
constraint linkedPrice(VMType, VMPrice, Price, VM, VMOffers);
constraint uniqueType(VMType, VM, VMOffers);
constraint uniqueAlloc(AssignmentMatrix, VM, NoComponents, VMOffers);
solve minimize sum(k in 1..VM)(Price[k]);
