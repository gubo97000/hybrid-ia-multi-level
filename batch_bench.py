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
full_list = [["power", 3600]] * 2 
# + [["yeast", None]] * 50 + [["power", None]] * 50

n_process = 2  # Numero di processi contemporanei
######################


def bench(arg):
    name = arg[0]
    max_time = arg[1]
    # MULTI_LEVEL
    res = m.hybrid_multi_level_beta(
################# MULTILEVEL RANDOM FULL EXPLOSION ##################
        # ## IMPORTANT
        # graph=f"./networks/{name}.gml",
        # to_run="./immuno-ia", #EXEC NAME
        # ## HARD LIMITS
        # # max_levels=100,
        # # mod_goal= 0.2
        # max_time=max_time,
        # ## TYPE OF MERGE
        # smart_merge=False,
        # hybrid_it="1000",
        # ## ESPLOSIONI
        # explosion=1,
        # try_close=999, #To enforce time limit
        # last_try=False,
        # expl_min_ratio=1.5, #Full explosion
        # ## UTILITY
        # # add_args=add_arg,
        # seed=None,
        # save_intermediate=False,
        # verbose=False,
        # path=f"./BB-Immuno-RFullExplosion/{name}/{int(time.time()*1000000)}",

################# MULTILEVEL RANDOM SMART EXPLOSION ##################
        # ## IMPORTANT
        # graph=f"./networks/{name}.gml",
        # to_run="./immuno-ia", #EXEC NAME
        # ## HARD LIMITS
        # # max_levels=100,
        # # mod_goal= 0.2
        # max_time=max_time,
        # ## TYPE OF MERGE
        # smart_merge=False,
        # hybrid_it="1000",
        # ## ESPLOSIONI
        # explosion=2,
        # try_close=999, #To enforce time limit
        # last_try=False, 
        # expl_min_ratio=0.5,
        # ## UTILITY
        # # add_args=add_arg,
        # seed=None,
        # save_intermediate=False,
        # verbose=False,
        # path=f"./BB-Immuno-RSmartExplosion/{name}/{int(time.time()*1000000)}",

################# MULTILEVEL SMART MERGE ##################
        ## IMPORTANT
        graph=f"./networks/{name}.gml",
        to_run="./hybrid-ia",
        ## HARD LIMITS
        # max_levels=100,
        # mod_goal= 0.2
        max_time=max_time,
        ## TYPE OF MERGE
        smart_merge=True,
        merge_min_ratio=0.5,
        hybrid_it="i_linear",
        ## ESPLOSIONI
        explosion=2,
        try_close=1,
        last_try=False,
        expl_min_ratio=1.5, 
        ## UTILITY
        # add_args=add_arg,
        seed=None,
        save_intermediate=True,
        verbose=True,
        path=f"./test/{name}/{int(time.time()*1000000)}",


    )


if __name__ == "__main__":
    with Pool(n_process) as p:
        p.map(bench, full_list)

# %%
