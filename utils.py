#%%
import networkx as nx

import pandas as pd
from gml import write_gml

#%% Create graph for gephi

# rootdir = "t-runs-conn/results-smart-merge/yeast/1615226998873767"
# rootdir = "t-runs-conn/results-smart-explosion/yeast/1615317195355697"
# rootdir = "t-runs/results-smart-merge/power/1614074403316572"
rootdir = "t-runs/results-smart-merge/email/1614069315438030"
# rootdir = "Profiler"
G = nx.read_gml("networks/email.gml", label="id")
# MultiLevel

tr = pd.read_csv(f"{rootdir}/trace.csv", index_col=0).iloc[:, 0].to_dict()
# tr2 = pd.read_csv(f"{rootdir2}/trace.csv", index_col=0).iloc[:, 0].to_dict()

nx.set_node_attributes(G, tr, name="comm")
# nx.set_node_attributes(G, tr2, name="comm2")

write_gml(G, "./GT.gml")
# %% Create graph for gephi no multilevel
import io

# Hybrid
rootdir = "t-runs/results-hybridia/power/1614003632375487"

with open(f"./{rootdir}/R.txt", "r") as ff:
    arr = ff.readline().replace("\n", "").split("\t")
# print(arr[-2])
comms = arr[-2].replace(",", "\n").replace(":", ",")
# print(comms)
data = io.StringIO(comms)
tr = pd.read_csv(data, index_col=0, header=None).iloc[:, 0].to_dict()
G = nx.read_gml("networks/power.gml", label="id")
nx.set_node_attributes(G, tr, name="comm")
write_gml(G, "./GTh.gml")

# %% Fix wrong modularity (t-runs-conn problem)
import json
import os
import pquality as pq
import tqdm as tq

network = "power"
rootdirs = f"t-runs-conn/results-smart-merge/{network}"
G = nx.read_gml(f"./networks/{network}.gml", label="id")

rootdirs = rootdirs if type(rootdirs) == list else [rootdirs]
time = []
bf = []
it = []
names = []
for rootdir in rootdirs:
    for _subdir, dirs, _files in os.walk(rootdir):
        break
    for i in tq.tqdm(dirs, desc=rootdir, leave=False):
        with open(f"./{rootdir}/{i}/res.json") as j:
            r = json.load(j)
        r["best_fit_old"] = r["best_fit"]

        partition = (
            pd.read_csv(f"./{rootdir}/{i}/trace.csv", index_col=0).iloc[:, 0].to_dict()
        )

        r["best_fit"] = float(pq.PartitionQuality.community_modularity(partition, G))

        with open(f"./{rootdir}/{i}/res.json", "w") as j:
            json.dump(r, j)

        names += [i]
        time += [r["exe_time"]]
        bf += [r["best_fit"]]
        it += [len(r["fit_hist"])]


# %%
G = nx.read_edgelist("networks/email-Eu-core.txt")
# G = nx.read_gml("networks/emailEu.gml")
tr = (
    pd.read_csv(
        f"networks/email-Eu-core-department-labels.txt", delimiter=" ", header=None, index_col=0
    )
    .to_dict()
)
nx.set_node_attributes(G, tr, name="comm")
# write_gml(G,"networks/emailEu.gml")
# %%
