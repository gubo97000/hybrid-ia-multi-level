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
import json
from pathlib import Path


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
    fixed_R0 = {k: (v if not explode_id.count(v) else k) for k,
                v in trace.to_dict()[f'R{i}'].items()}
    return merge_nodes(G0, fixed_R0)


def add_trace(i: int, R: dict, trace: pd.DataFrame, prev: int = None):
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
    prev: int
        If Ri is computed from a graph created with an R different from Ri-1,
        insert the correct index (needed when exploding community with bomb_max)

    Returns
    -------
    nx.Graph
        The processed graph
    """
    prev = i-1 if prev == None else prev
    Rn, Rc = R.keys(), R.values()
    df = pd.DataFrame(Rc, index=Rn, columns=[f"R{i}"])
    # print("\n", df)
    if(trace.empty):
        return df
    else:
        df1 = trace.join(df, on=f"R{prev}")
        # print("\n", df1)
        for key, val in df1[f"R{i}"].iteritems():
            if math.isnan(val):
                # print(df1[f"R{i}"][key],"",end="")
                # print(key,val)
                # print(df1.at[key, f"R{i}"], df[f"R{i}"][key])
                # df1.at[key, f"R{i}"] = df[f"R{i}"][key]
                df1[f"R{i}"][key] = df[f"R{i}"][key]
                # print(df1[f"R{i}"][key])
                # print(df[f"R{i}"][key])
        return df1.astype('int64')

    # return df if trace.empty else trace.join(df, on=f"R{i-1}")


def prepare_folders(path="."):
    """
    Will remove, if already exist, then create folders "R" and "G" in "path"

    Parameters
    ----------
    path : string
        Path where to remove and create "R" and "G" folders
    """
    # DELETE AND CREATES ALL RESULTS DIRECTORIES
    shutil.rmtree(f"{path}/R", ignore_errors=True)
    shutil.rmtree(f"{path}/G", ignore_errors=True)
    try:
        Path(f"{path}/R").mkdir(parents=True)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    try:
        Path(f"{path}/G").mkdir(parents=True)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def hybrid_multi_level(graph, mod_goal=None, levels=20, explosion: int = 1, bomb_max=True, try_close=0, add_args=[], path=".", seed=None):
    # TODO: Bomb_max must be eliminated, can't be False anymore without uncertainties
    """
    Implements the multi-level to the hybrid-ia approach,
    WARNING folders named "G" and "R" inside "path" will be EMPTIED if existing!

    Parameters
    ----------
    graph: path to gml file
        The original graph where to find the communities
    levels: int
        How many times the communities will be computed then reduced,
        (in other words, the number of iterations)
    explosion: bool
        If True the function will try to maximize the result with community explosion
    bomb_max: bool
        If True further improvement are applied to community explosion
        (by exploding the communities of the best result instead of the latest)
    try_close: int
        If 0 the function will stop at max number of iteration defined in "levels",
        If "try_close">0 in case of modularity stagnation the function will try to explode
        each community "try_close" times then stops if no new max modularity is found  
    add_args: list
        A list of parameter for hybrid-ia
    path: string
        The path where the results will be saved
    """
    start = timer()
    prepare_folders(path)
    random.seed(seed)
    # Create G0 from original graph for consistency
    G0 = nx.read_gml(graph, label='id')
    # G0 = nx.convert_node_labels_to_integers(G0)  # Make sure first label is 0
    write_gml(G0, f"{path}/G/G0.gml")

    trace = pd.DataFrame()  # Empty dataframe to save the traceback
    R_i = None  # Needed for exploding the best result instead of the last
    fit_hist = []  # History of modularities
    best_1R = -1
    explode_pool = []

    # Needed to give communities non-conflicting ids with original nodes
    n_nodes = max(G0.nodes())

    print("Graph".rjust(5), "Nodes".rjust(5), "Edges".rjust(5),
          "Comm".ljust(5), "Fit".ljust(8), "Ex Time".rjust(5))
    for i in range(levels):  # Each loop: G"i" graph -compute-> create G"i+1"

        # Computation and gettin results
        # add_args=["-t", "2", "-p", "1000"]
        args = ["./hybrid-ia", "-i", f"{path}/G/G{i}.gml"] + add_args
        # res = subprocess.run(args, capture_output=True) #3.8 version
        res = subprocess.run(args, stdout=subprocess.PIPE)  # 3.6 version

        # Saving Raw Output in R folder
        with open(f"{path}/R/R{i}.txt", "w") as text_file:
            print(f"{res.stdout.decode('UTF-8')}", file=text_file)

        # Results cleaning
        arrRes = res.stdout.decode('UTF-8').replace("\n", "").split("\t")
        print(
            f"{arrRes[0]:5} {arrRes[1]:5} {arrRes[2]:5} {arrRes[-3]:5} {float(arrRes[9]):6f} {float(arrRes[-1]):3f} ", end="")

        # Saving resulting communities & update support variables
        rawR0 = arrRes[11]
        R0 = dict((int(val[0]), int(val[1])+n_nodes) for val in [pair.split(":")
                                                                 for pair in rawR0.split(",")])
        trace = add_trace(i, R0, trace, R_i)  # Updating traceback dataframe
        R_i = None  # Clean after been used
        fit_hist = fit_hist + [float(arrRes[9])]  # Update modularity history
        best_R = -1-((fit_hist[::-1].index(max(fit_hist))
                      )-len(fit_hist))  # Latest best index

        # Creating exploding pool or exit if empty
        if not bomb_max:
            explode_pool = list(
                trace[f"R{i}"].unique())*(try_close if try_close else 1)
        elif best_1R != fit_hist.index(max(fit_hist)):
            best_1R = fit_hist.index(max(fit_hist))
            explode_pool = list(
                trace[f"R{best_1R}"].unique())*(try_close if try_close else 1)
        elif not explode_pool:
            print(f"CLOSING, can't find better result")
            break

        # Check if explosion is needed
        if(explosion and len(fit_hist) > 1 and (fit_hist[-1] == fit_hist[-2])):
            R_i = best_1R if bomb_max else i
            # exploding_comm = random.randint(
            #     n_nodes+1, trace[(f"R{R_i}")].max())
            exploding_comm = random.sample(list(set(explode_pool)), k=explosion if len(
                list(set(explode_pool))) >= explosion else len(list(set(explode_pool))))
            print(f"R{R_i} -> G{i+1} with exploded comm {exploding_comm} ", end="")
            if(try_close):
                for c in exploding_comm:
                    explode_pool.remove(c)
            G1 = explode_community(nx.read_gml(
                f'{path}/G/G0.gml', label='id'), trace, exploding_comm, R_i)
        else:
            G1 = merge_nodes(G0, R0)
            print(f"R{i} -> G{i+1}", end=" ")

        write_gml(G1, f"{path}/G/G{i+1}.gml")
        G0 = G1

        print(f"{timer()-start : 5.2f}")  # \n

        if mod_goal != None and mod_goal <= fit_hist[-1]:
            print(f"CLOSING, Found modularity goal!")
            break

    end = timer()
    print(f"Computation took {end - start}s")
    print(
        f"Best modularity {max(fit_hist)} first R{fit_hist.index(max(fit_hist))}, last R{best_R}")

    print(f"Saving results... ", end="")
    trace.sort_index().to_csv(f"{path}/trace.csv")
    res = {
        "graph": graph,
        "mod_goal": mod_goal,
        "levels": levels,
        "explosion": explosion,
        "bomb_max": bomb_max,
        "try_close": try_close,
        "seed": seed,
        "add_args": add_args,
        "exe_time": end - start,
        "best_fit": max(fit_hist),
        "best_fit_fi": fit_hist.index(max(fit_hist)),
        "best_fit_li": best_R,
        "fit_hist": fit_hist
    }
    with open(f"{path}/res.json", "w") as f:
        json.dump(res, f)
        print(f"Done!")

    return res

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
