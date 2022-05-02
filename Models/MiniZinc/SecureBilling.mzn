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
include "Modules/Formalization2/GeneralConstraints.mzn";
include "Modules/Formalization2/GeneralVariables.mzn";


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
constraint basicAllocation(AssignmentMatrix, VM, VMOffers, NoComponents, {});
constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM, VMOffers);

% Problem-specific constraints
constraint equalBound(AssignmentMatrix, VM, VMOffers, {CodingService}, 1);
constraint equalBound(AssignmentMatrix, VM, VMOffers, {LoadBalancer}, 1);

constraint conflict(AssignmentMatrix, VM, VMOffers, CodingService, {SecurityManager, SQLServer, LoadBalancer, Gateway});
constraint conflict(AssignmentMatrix, VM, VMOffers, LoadBalancer, {Gateway, SQLServer});


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
