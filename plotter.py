# %%
from IPython.display import display

# from mpl_toolkits.mplot3d import Axes3D
import os
from statistics import mean

import json
import matplotlib.pyplot as plt
import importlib

# from multi import hybrid_multi_level
# import multi as m
import bench_util as bu

import pandas as pd

# import datetime
import numpy as np
import math

# import random
# from tqdm import tqdm


def color_light(color, amount=0.5):
    import matplotlib.colors as mc
    import colorsys

    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


# %% Single network plot ##########################################################
importlib.reload(bu)

plt.figure(figsize=(20, 20))
ax1 = plt.subplot(221)
ax2 = plt.subplot(222)
ax3 = plt.subplot(223)
ax4 = plt.subplot(224)

pdf_name = "B-Email"
avg, log = bu.multiAverage("./bench-batch-beta/email")
for name, ex in log.items():

    # ax1.plot(ex["h_time"], ex["res"]["fit_hist"], label=f"{name}", c="grey")
    ax1.plot(ex["h_time"], ex["h_best_fit"], c="grey")

    ax2.plot(ex["h_time"], np.array(ex["h_best_fit"]) / ex["h_best_fit"][-1], c="grey")

    # ax3.plot(ex["res"]["fit_hist"], label=f"{name}", c="grey")
    ax3.plot(ex["h_best_fit"], c="grey")

    ax4.plot(np.array(ex["h_best_fit"]) / ex["h_best_fit"][-1], c="grey")


# AVG plot
# ax1.plot(avg["h_time"], avg["fit_hist"], label=f"AVG")
ax1.plot(avg["h_time"], avg["h_best_fit"], label=f"AVG", c="red", linewidth=2)

ax2.plot(
    avg["h_time"],
    np.array(avg["h_best_fit"]) / avg["h_best_fit"][-1],
    label=f"AVG",
    c="red",
    linewidth=2,
)

ax3.plot(avg["h_best_lvl_fit"], label=f"AVG", c="red", linewidth=2)

ax4.plot(
    np.array(avg["h_best_lvl_fit"]) / avg["h_best_lvl_fit"][-1],
    label=f"AVG",
    c="red",
    linewidth=2,
)

ax = ax1
ax.set_xlabel("Time (s)")
ax.set_title("Modularity over time")
ax.yaxis.set_major_locator(plt.MaxNLocator(11))
ax.grid()
ax.legend()
# plt.hlines(0.57,0,2500)

ax = ax2
ax.set_title("current/final modularity over time")
ax.yaxis.set_major_locator(plt.MaxNLocator(11))
# plt.hlines(0.9,0,2500)
ax.set_xlabel("Time (s)")
ax.set_ylabel("current/final modularity")
ax.grid()
ax.legend()

ax3.set_title("Modularity over levels")
ax3.set_xlabel("Levels")
ax3.yaxis.set_major_locator(plt.MaxNLocator(11))
ax3.legend()
ax3.grid()

ax4.set_title("current/final modularity over levels")
ax4.yaxis.set_major_locator(plt.MaxNLocator(11))
# plt.hlines(0.9,0,2500)
ax4.set_xlabel("Levels")
ax4.set_ylabel("current/final modularity")
ax4.grid()
ax4.legend()

# plt.plot(res["fit_hist"])
plt.savefig(f"./Plots/M_Graphs_{pdf_name}.jpg", format="jpg", bbox_inches="tight")
plt.savefig(f"./Plots/M_Graphs_{pdf_name}.pdf", format="pdf", bbox_inches="tight")

# %% COMPARE EXPLOSION WITH HYBRID ###########################################
names = ["Email", "Yeast", "Power"]
final_pdf_name = False
final_pdf_name = f"./Plots/H_M_Graph{names}"
#########

importlib.reload(bu)
plt.figure(figsize=(10, len(names) * 5))
count = 1
for pdf_name in names:
    ax1 = plt.subplot(int(f"{len(names)}1{count}"))
    # ax2 = plt.subplot(int(f"{len(names)}2{count+1}"))
    count += 1

    ####COMPARE MULTI####
    avg, log = bu.multiAverage(f"./bench-batch/{pdf_name.lower()}")
    for name, ex in log.items():

        # ax1.plot(ex["h_time"], ex["res"]["fit_hist"])
        ax1.plot(ex["h_time"], ex["h_best_fit"], c="xkcd:silver")

        a = [i * 1000 for i in range(len(ex["res"]["fit_hist"]))]

        # ax2.plot(a, ex["res"]["fit_hist"])
        # ax2.plot(a, ex["h_best_fit"], c="grey")

    # ax1.plot(avg["h_time"], avg["fit_hist"], label=f"AVG")
    ax1.plot(
        avg["h_time"],
        avg["h_best_fit"],
        linewidth=2,
        c="xkcd:red",
        label=f"Mean Multi-Level",
    )

    a = [i * 1000 for i in range(len(avg["h_best_lvl_fit"]))]
    # ax2.plot(a, np.array(avg["h_best_lvl_fit"]), label=f"AVG", c="red", linewidth=2)

    #################
    # Hybrid plot

    avg, log = bu.hyAverage(f"./bench-batch-hybrid/{pdf_name.lower()}")
    for name, ex in log.items():

        ax1.plot(ex["time_hist"], ex["fit_hist"], c="lightblue")

    ax1.plot(
        avg["time_hist"],
        avg["fit_hist"],
        linewidth=2,
        c="xkcd:blue",
        label=f"Mean Immunologic",
    )

    # ax2.plot(a, np.array(avg["h_best_lvl_fit"]), label=f"AVG", c="red", linewidth=2)

    # rootdir = f'./bench-batch-hybrid/{pdf_name.lower()}'
    # for subdir, dirse, files in os.walk(rootdir):
    #     break
    # for one in tqdm(dirse, desc=rootdir):
    #     with open(f"{rootdir}/{one}/T_M.txt") as j:
    #         r = json.load(j)
    #         r["time_hist"]=[float(x) for x in r["time_hist"]]
    #         r["fit_hist"]=[float(x) for x in r["fit_hist"]]
    #         ax1.plot(r["time_hist"], r["fit_hist"], c="cyan")
    #         # ax2.plot(r["fit_hist"], c="cyan")

    ax1.set_xlabel("Time (s)")
    ax1.set_title(f"Modularity over time - {pdf_name}")
    ax1.yaxis.set_major_locator(plt.MaxNLocator(11))
    ax1.grid()
    ax1.legend()
    # ax1.hlines(0.57,0,2500)

    # ax2.set_title("Modularity over iterations")
    # ax2.set_xlabel("Iterations")

    # ax2.grid()
    # ax2.legend()
if final_pdf_name:
    plt.savefig(f"{final_pdf_name}.jpg", format="jpg", bbox_inches="tight")
    plt.savefig(f"{final_pdf_name}.pdf", format="pdf", bbox_inches="tight")

plt.show()

# %% TIME PER NODE AND EDGE for hybrid ########################################
importlib.reload(bu)

final_pdf_name = False
final_pdf_name = f"./Plots/Node-edge-time"

plt.figure(figsize=(10, 10))
ax1 = plt.subplot(221)
ax2 = plt.subplot(222)

t, n, links = bu.rel_timeVgraph(
    ["./bench-batch/email", "./bench-batch/yeast", "./bench-batch/power"], max_n=3,
)
# json.dump({"t":t,"n":n,"l":l}, "./e_l_cache.json")
s1 = ax1.scatter(t, n, 10, c=links, cmap="BuPu")
s2 = ax2.scatter(t, links, 10, c=n, cmap="BuPu")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("# of nodes")
ax2.set_ylabel("# of edges")
ax2.set_xlabel("Time (s)")
# leg= ax1.legend(*s1.legend_elements(num=4), title="# of edges")
# ax1.add_artist(leg)
leg = ax2.legend(*s2.legend_elements(num=4), title="# of nodes")
ax2.add_artist(leg)

if final_pdf_name:
    plt.savefig(f"{final_pdf_name}.jpg", format="jpg", bbox_inches="tight")
    plt.savefig(f"{final_pdf_name}.pdf", format="pdf", bbox_inches="tight")

plt.show()

# %matplotlib qt

# 3D
# fig = plt.figure(figsize=(20, 20))
# ax1 = fig.add_subplot(111, projection='3d')
# ax1.scatter(n, l, t)

# %%
def stat_table(networks, to_comp):
    importlib.reload(bu)
    stat = pd.DataFrame()
    for fold in to_comp:
        row = pd.DataFrame()
        for net in networks:
            if not row.empty:
                row = pd.concat(
                    [row, bu.batch_stats(f"{fold[0]}/{net.lower()}", net, fold[1])],
                    axis=1,
                )
            else:
                row = bu.batch_stats(f"{fold[0]}/{net.lower()}", net, fold[1])
        stat = pd.concat([stat, row])
    display(stat)
    return stat


#%% GET STAT TABLE
pd.options.display.latex.repr=True
pd.options.display.latex.repr=False
networks = ["Email", "Yeast", "Power"]
to_comp = [
        ["./bench-batch-hybrid", "Immunologic"],
        ["./bench-batch", "MultiLevel"],
        ["./bench-batch-beta", "Smart Explosion"],
        ["./BB-hybridIA", "HybridIA"],
        # ["./BB-hybridIA-smartMerge", "HybridIA + Smart Merge"],
        ["./BB-hybridIA-smartMerge1", "HybridIA + Smart Merge"],
        # ["./BB-h-sm-fix", "fix"],

    ]
stat = stat_table(networks, to_comp)

# latex_str = stat.to_latex(caption=to_comp)
# print(latex_str)
#%% No Explosion Plot #########################################################
names = ["Email", "Yeast", "Power"]
final_pdf_name = False
final_pdf_name = f"./Plots/No_Bomb_Graph{names}"
#######

importlib.reload(bu)
plt.figure(figsize=(10, len(names) * 5))
count = 1
for pdf_name in names:
    ax1 = plt.subplot(int(f"{len(names)}1{count}"))
    # ax2 = plt.subplot(int(f"{len(names)}2{count+1}"))
    count += 1

    ####Fixing Bad result####
    all_max_mod = []
    avg, log = bu.multiAverage(f"./bench-batch/{pdf_name.lower()}")
    for name, ex in log.items():
        # Check first time modularity stagnate
        stop_i = 0
        for stop_i in range(len(ex["h_best_fit"])):
            if ex["h_best_fit"][stop_i] == ex["h_best_fit"][stop_i + 1]:
                break
        # all_stop_i+=[stop_i+1]
        # ax1.plot(ex["h_time"], ex["res"]["fit_hist"])
        ax1.plot(
            ex["h_time"][: stop_i + 1], ex["h_best_fit"][: stop_i + 1], c="xkcd:silver"
        )

        all_max_mod += [ex["h_best_fit"][stop_i + 1]]
        # a = [i * 1000 for i in range(len(ex["res"]["fit_hist"]))]
        # ax2.plot(a, ex["res"]["fit_hist"])
        # ax2.plot(a, ex["h_best_fit"], c="grey")
    stop_i = next(i for i, v in enumerate(avg["h_best_fit"]) if v >= mean(all_max_mod))
    # ax1.plot(avg["h_time"], avg["fit_hist"], label=f"AVG")
    ax1.plot(
        avg["h_time"][:stop_i],
        avg["h_best_fit"][:stop_i],
        linewidth=2,
        c="xkcd:red",
        label=f"Immunologic + Simple Multi-Level",
    )

    #######COMPARE Immune ##########
    avg, log = bu.hyAverage(f"./bench-batch-hybrid/{pdf_name.lower()}")
    for name, ex in log.items():
        ax1.plot(ex["time_hist"], ex["fit_hist"], c="xkcd:pink", alpha=0.5)

    ax1.plot(
        avg["time_hist"],
        avg["fit_hist"],
        linewidth=2,
        c="xkcd:purple",
        label=f"Mean Immunologic",
    )

    ax1.set_xlabel("Time (s)")
    # ax1.set_xlabel("Time (s)", loc="right") #Only on matplotlib 3.3.3
    ax1.set_ylabel("Modularity")
    ax1.set_title(f"Modularity over time - {pdf_name}")
    ax1.yaxis.set_major_locator(plt.MaxNLocator(11))
    ax1.grid()
    ax1.legend()
    # ax1.hlines(0.57,0,2500)

    # ax2.set_title("Modularity over iterations")
    # ax2.set_xlabel("Iterations")

    # ax2.grid()
    # ax2.legend()

if final_pdf_name:
    plt.savefig(f"{final_pdf_name}.jpg", format="jpg", bbox_inches="tight")
    plt.savefig(f"{final_pdf_name}.pdf", format="pdf", bbox_inches="tight")

plt.show()

# %%
def plot_compare(networks, to_compare, pdf=False):
    names = networks
    if pdf:
        final_pdf_name = f"./Plots/{pdf}{names}.pdf"

    importlib.reload(bu)
    fig = plt.figure(figsize=(10, len(names) * 5))
    count = 1
    for network_name in names:
        ax1 = plt.subplot(int(f"{len(names)}1{count}"))
        # ax2 = plt.subplot(int(f"{len(names)}2{count+1}"))
        count += 1

        for fold in to_compare:
            if fold[0] in ["./bench-batch-hybrid", "./BB-hybridIA"]:  # Pure
                avg, log = bu.hyAverage(f"{fold[0]}/{network_name.lower()}")
                for name, ex in log.items():
                    ax1.plot(
                        ex["time_hist"],
                        ex["fit_hist"],
                        c=color_light(fold[1], 1.8),
                        alpha=0.4,
                    )
                ax1.plot(
                    avg["time_hist"],
                    avg["fit_hist"],
                    linewidth=2,
                    c=fold[1],
                    label=fold[2],
                )

            else:  # Multi-level
                avg, log = bu.multiAverage(f"{fold[0]}/{network_name.lower()}")
                for name, ex in log.items():
                    ax1.plot(
                        ex["h_time"],
                        ex["h_best_fit"],
                        c=color_light(fold[1], 2),
                        alpha=0.4,
                    )
                ax1.plot(
                    avg["h_time"],
                    avg["h_best_fit"],
                    linewidth=2,
                    c=fold[1],
                    label=fold[2],
                )

        ax1.set_xlabel("Time (s)")
        ax1.set_title(f"Modularity over time - {network_name}")
        ax1.yaxis.set_major_locator(plt.MaxNLocator(11))
        ax1.grid()
        ax1.legend()
        # ax1.hlines(0.57,0,2500)

        # ax2.set_title("Modularity over iterations")
        # ax2.set_xlabel("Iterations")

        # ax2.grid()
        # ax2.legend()
    if pdf:
        plt.savefig(f"{final_pdf_name}.jpg", format="jpg", bbox_inches="tight", dpi=200)
        plt.savefig(f"{final_pdf_name}.pdf", format="pdf", bbox_inches="tight")
        print(f"Plot saved: {final_pdf_name}")

    plt.show()
    return fig


# %%
plot_compare(
    ["Email", "Yeast", "Power"],
    [
        ["./bench-batch-hybrid", "xkcd:purple", "Mean Immunologic"],
        ["./bench-batch", "xkcd:green", "Mean MultiLevel"],
        ["./bench-batch-beta", "xkcd:red", "Mean Smart Explosion"],
        ["./BB-hybridIA", "xkcd:black", "Mean HybridIA"],
        ["./BB-hybridIA-smartMerge1", "xkcd:blue", "Mean HybridIA + Smart Merge"],
    ],
    "Smart_Merge_Compare_Graph",
)


# %%
names = ["Email", "Yeast", "Power"]
final_pdf_name = False
# final_pdf_name = f"./Plots/Fixed Smart{names}"
#######

importlib.reload(bu)
plt.figure(figsize=(10, len(names) * 5))
count = 1
for pdf_name in names:
    ax1 = plt.subplot(int(f"{len(names)}1{count}"))
    # ax2 = plt.subplot(int(f"{len(names)}2{count+1}"))
    count += 1

    ####Fix####
    avg, log = bu.multiAverage(f"./BB-hybridIA-smartMerge1/{pdf_name.lower()}")
    time,bf=[],[]
    for name, ex in log.items():
        f_h=ex["res"]["fit_hist"]
        c=0
        # for i in range(len(f_h)):
        #     if i>0:
        #         if f_h[i]>f_h[i-1]:
        #             c=0
        #     c += 1
        #     if c>5:
        #         break
# ######
        # for i in range(len(f_h)):
        #     if i>30:
        #         if math.isclose(f_h[i],f_h[i-30], rel_tol=1e-05):
        #             break
####
        for i in range(len(f_h)):
            if ex["h_time"][i] > 5431:
                break
        
        # stop=int(ex["res"]["best_fit_fi"])+5
        # stop=len(ex["h_time"])
        time+=[ex["h_time"][i]]
        bf+=[max(ex["h_best_fit"][:i])]
        ax1.plot(ex["h_time"][:i], ex["h_best_fit"][:i], c="xkcd:silver")

    filename = f"./BB-h-sm-fix/{pdf_name.lower()}/fixed/fix.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump({"time":time,"bf":bf},f)

    # ax1.plot(avg["h_time"], avg["fit_hist"], label=f"AVG")
    # ax1.plot(
    #     avg["h_time"],
    #     avg["h_best_fit"],
    #     linewidth=2,
    #     c="xkcd:red",
    #     label=f"Mean Multi-Level",
    # )

    ax1.set_xlabel("Time (s)")
    # ax1.set_xlabel("Time (s)", loc="right") #Only on matplotlib 3.3.3
    ax1.set_ylabel("Modularity")
    ax1.set_title(f"Modularity over time - {pdf_name}")
    ax1.yaxis.set_major_locator(plt.MaxNLocator(11))
    ax1.grid()
    ax1.legend()
    # ax1.hlines(0.57,0,2500)

    # ax2.set_title("Modularity over iterations")
    # ax2.set_xlabel("Iterations")

    # ax2.grid()
    # ax2.legend()

if final_pdf_name:
    plt.savefig(f"{final_pdf_name}.jpg", format="jpg", bbox_inches="tight")
    plt.savefig(f"{final_pdf_name}.pdf", format="pdf", bbox_inches="tight")

plt.show()
# %%
#%% GET STAT TABLE
pd.options.display.latex.repr=True
pd.options.display.latex.repr=False
networks = ["Email", "Yeast", "Power"]
to_comp = [
        # ["./bench-batch-hybrid", "Immunologic"],
        ["./bench-batch", "MultiLevel"],
        # ["./bench-batch-beta", "Smart Explosion"],
        # ["./BB-hybridIA", "HybridIA"],
        # ["./BB-hybridIA-smartMerge", "HybridIA + Smart Merge"],
        ["./BB-hybridIA-smartMerge1", "HybridIA + Smart Merge"],
        ["./BB-h-sm-fix", "fix"],

    ]
stat = stat_table(networks, to_comp)
