# %%
import multi_level as m
from multiprocessing import Pool
import time
import importlib

importlib.reload(m)
######################
# Il nome è usato anche per prendere il .gml con lo stesso identico nome
#IMMUNO
# full_list = [["email", 1200]] * 50 + [["yeast", 2400]] * 50 + [["power", 3600]] * 50
#HYBRID
# full_list = [["email", 120]] * 50 + [["yeast", 900]] * 50 + [["power", 3600]] * 50

# CUSTOM
# full_list = [["power", 100]] * 2
# + [["yeast", None]] * 50 + [["power", None]] * 50

n_process = 2  # Numero di processi contemporanei
######################

def bench(arg):
    name = arg[0]
    max_time = arg[1]
    # MULTI_LEVEL
    res = m.hybrid_multi_level_beta(
        graph=f"./networks/{name}.gml",
        save_intermediate=False,
        verbose=False,
        seed=None,

################# MULTILEVEL RANDOM FULL EXPLOSION ##################
        # ## IMPORTANT
        # to_run="./immuno-ia", #EXEC NAME
        # ## HARD LIMITS
        # max_time=max_time,
        # ## TYPE OF MERGE
        # smart_merge=False,
        # hybrid_it="1000",
        # ## ESPLOSIONI
        # explosion=1,
        # try_close=999, #To enforce time limit
        # expl_min_ratio=1.5, # >1 = Full explosion
        # ## UTILITY
        # path=f"./BB-Immuno-RFullExplosion/{name}/{int(time.time()*1000000)}",

################# MULTILEVEL RANDOM SMART EXPLOSION ##################
        # ## IMPORTANT
        # to_run="./immuno-ia", #EXEC NAME
        # ## HARD LIMITS
        # max_time=max_time,
        # ## TYPE OF MERGE
        # smart_merge=False,
        # hybrid_it="1000",
        # ## ESPLOSIONI
        # explosion=2,
        # try_close=999, #To enforce time limit
        # expl_min_ratio=0.5,
        # ## UTILITY
        # path=f"./BB-Immuno-RSmartExplosion/{name}/{int(time.time()*1000000)}",

################# MULTILEVEL SMART MERGE ##################
        # ## IMPORTANT
        # to_run="./hybrid-ia",
        # ## HARD LIMITS
        # max_time=max_time,
        # ## TYPE OF MERGE
        # smart_merge=True,
        # merge_min_ratio= 0.5,
        # hybrid_it="ratio-10-50",
        # ## ESPLOSIONI
        # explosion=999,
        # try_close=999,
        # expl_min_ratio=0.5, 
        # ## UTILITY
        # path=f"./test/{name}/{int(time.time()*1000000)}",


    )


if __name__ == "__main__":
    with Pool(n_process) as p:
        p.map(bench, full_list)

# %%
