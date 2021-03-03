#%%
import networkx as nx

import pandas as pd
from gml import write_gml


def add_comm(G, tr):
    return

#MultiLevel
tr = (
    pd.read_csv(
        "t-runs/results-smart-merge/power/1614074403316572/trace.csv", index_col=0
    )
    .iloc[:, 0]
    .to_dict()
)
G = nx.read_gml(
    "networks/power.gml", label="id"
)
nx.set_node_attributes(G, tr, name="comm")
write_gml(G,"./GT.gml")
# %%
import io
#Hybrid
rootdir="t-runs/results-hybridia/power/1614003632375487"

with open(f"./{rootdir}/R.txt","r") as ff:
    arr=ff.readline().replace("\n", "").split("\t")
# print(arr[-2])
comms=arr[-2].replace(",","\n").replace(":",",")
# print(comms)
data= io.StringIO(comms)
tr = (
    pd.read_csv(
        data, index_col=0, header=None
    )
    .iloc[:, 0]
    .to_dict()
)
G = nx.read_gml(
    "networks/power.gml", label="id"
)
nx.set_node_attributes(G, tr, name="comm")
write_gml(G,"./GT.gml")
# %%