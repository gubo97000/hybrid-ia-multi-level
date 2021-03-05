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
        "./networks/email.gml",
        smart_merge=True,
        # max_levels=20,
        max_time=100,
        hybrid_it= "i_linear",
        explosion=0,
        try_close=0,
        verbose=True,
        save_intermediate=True,
        path=f"./Profiler/")

# %lprun -f m.hybrid_multi_level_beta -f m.add_trace -f m.fix_disconnected_comms profile_it()
profile_it()
# dat=pd.read_csv("./trace.csv")

# %%
