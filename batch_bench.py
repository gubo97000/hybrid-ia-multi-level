# %%
import multi as m
from multiprocessing import Pool
import time
import importlib

importlib.reload(m)
######################
# Il nome è usato anche per prendere il .gml con lo stesso identico nome
full_list = ["email"]*10 
# + ["power"] * 2
# +["yeast"]*5
n_process = 2  # Numero di processi contemporanei
######################


def bench(name):
    # MULTI_LEVEL
    # add_arg = ["-t", "1000"]
    res = m.hybrid_multi_level_beta(
        f"./networks/{name}.gml",
        # max_levels=100,
        max_time=750,
        smart_merge=False,
        # mod_goal= 0.2
        hybrid_it="i_linear",
        # add_args=add_arg,
        explosion=0,
        try_close=0,
        min_ratio=0.5,
        seed=None,
        save_trace=True,
        path=f"./BB-hybridIA-multiLevel/{name}/{int(time.time()*1000000)}",
    )


if __name__ == "__main__":
    with Pool(n_process) as p:
        p.map(bench, full_list)

# %%
