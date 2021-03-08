# %%
import multi_level as m
import importlib
import line_profiler
%load_ext line_profiler

# %%
# PROFILING
importlib.reload(m)

def profile_it():
    m.hybrid_multi_level_beta(
        # "./networks/email.gml",
        # smart_merge=True,
        # # max_levels=20,
        # max_time=50,
        # # hybrid_it= "ratio-10-40",
        # hybrid_it= "10",
        # explosion=0,
        # try_close=0,
        # verbose=True,
        # save_intermediate=True,
        # path=f"./Profiler/",

        graph=f"./networks/power.gml",
        save_intermediate=True,
        verbose=True,
        seed=None,

################# MULTILEVEL RANDOM FULL EXPLOSION ##################
        ## IMPORTANT
        # to_run="./immuno-ia", #EXEC NAME
        ## HARD LIMITS
        max_time=1000,
        ## TYPE OF MERGE
        smart_merge=False,
        hybrid_it="10",
        ## ESPLOSIONI
        explosion=5,
        try_close=1, #To enforce time limit
        expl_min_ratio=0.5, # >1 = Full explosion
        ## UTILITY
        path=f"./BB-Immuno-RFullExplosion/email/pr",

        
        )

# %lprun -f m.hybrid_multi_level_beta -f m.add_trace profile_it()
profile_it()
# dat=pd.read_csv("./trace.csv")

# %%
