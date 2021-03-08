# %%
import cdlib
import networkx as nx
import pandas as pd
from collections import defaultdict
from cdlib import evaluation, algorithms
import json
import tqdm.notebook as tq


def to_NC(partition, graph, name):
    my_inverted_dict = defaultdict(list)
    {my_inverted_dict[v].append(k) for k, v in partition.items()}
    return cdlib.NodeClustering(list(my_inverted_dict.values()), graph, name)


def get_best_partition(path):
    with open(f"{path}res.json") as j:
        r = json.load(j)
    tr = pd.read_csv(f"{path}trace.csv", index_col=0)
    tr = tr[f"R{r['best_fit_li']}"].to_dict()
    return to_NC(tr, nx.read_gml(f"{path}G/G0.gml", label="id"), "Hybrid-Ia")


def find_mod(g, it):
    """
    Find Louvain modularity
    """
    res = -2
    for i in tq.tqdm(range(it), leave=False):
        lp_coms = algorithms.louvain(g, randomize=True)
        res = (
            lp_coms.newman_girvan_modularity().score
            if lp_coms.newman_girvan_modularity().score > res
            else res
        )
        # print(lp_coms.newman_girvan_modularity())
    return {"mod": res, "com": lp_coms}
# %%
# g = nx.karate_club_graph()
g = nx.read_gml("./power.gml")
lp_coms = algorithms.louvain(g, randomize=True)
# leiden_coms = algorithms.leiden(g)
print(lp_coms.newman_girvan_modularity())


# %%
tr = pd.read_csv("test/power/1615159868223111/trace.csv", index_col=0).iloc[:, 0].to_dict()

clust = to_NC(tr, nx.read_gml("./networks/power.gml", label="id"), "Hybrid-Ia")
# clust=to_NC(par,nx.read_gml("./karate.gml"),"Hybrid-Ia")
# clust = to_NC(par, g, "Hybrid-Ia")
print(clust.newman_girvan_modularity())
# print(clust.edges_inside())
# print(clust.communities)
# print(clust.link_modularity)


# %% Vs LOUVAIN, CHECK IF LOST MODULARITY
dir=f"t-runs/results-smart-merge/power/1614074403316572"
with open(f"{dir}/res.json") as j:
    r = json.load(j)

    # for i in range(0,len(r["fit_hist"]),20):
    for i in [0,"f"]:
        G=nx.read_gml(f"{dir}/G/G{i}.gml")
        re = find_mod(G, 5)
        # print(f"{i} {G.number_of_nodes()} {r['fit_hist'][i]} {re['mod']:2.5f} {re['mod']/float(r['fit_hist'][i]):2.5f}")
        print(f"{i} {G.number_of_nodes()} {r['fit_hist'][-1]} {re['mod']:2.5f} {re['mod']/float(r['fit_hist'][-1]):2.5f}")

# %% NORMALIZED MUTUAL INFORMATION
g = nx.read_gml("./networks/email.gml", label="id")
lp_coms = algorithms.louvain(g, randomize=True)

hy_coms = get_best_partition("./BB-hybridIA-smartMerge/email/1612622221743967/")

evaluation.normalized_mutual_information(lp_coms, hy_coms)

# %%
print(lp_coms.newman_girvan_modularity())
print(hy_coms.newman_girvan_modularity())
# %%
partition = pd.read_csv("test/power/1615159868223111/trace.csv", index_col=0).iloc[:, 0].to_dict()
my_inverted_dict = defaultdict(list)
{my_inverted_dict[v].append(k) for k, v in partition.items()}

nx.algorithms.community.quality.modularity(nx.read_gml("./networks/power.gml", label="id"),list(my_inverted_dict.values()))
# %%
