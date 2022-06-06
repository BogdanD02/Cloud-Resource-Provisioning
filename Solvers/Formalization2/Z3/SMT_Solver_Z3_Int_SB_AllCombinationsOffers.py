from z3 import *
from Solvers.Formalization2.Z3.SMT_Solver_Z3_Parent import Z3_Solver_Int_Parent_Form2
from Solvers.Core.ManuverSolver_SB import ManuverSolver_SB

class Z3_SolverInt_SB_Enc_AllCombinationsOffers(Z3_Solver_Int_Parent_Form2, ManuverSolver_SB):

    def _defineVariablesAndConstraints(self):
        """
        Creates the variables used in the solver and the constraints on them as well as others (offers encoding, usage vector, etc.)
        :return: None
        """
        super()._defineVariablesAndConstraints()

        # values from availableConfigurations
        if self.default_offers_encoding:
            self.ProcProv = [Int('ProcProv%i' % j) for j in range(1, self.nrVM + 1)]
            self.MemProv = [Int('MemProv%i' % j) for j in range(1, self.nrVM + 1)]
            self.StorageProv = [Int('StorageProv%i' % j) for j in range(1, self.nrVM + 1)]
        self.PriceProv = [Int('PriceProv%i' % j) for j in range(1, self.nrVM + 1)]

        self.a = [Int('C%i_VM%i_Of%i' % (i + 1, j + 1, k + 1)) for i in range(self.nrComp) for j in range(self.nrVM) for k in range(self.nrOffers)]

        # elements of the association matrix should be just 0 or 1
        for i in range(len(self.a)):
            self.solver.add(Or([self.a[i] == 0, self.a[i] == 1]))

        self.vmType = [Int('VM%i_Of%iType' % (j, k)) for j in range(1, self.nrVM + 1) for k in range(1, self.nrOffers + 1)]

        for i in range(len(self.vmType)):
            self.solver.add(Or([self.vmType[i] == 0, self.vmType[i] == 1]))

        # A component can only have one type
        for j in range(self.nrVM):
            for i in range(self.nrComp):
                self.solver.add(sum([self.a[i * self.nrVM * self.nrOffers + j * self.nrOffers + k] for k in range(self.nrOffers)]) <= 1)
        
        # A VM can only have one type
        for j in range(self.nrVM):
            self.solver.add(sum([self.vmType[j * self.nrOffers + k] for k in range(self.nrOffers)]) <= 1)
        
    def convert_price(self, price):
        return price.as_long() / 1000.

    def _hardware_and_offers_restrictionns(self, scale_factor):
        # #price restrictions
        # for j in range(self.nrVM):
        #     self.solver.add(self.PriceProv[j] >= 0)
            #self.solver.add(
            #    Implies(sum([self.a[i * self.nrVM * self.nrOffers + j * self.nrOffers + k] for i in range(self.nrComp) for k in range(self.nrOffers)]) == 0, self.PriceProv[j] == 0))

        for j in range(self.nrVM):
            for o in range(self.nrOffers):
                self.solver.add(
                    sum(self.a[i * self.nrOffers * self.nrVM + j * self.nrOffers + o] * self.problem.componentsList[i].HM for i in range(self.nrComp))
                    <= self.offers_list[o][2] * self.vmType[j * self.nrOffers + o]
                )

                self.solver.add(
                    sum(self.a[i * self.nrOffers * self.nrVM + j * self.nrOffers + o] * self.problem.componentsList[i].HS for i in range(self.nrComp))
                    <= self.offers_list[o][3] * self.vmType[j * self.nrOffers + o]
                )

                self.solver.add(
                    sum(self.a[i * self.nrOffers * self.nrVM + j * self.nrOffers + o] * self.problem.componentsList[i].HC for i in range(self.nrComp))
                    <= self.offers_list[o][1] * self.vmType[j * self.nrOffers + o]
                )

        for j in range(self.nrVM):
            for o in range(self.nrOffers):
                self.solver.add(
                    If(self.vmType[j * self.nrOffers + o] == 1, self.PriceProv[j] == self.offers_list[o][-1], self.PriceProv[j] >= 0)
                )

        #map vm to type
        # priceIndex = len(self.offers_list[0]) - 1
        # for vm_id in range(self.nrVM):
        #     index = 0
        #     for offer in self.offers_list:
        #         index += 1
        #         self.solver.add(
        #             Implies(And(sum([self.a[i * self.nrVM * self.nrOffers + vm_id * self.nrOffers + index - 1] for i in range(self.nrComp)]) >= 1,
        #                         self.vmType[vm_id * self.nrOffers + index - 1] == 1),
        #                     And(self.PriceProv[vm_id] == price,
        #                         self.ProcProv[vm_id] == offer[1],
        #                         self.MemProv[vm_id] == (
        #                         offer[2] if int(scale_factor) == 1 else offer[2] / scale_factor),
        #                         self.StorageProv[vm_id] == (
        #                         offer[3] if int(scale_factor) == 1 else offer[3] / scale_factor)
        #                         )
        #                     ))
        # #map hardware
        # tmp = []
        # for k in range(self.nrVM):
        #     tmp.append(
        #         sum([self.a[i * self.nrVM * self.nrOffers + k * self.nrOffers + o] * (self.problem.componentsList[i].HC) for i in range(self.nrComp) for o in range(self.nrOffers)]) <=
        #         self.ProcProv[k])
        #     tmp.append(sum([self.a[i * self.nrVM * self.nrOffers + k * self.nrOffers + o] * ((
        #         self.problem.componentsList[i].HM if int(scale_factor) == 1 else
        #         self.problem.componentsList[i].HM / scale_factor)) for i in range(self.nrComp) for o in range(self.nrOffers)]) <=
        #                self.MemProv[k])
        #     tmp.append(sum([self.a[i * self.nrVM * self.nrOffers + k * self.nrOffers + o] * ((
        #         self.problem.componentsList[i].HS if int(scale_factor) == 1 else
        #         self.problem.componentsList[i].HS / scale_factor)) for i in range(self.nrComp) for o in range(self.nrOffers)]) <=
        #                self.StorageProv[k])
        # self.solver.add(tmp)