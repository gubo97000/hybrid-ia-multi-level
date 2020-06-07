# %%
import pandas as pd
import shutil
import os
import subprocess
import networkx as nx
import matplotlib.pyplot as plt
from gml import write_gml
import random
import math
from timeit import default_timer as timer


def merge_nodes(G, R):
    """
    Returns a graph where each community of the original graph is a single node,
    edges are modified accordingly to keep the same modularity.

    Parameters
    ----------
    G : nx.Graph
        The graph to reduce
    R : dict
        Computed communities for G

    Returns
    -------
    nx.Graph
        The processed graph
    """
    G1 = nx.Graph()
    # Creates nodes
    for n0 in R:
        G1.add_node(R[n0])

    # Cicle through edges in G
    for (u, v, w) in G.edges().data('weight', default=1):
        # Insert edges between communities, no issue if repeated
        G1.add_edge(R[u], R[v])
        # Compute weight
        G1.edges[R[u], R[v]]['weight'] = G1.edges[R[u],
                                                    R[v]].get('weight', 0) + w
    return G1


def explode_community(G0, trace, explode_id: int, i: int):
    """
    Returns a graph where each community of "G0" is reduced to a single node,
    except the selected community that will return to the orignial nodes.

    Parameters
    ----------
    G0 : nx.Graph
        The original graph with the original nodes
    trace : pd.DataFrame
        DataFrame with the traceback from any level to G0.
    explode_id: int
        id for the community to explode
    i: int
        number of the level to use for explosion

    Returns
    -------
    nx.Graph
        The processed graph
    """
    fixed_R0 = {k: v if v != explode_id else k for k,
                v in trace.to_dict()[f'R{i}'].items()}
    return merge_nodes(G0, fixed_R0)


def add_trace(i: int, R: dict, trace: pd.DataFrame):
    """
    Returns a dataframe to traceback from any level's communities the original nodes,
    giving an empty dataframe will return the dataframe with indexes the original nodes received from R0

    Parameters
    ----------
    i : int
        Number of the level
    R : dict
        The results from the computation ex. {"orignal_node":"community_id", ...}
    trace: pd.dataframe
        The dataframe where to join the newer R

    Returns
    -------
    nx.Graph
        The processed graph
    """
    Rn, Rc = R.keys(), R.values()
    df = pd.DataFrame(Rc, index=Rn, columns=[f"R{i}"])
    if(trace.empty):
        return df
    else:
        df1 = trace.join(df, on=f"R{i-1}")
        for key, val in df1[f"R{i}"].iteritems():
            if math.isnan(val):
                # print(key,val)
                # print(df1.at[key, f"R{i}"], df[f"R{i}"][key])
                # df1.at[key, f"R{i}"] = df[f"R{i}"][key]
                df1[f"R{i}"][key] = df[f"R{i}"][key]
                # print(df1[f"R{i}"][key])
        return df1.astype('int64')

    # return df if trace.empty else trace.join(df, on=f"R{i-1}")


def prepare_folders(path="."):
    """
    Will remove if they already exist then create folders "R" and "G" in "path"

    Parameters
    ----------
    path : string
        Path where to remove and create "R" and "G" folders
    """
    # DELETE AND CREATES ALL RESULTS DIRECTORIES
    shutil.rmtree(f"{path}/R", ignore_errors=True)
    shutil.rmtree(f"{path}/G", ignore_errors=True)
    try:
        os.mkdir(f"{path}/G")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    try:
        os.mkdir(f"{path}/R")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def hybrid_multi_level(graph, levels=20, explosion=True, add_args=[], path="."):
    start = timer()
    prepare_folders()

    # Create G0 from original graph for consistency
    G0 = nx.read_gml(graph, label='id')
    G0 = nx.convert_node_labels_to_integers(G0)  # Make sure first label is 0
    write_gml(G0, f"{path}/G/G0.gml")

    trace = pd.DataFrame()  # Empty dataframe to save the traceback

    n_nodes = len(G0.nodes())-1 # Needed to give communities not conflicting ids
    fit_hist=[]

    print("Graph".rjust(5), "Nodes".rjust(5), "Edges".rjust(5), "Comm".ljust(5), "Fit".ljust(8), "Ex Time".rjust(5))
    for i in range(levels):  # Each loop: G"i" graph -compute-> create G"i+1"

        # Computation and gettin results
        # add_args=["-t", "2", "-p", "1000"]
        args = ["./hybrid-ia", "-i", f"{path}/G/G{i}.gml"] + add_args
        res = subprocess.run(args, capture_output=True)

        # Saving Raw Output
        with open(f"{path}/R/R{i}.txt", "w") as text_file:
            print(f"{res.stdout.decode('UTF-8')}", file=text_file)

        # Results cleaning
        arrRes = res.stdout.decode('UTF-8').replace("\n","").split("\t")
        print(f"{arrRes[0]:5} {arrRes[1]:5} {arrRes[2]:5} {arrRes[-3]:5} {float(arrRes[9]):6f} {float(arrRes[-1]):3f}",end="")
        # print(f"{arrRes[:-2]}")

        rawR0 = arrRes[11]
        R0 = dict((int(val[0]), int(val[1])+n_nodes) for val in [pair.split(":")
                                                                 for pair in rawR0.split(",")])
        trace = add_trace(i, R0, trace)  # Updating traceback dataframe
        fit_hist = fit_hist + [float(arrRes[9])]
        
        #Check if explosion is needed
        if(explosion and len(fit_hist)>1 and (fit_hist[-1] == fit_hist[-2])):
            exploding_comm = random.randint(n_nodes+1, n_nodes+int(arrRes[10]))
            G1 = explode_community(nx.read_gml(
                f'{path}/G/G0.gml', label='id'), trace, exploding_comm, i)
            print(f" In G{i+1} exploded comm {exploding_comm}")
        else:
            G1 = merge_nodes(G0, R0)

        write_gml(G1, f"{path}/G/G{i+1}.gml")
        G0 = G1
        print("")
    print(max(fit_hist))
    print(fit_hist.index(max(fit_hist)))
    trace.to_csv(f"{path}/trace.csv")
    
    end = timer()
    print(end - start)

 # Time in seconds, e.g. 5.38091952400282
# %%
# Create traceback dataframe
# base_g = 0
# last_g = levels
# with open(f"./R/R{base_g}.txt", "r") as txt:
#     arrRes = txt.read().split("\t")
#     print(f"ADD {txt.name} -> {arrRes[:-5]}")
#     rawR0 = arrRes[11]
#     r0 = [pair.split(":") for pair in rawR0.split(",")]
#     R0n = [int(val[0]) for val in r0]
#     R0c = [int(val[1])+33 for val in r0]

#     df = pd.DataFrame(R0c, index=R0n, columns=["R0"])

# for i in range(base_g+1, last_g):
#     with open(f"./R/R{i}.txt", "r") as txt:
#         arrRes = txt.read().split("\t")
#         print(f"ADD {txt.name} -> {arrRes[:-5]}")

#         rawR0 = arrRes[11]
#         r0 = [pair.split(":") for pair in rawR0.split(",")]
#         R0n = [int(val[0]) for val in r0]
#         R0c = [int(val[1])+33 for val in r0]

#         df1 = pd.DataFrame(R0c, index=R0n, columns=[f"R{i}"])

#         df = df.join(df1, on=f"R{i-1}", lsuffix='_caller', rsuffix='_other')
# df = df.sort_index()
# print(df.head())
# df.to_csv("./trace.csv")


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

# %%
