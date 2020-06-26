# %%
import os
from statistics import mean
import json
import matplotlib.pyplot as plt
import importlib
# from multi import hybrid_multi_level
import multi as m
import pandas as pd
import datetime
import cProfile
import numpy as np
%load_ext line_profiler
#   -a|--max-age int
#      Max age of the antibodies (tau)
#   -d|--duplicates int
#      Number of duplicates for each antibody
#   -e|--elitist
#      Elitist aging operator
#   -o|--optimal num
#      Optimal solution value
#   -p|--population-size int
#      Size of the population of antibodies
#   -r|--mutation-shape num
#      Value that determines the shape of the hypermutation (rho)
#   -s|--seed int
#      Seed for the random number generator
#   -t|--max-iterations int
#      Max number of iterations

# %%
# PROFILING
importlib.reload(m)
add_arg = ["-t", "10"]
%lprun - f m.hybrid_multi_level m.hybrid_multi_level("email.gml", levels=20, add_args=add_arg, try_close=2,)


# %%
importlib.reload(m)
# MULTI_LEVEL
add_arg = ["-t", "500", "-s", "1"]
res = m.hybrid_multi_level(
    "email.gml",
    levels=9999999,
    # mod_goal= 0.2
    add_args=add_arg,
    bomb_max=True,
    explosion=1,
    try_close=2,
    seed=1,
    path="./Bench-Email/500")
# trace = pd.read_csv("./trace.csv", index_col=0)

# %%

# print(max(fit_hist))
plt.figure(figsize=(20, 20))

rootdir = './Bench-Email/'
for subdir, dirs, files in os.walk(rootdir):
    break
# dirs=[float(i) for i in dirs]
# dirs.sort()
dirs = sorted(dirs, key=lambda x: int("".join([i for i in x if i.isdigit()])))
# dirs=[str(1*i) for i in dirs]
# for i in [2,10,100,200,750,999,1000,1001,1002, 1250,1500]:
for i in dirs:
    with open(f"./Bench-Email/{i}/res.json") as j:
        r = json.load(j)
    s = []
    best = []
    for ii in range(len(r["fit_hist"])):
        with open(f"./Bench-Email/{i}/R/R{ii}.txt") as t:
            arr = t.read().replace("\n", "").split("\t")
            s += [(0 if not s else s[-1])+float(arr[-1])]
            if not best:
                best += [float(arr[9])]
            else:
                if float(arr[9])>best[-1]:
                    best +=[float(arr[9])]
                else:
                    best += [best[-1]]

            # best += [best[-1] if not best else [
            #     float(arr[9]) if float(arr[9]) > best[-1] else best[-1]]]
    print(i, datetime.timedelta(seconds=s[-1]),
          datetime.timedelta(seconds=r["exe_time"]), r["best_fit"])
    ax1 = plt.subplot(221)
    ax1.plot(s, r["fit_hist"], label=f"{i}")
    ax1.plot(s, best,label=f"{i}")
    ax1.legend()

    ax3 = plt.subplot(223)
    ax3.plot(r["fit_hist"], label=f"{i}")
    ax3.legend()

    ax2 = plt.subplot(222)
    ax2.plot(s, np.array(r["fit_hist"])/r["best_fit"], label=f"{i}")

# for i in [1000]:
#     with open(f"./Bench-Power/{i}/res.json") as j:
#         r = json.load(j)
#     s = []
#     for ii in range(len(r["fit_hist"])):
#         with open(f"./Bench-Power/{i}/R/R{ii}.txt") as t:
#             s += [(0 if not s else s[-1])+float(t.read().replace("\n", "").split("\t")[-1])]
#     print(datetime.timedelta(seconds=s[-1]),
#           datetime.timedelta(seconds=r["exe_time"]), r["best_fit"])
#     plt.subplot(551)
#     plt.plot(s,r["fit_hist"], label=f"{i}")
#     plt.legend()

#     plt.subplot(552)
#     plt.plot(s,np.array(r["fit_hist"])/r["best_fit"], label=f"{i}")


ax1.set_xlabel("Time (s)")
ax1.set_title("Absolute reached value")
ax1.grid()
# plt.hlines(0.57,0,2500)

ax2.set_title("Percentage of final reached value")
# plt.hlines(0.9,0,2500)
ax2.set_xlabel("Time (s)")
ax2.grid()

# plt.plot(res["fit_hist"])

# %%
# SPEED-UP TEST: RACE TO MODULARITY - REACH THE MASTER
# In this benchmark the original algorithm will be executed,
# then the multi-level will try to reach the same solution

# importlib.reload(m)
# for i in range(10):
#     # Original
#     r = m.hybrid_multi_level(
#         "email.gml",
#         levels=1,
#         add_args=["-t", "10000"],
#         explosion=True,
#         bomb_max=True,
#         path=f"./Bench-Speed1/Base/{i}")

#     fit_hist = m.hybrid_multi_level(
#         "email.gml",
#         levels=9999999,
#         mod_goal=r["best_fit"],
#         add_args=["-t", "100"],
#         explosion=True,
#         bomb_max=True,
#         path=f"./Bench-Speed1/Multi/{i}")


# %%
# READING RES FOR SPEED-UP TEST: RACE TO MODULARITY
tB_arr = []
tM_arr = []
sp_arr = []
print("Time Base".ljust(8), "Time Mult".ljust(8),
      "SpeedUp".ljust(7), "Modularity".ljust(8))
for i in range(10):
    with open(f"./Bench-Speed1/Base/{i}/res.json", "r") as j:
        data = json.load(j)
        timeB = data["exe_time"]
        tB_arr += [timeB]
        bf = data["best_fit"]
    with open(f"./Bench-Speed1/Multi/{i}/res.json", "r") as j:
        timeM = json.load(j)["exe_time"]
        tM_arr += [timeM]
    sp_arr += [timeB/timeM]
    print(f"{timeB:3.5f} {timeM:3.5f} {sp_arr[-1]:3.5f} {bf:3.5f}")

print("Mean")
print(f"{mean(tB_arr):3.5f} {mean(tM_arr):3.5f} {mean(sp_arr):3.5f}")


# %%
# SPEED-UP TEST: RACE TO MODULARITY
# In this benchmark the original algorithm will be executed,
# then the multi-level will try to reach the same solution

importlib.reload(m)
for i in range(10):
    # Original
    r = m.hybrid_multi_level(
        "email.gml",
        levels=1,
        add_args=["-t", "100", "-o", "0.2"],
        explosion=True,
        bomb_max=True,
        path=f"./Bench-SpeedMod1/Base/{i}")

    fit_hist = m.hybrid_multi_level(
        "email.gml",
        levels=9999999,
        mod_goal=r["best_fit"],
        add_args=["-t", "100"],
        explosion=True,
        bomb_max=True,
        path=f"./Bench-SpeedMod1/Multi/{i}")


# %%
# IMPROVEMENT OVER ITERATION - HYBRID-IA and MULTILEVEL
# Testing with the same seed (1) but different n of iterations

importlib.reload(m)
for i in range(300, 400, 10):
    # Original
    r = m.hybrid_multi_level(
        "email.gml",
        levels=1,
        add_args=["-t", f"{100*i}", "-s", "1"],
        explosion=1,
        bomb_max=True,
        try_close=2,
        seed=1,
        path=f"./Bench-HybridIA/{100*i}")


# %%

plt.figure(figsize=(50, 50))
# plt.suptitle("HybridIA benchmark")
it_a = []
time_a = []
fit_a = []
# for i in range(1,81):
rootdir = './Bench-HybridIA/'
for subdir, dirs, files in os.walk(rootdir):
    break
dirs = [int(i) for i in dirs]
dirs.sort()
for i in dirs:
    with open(f"./Bench-HybridIA/{i}/R/R0.txt") as j:
        r = j.read().replace("\n", "").split("\t")
        it_a += [float(r[8])]
        time_a += [float(r[-1])]
        fit_a += [float(r[-4])]


with open(f"./Bench-MultiLevel/res.json") as j:
    r = json.load(j)
s = []
hybrid_total_it = []
for ii in range(len(r["fit_hist"])):
    with open(f"./Bench-MultiLevel/R/R{ii}.txt") as t:
        hybrid_total_it += [ii*1000]
        s += [(0 if not s else s[-1]) +
              float(t.read().replace("\n", "").split("\t")[-1])]
print(datetime.timedelta(seconds=s[-1]),
      datetime.timedelta(seconds=r["exe_time"]), r["best_fit"])
plt.subplot(551)
plt.plot(s, r["fit_hist"], label=f"Multi")
plt.legend()

plt.subplot(552)
plt.plot(hybrid_total_it, r["fit_hist"], label=f"Multi")


plt.subplot(551)
plt.plot(time_a, fit_a, label="Hybrid-IA")
plt.xlabel("Time (s)")
plt.title("Results over time")
plt.grid()
# plt.hlines(0.57,0,2500)
plt.subplot(552)
plt.plot(it_a, fit_a, label="Hybrid-IA")
plt.title("Results over iterations")
plt.xlabel("Iterations")
plt.grid()

# %%

# %%

# %%
