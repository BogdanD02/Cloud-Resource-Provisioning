from src.init import parse_config
from src.New.Core.Instance import Instance
from src.New.Solvers.MiniZinc_Solver import MiniZinc_Solver

parse_config()

inst = Instance("Models/Json/Wordpress_new.json")
inst.SetComponentInstances("Wordpress", 4)

#
# Adv: Run SURROGATE ONCE / SB.
#
#
inst.AddDataFile("Data/Json/offers_20.json")

solver = MiniZinc_Solver("chuffed", inst)
print(solver.Solve())