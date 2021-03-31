# %%
# import multi_level as m
import multi_level_bootstrap as m
import importlib
import line_profiler
%load_ext line_profiler

# %%
# PROFILING
importlib.reload(m)

def profile_it():
    m.hybrid_multi_level_beta(
        "./networks/email.gml",
        merge_min_ratio=0.5,
        expl_min_ratio=1.6,
        # bootstrap=True,
        # max_levels=999,
        max_time=120,
        hybrid_it= "ratio-10-40",
        # hybrid_it= 40,
        explosion=2,
        try_close=999,
        verbose=True,
        save_intermediate=True,
        path=f"./Profiler/",

        # graph=f"./networks/power.gml",
        # save_intermediate=True,
        # verbose=True,
        # seed=None,

################# MULTILEVEL RANDOM FULL EXPLOSION ##################
        # ## IMPORTANT
        # # to_run="./immuno-ia", #EXEC NAME
        # ## HARD LIMITS
        # max_time=1000,
        # ## TYPE OF MERGE
        # smart_merge=False,
        # hybrid_it="10",
        # ## ESPLOSIONI
        # explosion=5,
        # try_close=1, #To enforce time limit
        # expl_min_ratio=0.5, # >1 = Full explosion
        # ## UTILITY
        # path=f"./BB-Immuno-RFullExplosion/email/pr",

        
        )

# %lprun -f m.hybrid_multi_level_beta profile_it()
profile_it()
# dat=pd.read_csv("./trace.csv")

# %%
