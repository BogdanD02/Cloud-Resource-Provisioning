import docplex.mp.model as cpx
import docplex.util
from docplex.mp.conflict_refiner import ConflictRefiner, VarUbConstraintWrapper, VarLbConstraintWrapper
import time
from docplex.mp.functional import  LogicalAndExpr
from Solvers.Core.ManuverSolver import ManuverSolver
 
class CPlex_Solver_Parent(ManuverSolver):
    def _initSolver(self):

        self.orCntIndex = 0

        self.nr_vms = self.problem.nrVM
        self.nr_comps = self.problem.nrComp
        self.offers_list = self.problem.offers_list

        ### Option: default-s-b
        self.model = cpx.Model(name="Manuver Model")
        self.model.parameters.timelimit.set(2400.0)
        ### Option: reduce-set-lpmethod-default-s-b:
        # http://www-eio.upc.es/lceio/manuals/cplex-11/html/refparameterscplex/refparameterscplex103.html#271905
        #self.model.parameters.preprocessing.reduce.set(1)
        # print(self.model.parameters.lpmethod)
        # self.model.parameters.lpmethod =3
        # print(self.model.parameters.lpmethod)
        ### sym breaking options
        ### Option: 0 no-s-b
        #self.model.parameters.preprocessing.symmetry = 0
        ### Option: 1 Exert a moderate level of symmetry breaking
        self.model.parameters.preprocessing.symmetry = 1
        # ### Option: 2 Exert an aggressive level of symmetry breaking
        #self.model.parameters.preprocessing.symmetry = 2
        # ### Option: 3 Exert a very aggressive level of symmetry breaking
        #self.model.parameters.preprocessing.symmetry = 1
        # ### Option: 4 Exert a highly aggressive level of symmetry breaking
        #self.model.parameters.preprocessing.symmetry = 4
        # ### Option: 5 Exert an extremely aggressive level of symmetry breaking
        #self.model.parameters.preprocessing.symmetry = 5

        #0-default CPX_ALG_AUTOMATIC
        #2-CPX_ALG_DUAL
        #3-CPX_ALG_NET

        # CPXPARAM_Preprocessing_Reduce
        # 1
        # CPXPARAM_MIP_Tolerances_AbsMIPGap
        # 0
        # CPXPARAM_MIP_Tolerances_MIPGap
        # 0

        self._define_variables()

    def _define_variables(self):
        """
        Creates the variables used in the solver and the constraints on them as well as others (offers encoding,
        usage vector, etc.)
        :return: None
        """

        # Assignment matrix a_{alpha,k}: 1 if component alpha is on machine k, 0 otherwise
        self.a = {}

        # VAriables related to offers
        self.vmType = {}
        self.PriceProv = {}

    def run(self):
        objective = self.model.sum(self.PriceProv[j] for j in range(self.nr_vms))
        self.model.minimize(objective)
        #       self.model.prettyprint("out")
        self.model.export_as_lp(self.cplexLPPath)
        #       self.model.export_as_mps("nou")

        vmPrice = []
        vmType = []
        a_mat = []

        self.get_current_time()

        starttime = time.time()
        xx = self.model.solve()
        stoptime = time.time()

        if docplex.util.status.JobSolveStatus.OPTIMAL_SOLUTION == self.model.get_solve_status():
            # Variables for offers description
            vmType = self._get_solution_vm_type()

            for var in self.PriceProv:
                vmPrice.append(int(self.model.solution.get_value(f"PriceProv{var+1}")))
            #print(vmPrice)

            l = []
            col = 0
            for index, var in self.a.items():
                if col == self.problem.nrVM:
                    a_mat.append(l)
                    l = []
                    col = 0
                col += 1
                l.append(int(var.solution_value))
            a_mat.append(l)

        else:
            cr = ConflictRefiner()
            conflicts = cr.refine_conflict(self.model)
            for conflict in conflicts:
                st = conflict.status
                ct = conflict.element
                label = conflict.name
                label_type = type(conflict.element)
                if isinstance(conflict.element, VarLbConstraintWrapper)\
                        or isinstance(conflict.element, VarUbConstraintWrapper):
                    ct = conflict.element.get_constraint()
                # Print conflict information in console

        return xx.get_objective_value(), vmPrice, stoptime - starttime, a_mat, vmType
        # return None, None, stoptime - starttime, None, None




    def RestrictionLex(self, vm_id, additional_constraints=[]):
        """
        Lexicografic order between two consecutive columns
        :param vm_id: the vm id
        :param additonal_constraints: other constraints
        :return:
        """
        l = additional_constraints.copy()
        previousVar = None

        # print("self.nrComp ", self.nrComp)
        for i in range(0, self.nrComp):
            if i > 0:
                u = i - 1
                if previousVar is None:
                    l = []
                else:
                    l = [previousVar]
                l.append(self.a[u, vm_id] == self.a[u, vm_id + 1])
            var = self.model.binary_var(name="lex_VM{0}_comp{1}".format(vm_id, i))
            element = [self.a[i, vm_id] >= self.a[i, vm_id + 1]]
            if len(l) >= 1:
                if len(l) == 1:
                    self.model.add_equivalence(var, l[0])
                else:
                    self.model.add_equivalence(var, LogicalAndExpr(self.model, l) == 1)
                self.model.add_indicator(var, self.a[i, vm_id] >= self.a[i, vm_id + 1])
                previousVar = var
            else:
                self.model.add_constraint(ct=self.a[i, vm_id] >= self.a[i, vm_id + 1])



    def RestrictionPrice(self, vm_id, additional_constraints=[]):
        """
        Lexicografic order between two consecutive columns
        :param vm_id: the vm id
        :param additonal_constraints: other constraints
        :return:
        """
        if len(additional_constraints) == 0:
            self.model.add_constraint(ct=self.PriceProv[vm_id] >= self.PriceProv[vm_id + 1], ctname="price_order")
        else:
            var = self.model.binary_var(name="order_VM{0}_combined".format(vm_id))
            if len(additional_constraints) == 1:
                self.model.add_equivalence(var, additional_constraints[0])
            else:
                self.model.add_equivalence(var, LogicalAndExpr(additional_constraints))
            self.model.add_indicator(var, self.PriceProv[vm_id] >= self.PriceProv[vm_id + 1])

        return self.PriceProv[vm_id] == self.PriceProv[vm_id + 1]


    def RestrictionFixComponentOnVM(self, comp_id, vm_id, value=1):
        """
        Force placing component on a specific VM
        :param comp_id: the ID of the component
        :param vm_id: the ID of the VM
        :param value: 1 assigned; 0 unassigned
        :return: None
        """
        self.model.add_constraint(ct=self.a[comp_id, vm_id] == value, ctname="a_c_fix_component")

    def RestrictionLoad(self, vm_id, additional_constraints=[]):
        """
        Lexicografic order between two consecutive columns
        :param vm_id: the vm id
        :param additonal_constraints: other constraints
        :return:
        """

        if len(additional_constraints) == 0:
            self.model.add_constraint(ct=sum([self.a[i, vm_id] for i in range(0, self.nr_comps)]) >= sum(
                [self.a[i, vm_id + 1] for i in range(0, self.nr_comps)]), ctname="c_vm_load_lex_order")
        else:
            var = self.model.binary_var(name="vmload_VM{0}_combined".format(vm_id))
            if len(additional_constraints) == 1:
                self.model.add_equivalence(var, additional_constraints[0])
            else:
                self.model.add_equivalence(var, LogicalAndExpr(additional_constraints))
            self.model.add_indicator(var, sum([self.a[i, vm_id] for i in range(0, self.nr_comps)]) >= sum(
                [self.a[i, vm_id + 1] for i in range(0, self.nr_comps)]))

        return sum([self.a[i, vm_id] for i in range(self.nr_comps)]) == \
               sum([self.a[i, vm_id + 1] for i in range(self.nr_comps)])


    def RestrictionConflict(self, alphaCompId, conflictCompsIdList):
        """
        Constraint describing the conflict between components. The 2 params. should not be placed on the same VM
        :param alphaCompId: id of the first conflict component
        :param conflictCompsIdList: id of the second conflict component
        :return: None
        """
        for compId in conflictCompsIdList:
            compId += 1

        self.problem.logger.debug(
            "RestrictionConflict: alphaCompId = {} conflictComponentsList = {}".format(alphaCompId,
                                                                                       conflictCompsIdList))
        for j in range(self.nr_vms):
            for k in range(self.nrOffers):
                for conflictCompId in conflictCompsIdList:
                    self.model.add_constraint(ct=self.a[alphaCompId, j, k] + self.a[conflictCompId, j, k] <= 1,
                                            ctname="c_comp_conflict")

    def RestrictionOneToOneDependency(self, alphaCompId, betaCompId):
        """
        Contraint describing that alphaCompId and betaCompId should be deployed on the same VM
        :param alphaCompId: id of the first component
        :param betaCompId: id of the second component
        :return: None
        """
        for j in range(self.nr_vms):
            self.model.add_constraint(ct=sum(self.a[alphaCompId, j, k] for k in range(self.nrOffers)) == sum(self.a[betaCompId, j, k] for k in range(self.nrOffers)),
                                      ctname="c_one_2_one_dependency")

    def RestrictionManyToManyDependency(self, alphaCompId, betaCompId, relation):
        """
        The number of instances of component alphaCompId depends on the number of instances of component betaCompId
        :param alphaCompId: id of the first component
        :param betaCompId: id of the second component
        :param relation: one of the strings in the set {"=", "<=", ">="}
            "=": sum(instances of alpha component) == sum(instances of beta component)
            "<=": sum(instances of alpha component) <= sum(instances of beta component)
            ">=": sum(instances of alpha component) >= sum(instances of beta component)
        :return: None
        """
        if relation == "<=":
            self.model.add_constraint(ct=self.model.sum(self.a[alphaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) <=
                                      self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)),
                                      ctname="c_many_2_many_dependency_le")

        elif relation == ">=":
            self.model.add_constraint(ct=self.model.sum(self.a[alphaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) >=
                                      self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)),
                                      ctname="c_many_2_many_dependency_ge")

        elif relation == "=":
            self.model.add_constraint(ct=self.model.sum(self.a[alphaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) ==
                                      self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)),
                                      ctname="c_many_2_many_dependency_eq")

    def RestrictionOneToManyDependency(self, alphaCompId, betaCompId, noInstances):
        """
        At each alphaCompId component should be deployed noInstances betaCompId components
        :param alphaCompId: id of the first component
        :param betaCompId: id of the second component
        :param noInstances: depending instances number
        :return: None
        """

        self.model.add_constraint(ct=
                                  noInstances * self.model.sum(self.a[alphaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) -
                                  self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) >= 1,
                                  ctname="c_one_2_many_dependency_p1")

        self.model.add_constraint(ct=noInstances * self.model.sum(self.a[alphaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) -
                                     self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) <= noInstances,
                                  ctname="c_one_2_many_dependency_p1")

    def RestrictionUpperLowerEqualBound(self, compsIdList, bound, operator):
        """
        Defines an upper/lower/equal bound on the number of instances that a component must have
        :param compsIdList: list of components
        :param bound: a positive number
        :param operator: <=, >=, =
            "<=": sum(compsIdList) <= bound
            ">=": sum(compsIdList) >= bound
            "==":  sum(compsIdList) == bound
        :return: None
        """

        self.problem.logger.debug("RestrictionUpperLowerEqualBound: {} {} {} ".format(compsIdList, operator, bound))

        if operator == "<=":
            self.model.add_constraint(
                ct=self.model.sum(self.a[compId, j, k] for compId in compsIdList for j in range(self.nr_vms) for k in range(self.nrOffers)) <= bound,
                ctname="c_upper_lower_bound")

        elif operator == ">=":
            self.model.add_constraint(
                ct=self.model.sum(self.a[compId, j, k] for compId in compsIdList for j in range(self.nr_vms) for k in range(self.nrOffers)) >= bound,
                ctname="c_upper_lower_bound")

        elif operator == "=":
            self.model.add_constraint(
                ct=self.model.sum(self.a[compId, j, k] for compId in compsIdList for j in range(self.nr_vms) for k in range(self.nrOffers)) == bound,
                ctname="c_upper_lower_bound")
        else:
            self.problem.logger.info("Unknown operator")

    def RestrictionRangeBound(self, compsIdList, lowerBound, upperBound):
        """
        Defines a lower and upper bound of instances that a component must have
        :param compsIdList: list of components
        :param lowerBound: a positive number
        :param upperBound: a positive number
        :return:
        """
        for i in range(len(compsIdList)): 
            compsIdList[i] -= 1
            self.model.add_constraint(
                ct=self.model.sum(self.a[compId, j, k] for compId in compsIdList for j in range(self.nr_vms) for k in range(self.nrOffers)) >= lowerBound,
                ctname="c_range_bound")
            self.model.add_constraint(
                ct=self.model.sum(self.a[compId, j, k] for compId in compsIdList for j in range(self.nr_vms) for k in range(self.nrOffers)) <= upperBound,
                ctname="c_range_bound")

    def RestrictionFullDeployment(self, alphaCompId, inConflictCompsIdList):
        """
        Adds the fact that the component alphaCompId must be deployed on all machines except the ones that contain
         components that alphaCompId alpha is in conflict with
        :param alphaCompId: the component which must be fully deployed
        :param inConflictCompsIdList: the list of components that alphaCompId is in conflict in
        :return: None
        """
        for j in range(self.nr_vms):
            for k in range(self.nrOffers):
                self.model.logical_and(
                    self.model.logical_and(self.model.sum(self.a[i, j, k] for i in range(self.nr_comps)) >= 1, self.model.sum(self.a[i,j,k] for i in inConflictCompsIdList) == 0),
                    self.a[alphaCompId,j,k] == 1
                )

                self.model.logical_and(
                    self.model.logical_or(self.model.sum(self.a[i, j, k] for i in range(self.nr_comps)) == 0, self.model.sum(self.a[i,j,k] for i in inConflictCompsIdList) >= 1),
                    self.a[alphaCompId,j,k] == 0,
                )

    def RestrictionRequireProvideDependency(self, alphaCompId, betaCompId, alphaCompIdInstances, betaCompIdInstances):
        """
        The number of instances of component alpha depends on the number of instances of component beta
        :param alphaCompId: id of the first component
        :param betaCompId: id of the second component
        :param alphaCompIdInstances: number of instances of component alphaCompId
        :param betaCompIdInstances: number of instances of component betaCompId
        :return: None
        """
        self.model.add_constraint(
            ct=self.model.logical_or(alphaCompIdInstances * self.model.sum(self.a[alphaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) <=
               betaCompIdInstances * self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)), self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) == 0),
            ctname="c_provide_require")

    def RestrictionAlphaOrBeta(self, alphaCompId, betaCompId):
        """
        Describes the fact that alphaCompId or betaCompId not both
        :param alphaCompId: id of the first component
        :param betaCompId: id of the second component
        :return:
        """
        self.problem.logger.debug(
            "RestrictionAlphaOrBeta: alphaCompId={}, betaCompId={}".format(alphaCompId, betaCompId))

        alphaSum = self.model.binary_var(name="alphaSum{0}".format(self.orCntIndex))
        betaSum = self.model.binary_var(name="betaSum{0}".format(self.orCntIndex))

        self.orCntIndex += 1

        self.model.add_equivalence(alphaSum, self.model.sum(self.a[alphaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) >= 1,
                                   name="c_or_alpha")
        self.model.add_equivalence(betaSum, self.model.sum(self.a[betaCompId, j, k] for j in range(self.nr_vms) for k in range(self.nrOffers)) >= 1,
                                   name="c_or_beta")

        self.model.add_constraint(ct=self.model.sum([alphaSum, betaSum]) == 1, ctname="c_or")


    def RestrictionLexBinaryNumber(self):
        """
        Transform column into a binary number - not tested preprocessing reorder components by number
        :return:
        """
        list_comps = []
        for comp_id in range(self.nrComp):
            if not self.problem.componentsList[comp_id].fullDeployedComponent:
                list_comps.append(comp_id)
        n = len(list_comps)
        n = n - 1
        for vm_id in range(self.nrVM - 1):
            self.model.add_constraint(
                self.model.sum([self.a[list_comps[i], vm_id] * (2 ** (i)) for i in range(len(list_comps))]) <=
                self.model.sum([self.a[list_comps[i], vm_id + 1] * (2 ** (i)) for i in range(len(list_comps))]),
                ctname="binayr_flav")

    def _get_solution_vm_type(self):
        print("Get from subclass")