/*
 * Secure Billing Mail model for MiniZinc
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
include "Modules/Formalization1/SymmetryBreaking.mzn";
include "Modules/Formalization1/GeneralConstraints.mzn";
include "Modules/Formalization1/GeneralVariables.mzn";


/***********************************
 ****                           ****
 ****        CONSTANTS          ****
 ****                           ****
 ***********************************/
int: CodingService = 1;
int: SecurityManager = 2;
int: Gateway = 3;
int: SQLServer = 4;
int: LoadBalancer = 5;

              
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
constraint equalBound(AssignmentMatrix, VM, CodingService, 1);
constraint equalBound(AssignmentMatrix, VM, LoadBalancer, 1);

constraint conflict(AssignmentMatrix, {SecurityManager, SQLServer, LoadBalancer, Gateway}, VM, CodingService);
constraint conflict(AssignmentMatrix, {Gateway, SQLServer}, VM, LoadBalancer);


/***********************************
 ****                           ****
 ****      SOLVING PROBLEM      ****
 ****                           ****
 ***********************************/
constraint AssignmentMatrix[CodingService,1] = 1;
constraint AssignmentMatrix[LoadBalancer, 1] = 0;
constraint AssignmentMatrix[SQLServer, 1] = 0;
constraint AssignmentMatrix[LoadBalancer,2] = 1;
constraint AssignmentMatrix[CodingService, 2] = 0;
constraint AssignmentMatrix[SQLServer, 2] = 0;
constraint AssignmentMatrix[SQLServer,3] = 1;
constraint AssignmentMatrix[CodingService, 3] = 0;
constraint AssignmentMatrix[LoadBalancer, 3] = 0;
constraint LX(AssignmentMatrix, NoComponents, VM, 4);
solve minimize sum(k in 1..VM)(Price[k]);
