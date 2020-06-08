# %%
import importlib
# from multi import hybrid_multi_level
import multi as m
import pandas as pd

# %%
importlib.reload(m)
# MULTI_LEVEL
add_arg = ["-t", "4000", "-p", "100"]
fit_hist = m.hybrid_multi_level(
    "email.gml",
    levels=1,
    add_args=add_arg,
    explosion=False,
    bomb_max=False)

# %%
# trace=pd.read_csv("./trace.csv")
# print(max(fit_hist))
import matplotlib.pyplot as plt

plt.plot(fit_hist)
# %%
#   -a|--max-age int
#      Max age of the antibodies (tau)
#   -d|--duplicates int
#      Number of duplicates for each antibody
#   -e|--elitist
#      Elitist aging operator
#   -o|--optimal num
#      Optimal solution value
#   -p|--population-size int
#      Size of the population of antibodies
#   -r|--mutation-shape num
#      Value that determines the shape of the hypermutation (rho)
#   -s|--seed int
#      Seed for the random number generator
#   -t|--max-iterations int
#      Max number of iterations
