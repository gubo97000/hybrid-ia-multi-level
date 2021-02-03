# %%
import multi as m
import importlib
import line_profiler
%load_ext line_profiler

# %%
# BULK TEST FOR MULTI-LEVEL
importlib.reload(m)

%lprun -f m.add_trace m.hybrid_multi_level_beta(    "./networks/power.gml",    smart_merge=True,  max_levels=10,   hybrid_it= "i_linear",    add_args=[],explosion=2,try_close=1,path=f"./Profiler/")

# dat=pd.read_csv("./trace.csv")

# %%
