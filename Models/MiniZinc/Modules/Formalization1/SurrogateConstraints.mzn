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

% Create bound constraints
predicate lowerBound(var int: compID, int: bound) = compID >= bound;
predicate lowerBound(var int: compID1, var int: compID2, int: bound) = compID1 + compID2 >= bound;
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

predicate boundedRequireProvide(var int: compID1, var int: compID2, int: NoInstID2) =
        (compID1 * NoInstID2 - compID2 > 0) /\ (compID1 * NoInstID2 - compID2 <= NoInstID2);
