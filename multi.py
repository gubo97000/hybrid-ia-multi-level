# %%
import pandas as pd
import shutil
import os
import subprocess
import networkx as nx
import matplotlib.pyplot as plt


def merge_nodes(G0, R0):
    """
    Returns a graph where each community of the original graph is a single node, 
    edges are modified accordingly to keep the same modularity.

    Parameters
    ----------
    G0 : nx.Graph
        The original graph 
    R0 : dict
        Computed communities

    Returns
    -------
    nx.Graph
        The processed graph
    """
    G1 = nx.Graph()
    # Creates nodes
    for n0 in R0:
        G1.add_node(R0[n0])

    # Cicle through edges in G0
    for (u, v, w) in G0.edges().data('weight', default=1):
        # Insert edges between communities, no issue if repeated
        G1.add_edge(R0[u], R0[v])
        # Compute weight
        G1.edges[R0[u], R0[v]]['weight'] = G1.edges[R0[u],
                                                    R0[v]].get('weight', 0) + w
    return G1


def explode_community(G0, trace, community:int):
    G1= nx.Graph()
    
    return G1


# %%
# DELETE AND CREATES ALL RESULTS DIRECTORIES
try:
    shutil.rmtree("./R", ignore_errors=True)
    shutil.rmtree("./G", ignore_errors=True)
    os.mkdir("./G")
    os.mkdir("./R")
except OSError as e:
    print("Error: %s - %s." % (e.filename, e.strerror))


# %%
# RUN MULTI-LEVEL
G0 = nx.read_gml('karate.gml', label='id')  # Original Graph
G0 = nx.convert_node_labels_to_integers(G0)  # Make sure first label is 0
nx.write_gml(G0, f"./G/G0.gml")
lvl = 10
for i in range(lvl):  # Numero di iterazioni
    # pos = nx.spring_layout(G0, seed=1)
    # nx.draw_networkx_labels(G0, pos, font_size=20, font_family='sans-serif')
    # nx.draw(G0, pos)
    # plt.show()

    # Computation and results cleaning
    args = ["./hybrid-ia", "-i", f"./G/G{i}.gml", "-t", "20"]
    res = subprocess.run(args, capture_output=True)

    # Saving Raw Output
    with open(f"./R/R{i}.txt", "w") as text_file:
        print(f"{res.stdout.decode('UTF-8')}", file=text_file)

    arrRes = res.stdout.decode('UTF-8').split("\t")
    print(f"{arrRes[:-2]}")

    rawR0 = arrRes[11]
    R0 = dict((int(val[0]), int(val[1])-1) for val in [pair.split(":")
                                                       for pair in rawR0.split(",")])
    # print(R0)
    # print(G0.edges())
    G1 = merge_nodes(G0, R0)
    nx.write_gml(G1, f"./G/G{i+1}.gml")
    G0 = G1

# %%
# Create traceback dataframe
base_g = 0
last_g = lvl
with open(f"./R/R{base_g}.txt", "r") as txt:
    arrRes = txt.read().split("\t")
    print(f"ADD {txt.name} -> {arrRes[:-5]}")
    rawR0 = arrRes[11]
    r0 = [pair.split(":") for pair in rawR0.split(",")]
    R0n = [int(val[0]) for val in r0]
    R0c = [int(val[1])-1 for val in r0]

    df = pd.DataFrame(R0c, index=R0n, columns=["R0"])

for i in range(base_g+1, last_g):
    with open(f"./R/R{i}.txt", "r") as txt:
        arrRes = txt.read().split("\t")
        print(f"ADD {txt.name} -> {arrRes[:-5]}")

        rawR0 = arrRes[11]
        r0 = [pair.split(":") for pair in rawR0.split(",")]
        R0n = [int(val[0]) for val in r0]
        R0c = [int(val[1])-1 for val in r0]

        df1 = pd.DataFrame(R0c, index=R0n, columns=[f"R{i}"])

        df = df.join(df1, on=f"R{i-1}", lsuffix='_caller', rsuffix='_other')
df = df.sort_index()
print(df.head())
df.to_csv("./trace.csv")

# %%
# # SIMPLE GRAPH PLOT (DOESN'T SHOW SELF-LOOPS)
# for g in range(20):  # Change here to choose the Gs to show
#     G10 = nx.read_gml(f'./G/G{g}.gml', label='id')
#     plt.figure(figsize=(20, 8))
#     plt.subplot(121)
#     pos = nx.spring_layout(G10, seed=1)
#     nx.draw_networkx_labels(G10, pos, font_size=20, font_family='sans-serif')
#     nx.draw(G10, pos)

#     plt.subplot(122)
#     pos = nx.spring_layout(G10, seed=1)
#     nx.draw_networkx_nodes(G10, pos)
#     nx.draw_networkx_labels(G10, pos, font_size=20, font_family='sans-serif')
#     nx.draw_networkx_edges(G10, pos)
#     nx.draw_networkx_edge_labels(
#         G10, pos, font_size=20, font_family='sans-serif')
#     plt.show()

#     # weight check
#     s = 0
#     for (u, v, w) in G10.edges().data('weight', default=1):
#         s += w
#     print(s)

# %%
# TEST AVVIO COMANDO
# args = ["./hybrid-ia", "-i", "./test.gml", "-t", "2"]
# args1 = ["ls", "-l"]
# res = subprocess.run(args, capture_output=True)
# print(res.stdout.decode('UTF-8'))
# print(res.stdout.decode('UTF-8').split("\t")[11])
# rawRes = res.stdout.decode('UTF-8').split("\t")[11]


# %%
