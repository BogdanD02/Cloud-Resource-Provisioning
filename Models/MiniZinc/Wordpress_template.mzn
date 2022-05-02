/*
 * Wordpress model for MiniZinc
 * ---------------------------------
 *
 * @author 
 *    David Bogdan
 *    bogdan.david02@e-uvt.ro
 *
 * This model was originally designed and implemented by Andrei Iovescu (andrei.iovescu99@e- uvt.ro). I only adapted it so it would have the same format as the other problems.
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
 ****      INPUT VARIABLES      ****
 ****                           ****
 ***********************************/
int: WPInstances;

/***********************************
 ****                           ****
 ****        CONSTANTS          ****
 ****                           ****
 ***********************************/
int: Wordpress = 1;
int: MySQL = 2;
int: DNS_LoadBalancer = 3;
int: HTTP_LoadBalancer = 4;
int: Varnish = 5;

/***********************************
 ****                           ****
 ****      MODELING PROBLEM     ****
 ****                           ****
 ***********************************/
constraint basicAllocation(AssignmentMatrix, {DNS_LoadBalancer, HTTP_LoadBalancer}, S, VM);
constraint occupancy(AssignmentMatrix, OccupancyVector, NoComponents, VM);
constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM);
constraint link(VMSpecs, VMPrice, OccupancyVector, VMType, Price, VMOffers, VM);

% Problem specific constraints
constraint exclusiveDeployment(AssignmentMatrix, VM, DNS_LoadBalancer, HTTP_LoadBalancer);

constraint if(isDeployed(AssignmentMatrix, VM, DNS_LoadBalancer) == 1)
then 
    requireProvide(AssignmentMatrix, VM, Wordpress, DNS_LoadBalancer, 1, 7)
else
    requireProvide(AssignmentMatrix, VM, Wordpress, HTTP_LoadBalancer, 1, 3)
endif;

constraint requireProvide(AssignmentMatrix, VM, Wordpress, MySQL, 2, 3);

constraint conflict(AssignmentMatrix, {DNS_LoadBalancer, HTTP_LoadBalancer, MySQL}, VM, Varnish);
constraint conflict(AssignmentMatrix, {Wordpress, MySQL, Varnish}, VM, DNS_LoadBalancer);
constraint conflict(AssignmentMatrix, {Wordpress, MySQL, Varnish}, VM, HTTP_LoadBalancer);

constraint lowerBound(AssignmentMatrix, VM, Wordpress, WPInstances);
constraint lowerBound(AssignmentMatrix, VM, Varnish, 2);
constraint lowerBound(AssignmentMatrix, VM, MySQL, 2);
constraint upperBound(AssignmentMatrix, VM, DNS_LoadBalancer, 1);


/***********************************
 ****                           ****
 ****      SOLVING PROBLEM      ****
 ****                           ****
 ***********************************/
solve minimize sum(k in 1..VM)(Price[k]);

