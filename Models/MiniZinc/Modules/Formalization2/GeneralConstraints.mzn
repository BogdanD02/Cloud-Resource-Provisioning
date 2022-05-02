/*
 * Constraints for MiniZinc
 * ---------------------------------
 *
 * @b Description
 * This file is to be included in all Minizinc models.
 * It provides the definitions for the general constraints used in all models.
 *
 * @author 
 *    David Bogdan
 *    bogdan.david02@e-uvt.ro
 */
 
% Returns the number of instances of a component
function var int: instances(
       array[int, int, int] of var 0..1: AssignmentMatrix,
       int: VM,
       int: VMOffers,
       int: Component) =
  sum(k in 1..VM)(sum(j in 1..VMOffers)(AssignmentMatrix[Component,k,j]));
  
% Returns whether a component is deployed at least once
function var int: isDeployed(
       array[int, int, int] of var 0..1: AssignmentMatrix,
       int: VM,
       int: VMOffers,
       int: Component) =
  if(instances(AssignmentMatrix,VM,VMOffers,Component) >= 1) then 1 else 0 endif;
  
% Ensures each component is deployed, unless it is part of an exclusive deployment relation
predicate basicAllocation(
       array[int, int, int] of var 0..1: AssignmentMatrix,
       int: VM,
       int: VMOffers,
       int: NoComponents,
       set of int: ExclusiveDeployment) =
  forall(Component in 1..NoComponents diff ExclusiveDeployment)(instances(AssignmentMatrix, VM, VMOffers, Component) >= 1);
  
% Ensures that a VM cannot have 2 or more types
predicate uniqueType(
      array[int, int] of var 0..1: VMType,
      int: VM,
      int: VMOffers) =
  forall(k in 1..VM)(sum(j in 1..VMOffers)(VMType[k,j]) <= 1);
  
predicate uniqueAlloc(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      int: VM,
      int: NoComponents,
      int: VMOffers) =
  forall(i in 1..NoComponents, k in 1..VM)(sum(j in 1..VMOffers)(AssignmentMatrix[i,k,j]) <= 1);

% Ensures a linkage between AssignmentMatrix and VMType (Basically, if a component is assigned to a specific type, that VM MUST have that type).
predicate linkedTypes(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      array[int, int] of var 0..1: VMType,
      int: VM,
      int: VMOffers,
      int: NoComponents) =
  forall(j in 1..VMOffers)(forall(k in 1..VM)(if(sum(c in 1..NoComponents)(AssignmentMatrix[c,k,j]) > 0) then VMType[k, j] = 1 endif));
  
predicate linkedPrice(
      array[int, int] of var 0..1: VMType,
      array[int] of var int: VMPrice,
      array[int] of var int: Price,
      int: VM,
      int: VMOffers) =
  forall(k in 1..VM)(
      forall(j in 1..VMOffers)(if(VMType[k,j] == 1) then Price[k] = VMPrice[j] endif) /\ if(sum(j in 1..VMOffers)(VMType[k,j]) == 0) then Price[k] = 0 endif
  );

% Ensures hardware constraints are respected
predicate capacity(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      array[int, int] of var int: ComponentReq,
      array[int, int] of var int: VMSpecs,
      array[int, int] of var 0..1: VMType,
      int: HardwareReq,
      int: NoComponents,
      int: VM,
      int: VMOffers) =
  forall(j in 1..VMOffers)(
    forall(k in 1..VM)(
      forall(h in 1..HardwareReq)(
        sum(c in 1..NoComponents)(AssignmentMatrix[c,k,j] * ComponentReq[c,h]) <= VMSpecs[j,h] * VMType[k,j]
      )
    )
  );

% Ensures that components are deployed (collectively) [AT LEAST | EXACTLY | AT MOST] a set number of times.
predicate lowerBound(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      int: VM,
      int: VMOffers,
      set of int: Components,
      int: bound) =
  sum(c in Components)(instances(AssignmentMatrix,VM,VMOffers,c)) >= bound;
  
predicate upperBound(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      int: VM,
      int: VMOffers,
      set of int: Components,
      int: bound) =
  sum(c in Components)(instances(AssignmentMatrix,VM,VMOffers,c)) <= bound;
  
predicate equalBound(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      int: VM,
      int: VMOffers,
      set of int: Components,
      int: bound) =
  sum(c in Components)(instances(AssignmentMatrix,VM,VMOffers,c)) == bound;
  
% If a component is in conflict with several others, they cannot be deployed on the same VM
predicate conflict(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      int: VM,
      int: VMOffers,
      int: Component,
      set of int: Conflicts) =
  forall(k in 1..VM) (
    forall(j in 1..VMOffers)(
      forall(c in Conflicts)(AssignmentMatrix[Component,k,j] + AssignmentMatrix[c,k,j] <= 1)
    )
  );
  
% The components part of a colocation relation must be deployed on the same VM
predicate colocation(
      array[int, int, int] of var 0..1: AssignmentMatrix,
      int: VM,
      int: VMOffers,
      set of int: Components) =
  forall(k in 1..VM)(
    forall(j in 1..VMOffers)(
      forall(i in Components, j2 in Components)(AssignmentMatrix[i,k,j] == AssignmentMatrix[j2,k,j])
    )
  );
  
% Out of all components part of an exclusive deployment relation, only one can be deployed.
predicate exclusiveDeployment(
       array[int, int, int] of var 0..1: AssignmentMatrix,
       int: VM,
       int: VMOffers,
       set of int: Components) =
  sum(c in Components)(isDeployed(AssignmentMatrix,VM,VMOffers,c)) == 1;

% Constraint stating a component requires instances and serves instances
predicate requireProvide(
       array[int, int, int] of var 0..1: AssignmentMatrix,
       int: VM,
       int: VMOffers,
       int: Component1,
       int: Component2,
       int: requires,
       int: provides) =
  requires * sum(k in 1..VM, j in 1..VMOffers)(AssignmentMatrix[Component1,k,j]) <= provides * sum(k in 1..VM, j in 1..VMOffers)(AssignmentMatrix[Component2,k,j]);
  
predicate boundedRequireProvide(array[int, int, int] of var 0..1: AssignmentMatrix,
                                int: VM,
                                int: compID1, 
                                int: compID2, 
                                int: NoInstID2) =
   (sum(k in 1..VM, j in 1..VMOffers)(AssignmentMatrix[compID1, k, j]) * NoInstID2 - sum(k in 1..VM, j in 1..VMOffers)(AssignmentMatrix[compID2,k,j]) > 0) /\ 
   (sum(k in 1..VM, j in 1..VMOffers)(AssignmentMatrix[compID1, k, j]) * NoInstID2 - sum(k in 1..VM, j in 1..VMOffers)(AssignmentMatrix[compID2,k,j])  <= NoInstID2);
     

% Ensures a component is deployed on all VMs that don't contain conflicting components
predicate fullDeployment(
       array[int, int, int] of var 0..1: AssignmentMatrix,
       int: VM,
       int: VMOffers,
       int: NoComponents,
       int: Component,
       set of int: Conflicts) =
  forall(k in 1..VM)(
    forall(j in 1..VMOffers) (
      if(sum(c in 1..NoComponents)(AssignmentMatrix[c,k,j]) >= 1 /\ sum(c in Conflicts)(AssignmentMatrix[c,k,j]) == 0) then AssignmentMatrix[Component,k,j] = 1 endif
    )
  );
