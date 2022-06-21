from src.init import parse_config
from src.New.Core.Instance import Instance
from src.New.Solvers.MiniZinc_Solver import MiniZinc_Solver
from src.New.Core.Model import Model

parse_config()

model = Model("Models/Json/Oryx2_new.json")

inst = Instance("Models/Json/Oryx2_new.json")

#
# Adv: Run SURROGATE ONCE / SB.
#
#
inst.AddDataFile("Data/Json/offers_20.json")

solver = MiniZinc_Solver("chuffed", inst)
print(solver.Solve())