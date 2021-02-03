# %%
import cdlib
import networkx as nx
import pandas as pd
from collections import defaultdict
from cdlib import algorithms
import json


def to_NC(partition, graph, name):
    my_inverted_dict = defaultdict(list)
    {my_inverted_dict[v].append(k) for k, v in partition.items()}
    return cdlib.NodeClustering(list(my_inverted_dict.values()), graph, name)


def find_mod(g, it):
    res = -2
    for i in range(it):
        lp_coms = algorithms.louvain(g, randomize=True)
        res = lp_coms.newman_girvan_modularity(
        ).score if lp_coms.newman_girvan_modularity().score > res else res
        # print(lp_coms.newman_girvan_modularity())
    return {"mod": res, "com": lp_coms}


# %%
# g = nx.karate_club_graph()
g = nx.read_gml("./power.gml")
lp_coms = algorithms.louvain(g, randomize=True)
# leiden_coms = algorithms.leiden(g)
print(lp_coms.newman_girvan_modularity())


# %%
tr = pd.read_csv("./Bench-Karate/1000/trace.csv", index_col=0).R16.to_dict()

clust = to_NC(tr, nx.read_gml(
    "./Bench-Karate/1000/G/G0.gml", label='id'), "Hybrid-Ia")
# clust=to_NC(par,nx.read_gml("./karate.gml"),"Hybrid-Ia")
# clust = to_NC(par, g, "Hybrid-Ia")
print(clust.newman_girvan_modularity())
print(clust.edges_inside())
print(clust.communities)
print(clust.link_modularity)


# %%
with open(f"./Bench-Email/1000/res.json") as j:
    r = json.load(j)

for i in range(len(r["fit_hist"])):
    with open(f"./Bench-Email/1000/R/R{i}.txt") as t:
        arr_r = t.read().replace("\n", "").split("\t")
        print(f"{int(arr_r[1]):5d} {float(arr_r[9]):2.5f} ", end="", flush=True)
    r = find_mod(nx.read_gml(f"./Bench-Email/1000/G/G{i}.gml"), 20)
    print(f" {r['mod']:2.5f} {r['mod']/float(arr_r[9]):2.5f}")

# %%
