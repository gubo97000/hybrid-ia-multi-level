# %%
from IPython.core.display import display_html, display_markdown
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
import tqdm as tq


def color_light(color, amount=0.5):
    import matplotlib.colors as mc
    import colorsys

    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


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
    # display(stat)
    return stat


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
            if fold[0] in [
                "./bench-batch-hybrid",
                "./BB-hybridIA",
                "t-runs/results-ia",
                "t-runs/results-hybridia",
            ]:  # Pure
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

    # plt.show()
    return fig


# %% FULL COMPARE
plot_compare(
    ["Email", "Yeast", "Power"],
    [
        ["BB/BB-Immuno", "xkcd:purple", "Mean Immunologic"],
        ["BB/BB-Immuno-multiLevel", "xkcd:green", "Mean MultiLevel"],
        ["BB/BB-Immuno-RSmartExplosion", "xkcd:red", "Mean Smart Explosion"],
        ["BB/BB-hybridIA", "xkcd:orange", "Mean HybridIA"],
        ["BB/BB-hybridIA-smartMerge", "xkcd:blue", "Mean HybridIA + Smart Merge"],

        ["t-runs/results-ia", "xkcd:purple", "Immunologic"],
        ["t-runs/results-random-explosion","xkcd:green","Immunologic + Random Explosion"],
        ["t-runs/results-smart-explosion", "xkcd:red", "Immunologic + Smart Explosion"],
        ["t-runs/results-hybridia", "xkcd:orange", "HybridIA"],
        ["t-runs/results-smart-merge", "xkcd:blue", "HybridIA + Smart Merge"],
        # ["test", "xkcd:green", "HybridIA + Smart Merge"],
    ],
    pdf="C_Full_Compare_Graph",
)
#%% FULL STAT TABLE
pd.options.display.latex.repr = True
pd.options.display.latex.repr = False
networks = ["Email", "Yeast", "Power"]
to_comp = [
    # ["BB/BB-Immuno", "Immunologic"],
    # ["BB/BB-Immuno-multiLevel", "Immunologic + M-L Explosion"],
    # ["BB/BB-Immuno-RSmartExplosion", "Immunologic + M-L Smart Explosion"],
    # ["BB/BB-hybridIA", "HybridIA"],
    # ["BB/BB-hybridIA-smartMerge", "HybridIA + Smart Merge"],
    # ["BB/BB-hybridIA-smartMerge-fix", "fix"],
    ["t-runs/results-ia", "Immunologic"],
    ["t-runs/results-random-explosion", "Immunologic + Random Explosion"],
    ["t-runs/results-smart-explosion", "Immunologic + Smart Explosion"],
    ["t-runs/results-hybridia", "HybridIA"],
    ["t-runs/results-smart-merge", "HybridIA + Smart Merge"],
]
stat = stat_table(networks, to_comp)
display(stat)

# latex_str = stat.to_latex(caption=to_comp)
html_str = stat.to_excel("./Plots/table.xlsx")

# %% COMPARE IMMUNE
plot_compare(
    ["Email", "Yeast", "Power"],
    [
        # ["./bench-batch-hybrid", "xkcd:purple", "Mean Immunologic"],
        # ["./bench-batch", "xkcd:green", "Mean MultiLevel"],
        # ["./bench-batch-beta", "xkcd:red", "Mean Smart Explosion"],
        # ["./BB-hybridIA", "xkcd:black", "Mean HybridIA"],
        # ["./BB-hybridIA-smartMerge1", "xkcd:blue", "Mean HybridIA + Smart Merge"],
        ["t-runs/results-ia", "xkcd:purple", "Mean Immunologic"],
        ["t-runs/results-random-explosion", "xkcd:green", "Mean MultiLevel"],
        ["t-runs/results-smart-explosion", "xkcd:red", "Mean Smart Explosion"],
        # ["t-runs/results-hybridia", "xkcd:orange", "Mean HybridIA"],
        # ["t-runs/results-smart-merge", "xkcd:blue", "Mean HybridIA + Smart Merge"],
    ],
    pdf="Immune_Compare_Graph",
)
# %% COMPARE HYBRID
plot_compare(
    ["Email", "Yeast", "Power"],
    [
        # ["./bench-batch-hybrid", "xkcd:purple", "Mean Immunologic"],
        # ["./bench-batch", "xkcd:green", "Mean MultiLevel"],
        # ["./bench-batch-beta", "xkcd:red", "Mean Smart Explosion"],
        # ["./BB-hybridIA", "xkcd:black", "Mean HybridIA"],
        # ["./BB-hybridIA-smartMerge1", "xkcd:blue", "Mean HybridIA + Smart Merge"],
        # ["t-runs/results-ia", "xkcd:purple", "Mean Immunologic"],
        # ["t-runs/results-random-explosion", "xkcd:green", "Mean MultiLevel"],
        # ["t-runs/results-smart-explosion", "xkcd:red", "Mean Smart Explosion"],
        ["t-runs/results-hybridia", "xkcd:orange", "Mean HybridIA"],
        ["t-runs/results-smart-merge", "xkcd:blue", "Mean HybridIA + Smart Merge"],
    ],
    pdf="Hybrid_Compare_Graph",
)


# %% FIXING SMART MERGE
importlib.reload(bu)
names = ["Email", "Yeast", "Power"]
final_pdf_name = False
# final_pdf_name = f"./Plots/No_Bomb_Graph{names}"
#######

fig = plot_compare(names, [["./BB-hybridIA", "xkcd:black", "Mean HybridIA"],],)
#######

plt.figure(fig.number)
count = 1
for pdf_name in names:
    ax1 = plt.subplot(int(f"{len(names)}1{count}"))
    count += 1

    ####Fix####
    avg, log = bu.multiAverage(f"./BB-hybridIA-smartMerge1/{pdf_name.lower()}")
    time, bf = [], []
    for name, ex in log.items():
        f_h = ex["res"]["fit_hist"]
        c = 0
        ######## No improvement for n turn (No good)
        # for i in range(len(f_h)):
        #     if i>0:
        #         if f_h[i]>f_h[i-1]:
        #             c=0
        #     c += 1
        #     if c==5:
        #         break
        ######## Check if value are close
        # for i in range(len(f_h)):
        #     if i>30:
        #         if math.isclose(f_h[i],f_h[i-30], rel_tol=1e-05):
        #             break
        ######## Time condition
        for i in range(len(f_h)):
            if ex["h_time"][i] > 6000:
                break

        time += [ex["h_time"][i]]
        bf += [max(ex["h_best_fit"][:i])]

        ax1.plot(
            ex["h_time"][:i], ex["h_best_fit"][:i], c=color_light("xkcd:green", 1.8)
        )

    # Save Fixed
    filename = f"./BB-h-sm-fix/{pdf_name.lower()}/fixed/fix.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump({"time": time, "bf": bf}, f)
    ################################################################

    ax1.set_xlabel("Time (s)")
    # ax1.set_xlabel("Time (s)", loc="right") #Only on matplotlib 3.3.3
    ax1.set_ylabel("Modularity")
    ax1.set_title(f"Modularity over time - {pdf_name}")
    ax1.yaxis.set_major_locator(plt.MaxNLocator(11))
    ax1.grid()


if final_pdf_name:
    plt.savefig(f"{final_pdf_name}.jpg", format="jpg", bbox_inches="tight")
    plt.savefig(f"{final_pdf_name}.pdf", format="pdf", bbox_inches="tight")

plt.show()


# GET FIxed STAT TABLE
pd.options.display.latex.repr = True
pd.options.display.latex.repr = False
networks = ["Email", "Yeast", "Power"]
to_comp = [
    # ["./bench-batch-hybrid", "Immunologic"],
    # ["./bench-batch", "MultiLevel"],
    # ["./bench-batch-beta", "Smart Explosion"],
    # ["./BB-hybridIA", "HybridIA"],
    # ["./BB-hybridIA-smartMerge", "HybridIA + Smart Merge"],
    ["./BB-hybridIA-smartMerge1", "HybridIA + Smart Merge"],
    ["./BB-h-sm-fix", "fix"],
]
stat = stat_table(networks, to_comp)

#%% GET STAT TABLE  #############################################
pd.options.display.latex.repr = True
pd.options.display.latex.repr = False
networks = ["Email", "Yeast", "Power"]
to_comp = [
    ["./bench-batch-hybrid", "Immunologic"],
    ["./bench-batch", "Immunologic + M-L Explosion"],
    ["./bench-batch-beta", "Immunologic + M-L Smart Explosion"],
    ["./BB-hybridIA", "HybridIA"],
    # ["./BB-hybridIA-smartMerge", "HybridIA + Smart Merge"],
    ["./BB-hybridIA-smartMerge1", "HybridIA + Smart Merge"],
    # ["./BB-h-sm-fix", "fix"],
]
stat = stat_table(networks, to_comp)

# latex_str = stat.to_latex(caption=to_comp)

#%% No Explosion Plot #########################################################
importlib.reload(bu)
names = ["Email", "Yeast", "Power"]
final_pdf_name = False
final_pdf_name = f"./Plots/No_Bomb_Graph{names}"
#######

fig = plot_compare(names, [["./bench-batch-hybrid", "xkcd:purple", "Immunologic"],],)
# plt.figure(figsize=(10, len(names) * 5))
plt.figure(fig.number)
count = 1
for pdf_name in names:
    ax1 = plt.subplot(int(f"{len(names)}1{count}"))
    count += 1
    ####No Explosion ####
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
            ex["h_time"][: stop_i + 1],
            ex["h_best_fit"][: stop_i + 1],
            c=color_light("xkcd:green", 1.8),
        )

        all_max_mod += [ex["h_best_fit"][stop_i + 1]]
    stop_i = next(i for i, v in enumerate(avg["h_best_fit"]) if v >= mean(all_max_mod))

    ax1.plot(
        avg["h_time"][:stop_i],
        avg["h_best_fit"][:stop_i],
        linewidth=2,
        c="xkcd:green",
        label=f"Immunologic + Simple Multi-Level",
    )

    ax1.legend()

if final_pdf_name:
    plt.savefig(f"{final_pdf_name}.jpg", format="jpg", bbox_inches="tight")
    plt.savefig(f"{final_pdf_name}.pdf", format="pdf", bbox_inches="tight")

# plt.show()


# %%
for n in ["email", "yeast", "power"]:
    rootdir = f"./bench-batch/{n}"
    for subdir, dirs, files in os.walk(rootdir):
        break
    for i in tq.tqdm(dirs, desc=rootdir, leave=False):
        with open(f"./{rootdir}/{i}/res.json") as j:
            r = json.load(j)
        open(f"./{rootdir}/{i}/R.txt", "w").close()
        for ii in range(len(r["fit_hist"])):
            with open(f"./{rootdir}/{i}/R/R{ii}.txt") as t:
                arr = t.read().replace("\n", "")
                with open(f"./{rootdir}/{i}/R.txt", "a") as ff:
                    ff.write(arr + "\n")
# %%
rootdir = "./bench-batch-beta/email"
for subdir, dirs, files in os.walk(rootdir):
    break
for i in tq.tqdm(dirs, desc=rootdir, leave=False):
    with open(f"./{rootdir}/{i}/res.json") as j:
        r = json.load(j)
        with open(f"./{rootdir}/{i}/R.txt", "r") as ff:
            for ii in range(len(r["fit_hist"])):
                arr = ff.readline().replace("\n", "").split("\t")
                print(len(arr))
# %%
