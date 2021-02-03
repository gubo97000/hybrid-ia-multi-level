# %%
import multi as m
from multiprocessing import Pool
import time
import importlib
importlib.reload(m)
######################
# EMAIL:20 minuti, YEAST:2 ore, POWER:9 ore
# Il nome è usato anche per prendere il .gml con lo stesso identico nome
full_list = ["power"] * 1
# ["email"]*10 +

# +["yeast"]*5
n_process = 3  # Numero di processi contemporanei
######################


def bench(name):
    # MULTI_LEVEL
    # add_arg = ["-t", "1000"]
    res = m.hybrid_multi_level_beta(
        f"{name}.gml",
        max_levels=9999999,
        smart_merge=True,
        # mod_goal= 0.2
        hybrid_it="20",
        # add_args=add_arg,
        # bomb_max=True,
        explosion=0,
        try_close=0,
        min_ratio=1,
        seed=None,
        save_trace=True,
        path=f"./bench-batch-hybridIA-beta/{name}/{int(time.time()*1000000)}",
    )


if __name__ == "__main__":
    with Pool(n_process) as p:
        p.map(bench, full_list)

# %%
