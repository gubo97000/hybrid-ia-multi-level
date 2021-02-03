# %%
# import pandas as pd
# import shutil
# import os
import subprocess

# import networkx as nx
# import matplotlib.pyplot as plt
# from gml import write_gml
# import random
# import math
# from timeit import default_timer as timer
import json

# from pathlib import Path
import multi as m
# import multiprocessing as mp
from multiprocessing import Pool
import time


######################
# EMAIL:1700, YEAST:7000, POWER:20000
# Il nome è usato anche per prendere il .gml con lo stesso identico nome
full_list = (
    [["email", "1700"]] * 50 + [["yeast", "7000"]] * 50 + [["power", "20000"]] * 50
)
n_process = 6  # Numero di processi contemporanei
######################


def bench(arg):
    name = arg[0]
    c = arg[1]
    path = f"./bench-batch-hybrid/{name}/{int(time.time()*1000000)}"
    m.prepare_folders(path)

    # MULTI_LEVEL
    print(f"benching {path}")
    args = ["./hybrid-ia", "-i", f"./{name}.gml", "-t", "30000", "-c", f"{c}", "-v"]
    # res = subprocess.run(args, capture_output=True, universal_newlines=True)  # 3.8 version
    res = subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )  # 3.6 version

    # Saving Raw Output in R folder
    with open(f"{path}/R.txt", "w") as t:
        print(res.stdout, file=t)

    # Results cleaning
    arrRes = [
        [re[0], re[1]] for re in (r.split("\t") for r in res.stderr.split("\n") if r)
    ]
    mod = [r[0] for r in arrRes]
    time_h = [r[1] for r in arrRes]

    with open(f"{path}/T_M.txt", "w") as f:
        json.dump({"time_hist": time_h, "fit_hist": mod}, f)
    # print("Done")


if __name__ == "__main__":
    with Pool(n_process) as p:
        p.map(bench, full_list)