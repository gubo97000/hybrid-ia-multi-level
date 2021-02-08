# %%
import multi as m
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
        max_levels=20,
        hybrid_it= "i_linear",
        explosion=0,
        try_close=0,
        path=f"./Profiler/")

%lprun profile_it()

# dat=pd.read_csv("./trace.csv")

# %%
