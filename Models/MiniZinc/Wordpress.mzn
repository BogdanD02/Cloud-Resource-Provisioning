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
include "Modules/Formalization2/GeneralVariables.mzn";
include "Modules/Formalization2/GeneralConstraints.mzn";


/***********************************
 ****                           ****
 ****      INPUT VARIABLES      ****
 ****                           ****
 ***********************************/
int: WPInstances = 5;

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
constraint basicAllocation(AssignmentMatrix, VM, VMOffers, NoComponents, {DNS_LoadBalancer, HTTP_LoadBalancer});
constraint capacity(AssignmentMatrix, CompREQ, VMSpecs, VMType, HardwareREQ, NoComponents, VM, VMOffers);

% Problem specific constraints
constraint exclusiveDeployment(AssignmentMatrix, VM, VMOffers, {DNS_LoadBalancer, HTTP_LoadBalancer});

constraint if(isDeployed(AssignmentMatrix, VM, VMOffers, DNS_LoadBalancer) == 1)
then 
requireProvide(AssignmentMatrix, VM, VMOffers, Wordpress, DNS_LoadBalancer, 1, 7)
else
requireProvide(AssignmentMatrix, VM, VMOffers, Wordpress, HTTP_LoadBalancer, 1, 3)
endif;

constraint requireProvide(AssignmentMatrix, VM, VMOffers, Wordpress, MySQL, 2, 3);
constraint conflict(AssignmentMatrix, VM, VMOffers, Varnish, {DNS_LoadBalancer, HTTP_LoadBalancer, MySQL});
constraint conflict(AssignmentMatrix, VM, VMOffers, DNS_LoadBalancer, {Wordpress, MySQL, Varnish});
constraint conflict(AssignmentMatrix, VM, VMOffers, HTTP_LoadBalancer, {Wordpress, MySQL, Varnish});

constraint lowerBound(AssignmentMatrix, VM, VMOffers, {Wordpress}, WPInstances);
constraint lowerBound(AssignmentMatrix, VM, VMOffers, {Varnish}, 2);
constraint lowerBound(AssignmentMatrix, VM, VMOffers, {MySQL}, 2);
constraint upperBound(AssignmentMatrix, VM, VMOffers, {DNS_LoadBalancer}, 1);


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

