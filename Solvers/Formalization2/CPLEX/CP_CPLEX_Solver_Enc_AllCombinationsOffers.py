from Solvers.Formalization2.CPLEX.CP_CPLEX_Solver import CPlex_Solver_Parent
from Solvers.Core.ManuverSolver_SB import ManuverSolver_SB

class CPlex_Solver_SB_Enc_AllCombinationsOffers(CPlex_Solver_Parent, ManuverSolver_SB):

    def _define_variables(self):
        """
        Creates the variables used in the solver and the constraints on them as well as others (offers encoding,
        usage vector, etc.)
        :return: None
        """

        # Assignment matrix a_{alpha,k}: 1 if component alpha is on machine k, 0 otherwise

        self.a = {(i, j, k): self.model.binary_var(name="C{0}_VM{1}_OF{2}".format(i+1, j+1, k+1))
                  for i in range(self.nr_comps) for j in range(self.nr_vms) for k in range(self.nrOffers)}

        #Variables for offers description
        self.vmType = {(j, k): self.model.binary_var(name="vmType{0}_of{1}".format(j + 1, k + 1))
                       for j in range(self.nr_vms) for k in range(self.nrOffers)}

        maxPrice = max(self.offers_list[t][len(self.offers_list[0]) - 1] for t in range(len(self.offers_list)))
        self.PriceProv = {(j): self.model.integer_var(lb=0, ub=maxPrice, name="PriceProv{0}".format(j + 1)) for j in range(self.nr_vms)}

        # A machine can only have one type
        for j in range(self.nr_vms):
            self.model.add_constraint(ct=self.model.sum(self.vmType[j, k] for k in range(self.nrOffers)) <= 1)

        # A component can only have one type
        for i in range(self.nr_comps):
            for j in range(self.nr_vms):
                self.model.add_constraint(ct=self.model.sum(self.a[i,j,k] for k in range(self.nrOffers)) <= 1)

    def _hardware_and_offers_restrictionns(self, scaleFactor):
        """
        Describes the hardware requirements for each component
        :param componentsRequirements: list of components requirements as given by the user
        :return: None
        """
        for j in range(self.nr_vms):
            for k in range(self.nrOffers):
                self.model.add_constraint(ct=self.model.sum(self.a[i, j, k] * (self.problem.componentsList[i].HC)
                                        for i in range(self.nr_comps)) <= self.offers_list[k][1] * self.vmType[j,k], ctname="c_hard_cpu")
                self.model.add_constraint(ct=self.model.sum(self.a[i, j, k] * (self.problem.componentsList[i].HM)
                                        for i in range(self.nr_comps)) <= self.offers_list[k][2] * self.vmType[j,k], ctname="c_hard_mem")
                self.model.add_constraint(ct=self.model.sum(self.a[i, j, k] * (self.problem.componentsList[i].HS)
                                            for i in range(self.nr_comps)) <= self.offers_list[k][3] * self.vmType[j,k], ctname="c_hard_storage")
                self.model.add_if_then(
                    self.vmType[j,k] == 1,
                    self.PriceProv[j] == self.offers_list[k][-1]
                )

    def _same_type(self, var, vm_id):
        self.model.add_equivalence(var, self.vmType[vm_id] == self.vmType[vm_id + 1])

    def _get_solution_vm_type(self):
        vm_types = []
        for index, var in self.vmType.items():
            vm_types.append(var.solution_value)
        return vm_types