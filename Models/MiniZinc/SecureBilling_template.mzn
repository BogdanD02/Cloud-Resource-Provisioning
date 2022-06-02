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
include "Modules/GeneralConstraints.mzn";
include "Modules/GeneralVariables.mzn";


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
solve minimize sum(k in 1..VM)(Price[k]);
