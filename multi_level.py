# %%
# from IPython.display import display
import pandas as pd
import shutil

# import os
import subprocess
import networkx as nx

# import matplotlib.pyplot as plt
from gml import write_gml
import random
import math
from timeit import default_timer as timer
import json
from pathlib import Path
from collections import defaultdict

import pquality as pq


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
    for (u, v, w) in G.edges().data("weight", default=1):
        # Insert edges between communities, no issue if repeated
        G1.add_edge(R[u], R[v])
        # Compute weight
        G1.edges[R[u], R[v]]["weight"] = G1.edges[R[u], R[v]].get("weight", 0) + w
    return G1


def add_trace(
    i: int, R: dict, trace: pd.DataFrame, after_expl_R=None, prev: int = None
):
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
    pandas.DataFrame
        The new DataFrame
    """
    prev = i - 1 if prev == None else prev
    R0_df = pd.DataFrame(index=R.keys(), data=R.values(), columns=[f"R{i}"])
    # print("\n", new_df)

    if after_expl_R:  # Add result after explosion, normal join causes NaN
        after_expl_df = pd.DataFrame(
            index=after_expl_R.keys(), data=after_expl_R.values(), columns=[f"R"]
        )

        joined_df = after_expl_df.join(
            R0_df, on=f"R"
        )  # Use topology after explosion to find comm for each original node
        trace[f"R{i}"] = joined_df[f"R{i}"]
        return trace.astype("int64")
    elif trace.empty:
        return R0_df.astype("int64")
    else:
        joined_df = trace.join(
            R0_df, on=f"R{prev}"
        )  # Use topology of previous result to find comm for each original node
        return joined_df.astype("int64")


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


def int_R_ext_degree(node, community, G, R):
    """
    Calculate internal/external degree of a node given the community structure
    """
    # print("\n", node, community, end=" ")
    in_deg, ex_deg = 0, 0
    for (u, v, w) in G.edges(node, data="weight", default=1):
        # print(u, v, w)
        if R[v] == community:
            in_deg += w
        else:
            ex_deg += w
    # print(in_deg/ex_deg if ex_deg != 0 else 999)
    return in_deg / ex_deg if ex_deg != 0 else 999


def ratio_internal_degree(node, community, G, R):
    """
    Calculate internal/total degree of a node given the community structure
    Return: float between [0,1]
    """
    # print("\n", node, community, end=" ")
    in_deg, deg = 0, 0
    for (u, v, w) in G.edges(node, data="weight", default=1):
        # print(u, v, w)
        deg += w
        if R[v] == community:
            in_deg += w
    return in_deg / deg


def explode_community_beta(
    G0, trace, explode_id: list, i: int, min_ratio: float = 1, verbose=False
):
    """
    Returns a graph where each community of "G0" is reduced to a single node,
    except the selected communities that will have all nodes with int/ext

    Parameters
    ----------
    G0 : nx.Graph
        The original graph with the original nodes
    trace : pd.DataFrame
        DataFrame with the traceback from any level to G0.
    explode_id: int
        id for the community to explode, if [], will explode all
    i: int
        number of the level to use for explosion
    min_ratio: float
        If internal/total degree is > min_ratio
    verbose: bool
        Verbose

    Returns
    -------
    nx.Graph
        The processed graph
    """
    R_base = trace.to_dict()[f"R{i}"]
    fixed_R0 = {}
    i_count, e_count = 0, 0
    # Aux variable to speed up
    R_base_max = max(R_base.values())
    R_base_len = len(R_base.values())
    # fixed_R0 = {k: (k if (v in explode_id) and int_R_ext_degree(k, v, G0, R_base) <1   else v) for k,
    #             v in R_base.items()}
    for k, v in R_base.items():
        if (
            not (explode_id) or v in explode_id
        ):  # Explode if explode id is [], oe if v is in
            if min_ratio < 0 or (
                min_ratio <= 1 and ratio_internal_degree(k, v, G0, R_base) > min_ratio
            ):
                # keep in comm
                fixed_R0[k] = v
                # + (R_base_max - R_base_len) + 1
                i_count += 1
            else:
                fixed_R0[k] = k  # expl
                e_count += 1
        else:
            fixed_R0[k] = v  # keep in comm
            i_count += 1
    if verbose:
        print(f"({i_count}) ){e_count}(", end=" ")
    return merge_nodes(G0, fixed_R0), fixed_R0


def fix_disconnected_comms(G: nx.Graph, trace: pd.DataFrame, i: int, offset):
    """
    Divides communities in theirs fully connected components, id of new communities
    are different, from original ids.

    Parameters
    ----------
    G0 : nx.Graph
        The original graph with the original nodes
    trace : pd.DataFrame
        DataFrame with the traceback dataframe.
    i: int
        number of the current level
    offset: int
        Offset used when indexing the communities

    Returns
    -------
    DataFrame:
        The fixed dataframe
    float:
        New modularity after fix
    """
    partition = trace.iloc[:, i].to_dict()
    my_inverted_dict = defaultdict(list)
    {my_inverted_dict[v].append(k) for k, v in partition.items()}
    comm_list = list(my_inverted_dict.values())

    comm_idx = 0
    fixed_res = {}

    for nodes_in_comm in comm_list:
        comm_G = G.subgraph(nodes_in_comm)
        # if nx.is_connected(comm_G):
        #     fixed_res.update(dict(zip(nodes_in_comm, [offset + comm_idx] * len(nodes_in_comm))))
        #     comm_idx += 1
        #     continue
        for node_set in nx.connected_components(comm_G):
            fixed_res.update(dict(zip(node_set, [offset + comm_idx] * len(node_set))))
            comm_idx += 1

    res_trace = trace.drop([f"R{i}"], axis=1)
    res_trace[f"R{i}"] = pd.Series(fixed_res)

    return res_trace, float(pq.PartitionQuality.community_modularity(fixed_res, G))


def get_hybrid_it(it_type, original_n_nodes, curr_n_nodes):
    """
    Parse the string or int
    Return "-t" arg for execution
    """
    if isinstance(it_type, int) or it_type.isdigit():
        return ["-t", f"{it_type}"]
    else:
        it_type = it_type.split("-")  # Get all args
        if it_type[0] == "linear":
            return ["-t", f"{curr_n_nodes}"]
        elif it_type[0] == "ratio":  # arg1= min, arg2= max
            n_it = int((1 - (curr_n_nodes / original_n_nodes)) * int(it_type[2]))
            return [
                "-t",
                f"{max([n_it, int(it_type[1])])}",
            ]
        else:
            raise NameError("Unknown type of hybrid iteration")


def hybrid_multi_level_beta(
    graph,
    to_run: str = "./hybrid-ia",
    smart_merge: bool = False,
    merge_min_ratio: float = 0.5,
    mod_goal: float = None,
    max_time: int = None,
    max_levels=9999999,
    hybrid_it: str = "",
    explosion: int = 1,
    try_close: int = 1,
    expl_min_ratio: float = 0.5,
    add_args=[],
    verbose: bool = False,
    path=".",
    seed=None,
    save_intermediate=False,
):
    """
    Implements multi-level to the immunologic approach,
    WARNING folders named "G" and "R" inside "path" will be EMPTIED if existing!

    Parameters
    ----------
    graph: str
        Path to gml file the original graph where to find the communities
    to_run: str
        Path to binaries of the base algorithm
    smart_merge: bool
        If True will not merge the entire community but only a subset of node based on 
        "merge_min_ratio" value
    merge_min_ratio: float
        Ratio of internal links of a node, nodes with ratio > "merge_min_ratio" will 
        be fused with Smart Merge  
    mod_goal: float
        Value of Modularity to reach
    max_time: int
        Max time of execution in seconds
    max_levels: int
        How many times the communities will be computed then reduced,
        (in other words, the number of iterations)
    hybrid_it: string
        Can be a string containing the number of iteration or "linear","i_linear" method
    explosion: int
        If >0 the explosion optimization will explode n="explosion" community
    try_close: int
        If "try_close" is higher than 0 in case of modularity stagnation the function will try to explode
        each community, from the best result, "try_close" times then stops if no new max modularity is found  
    expl_min_ratio: float
        Ratio of internal links of a node, nodes with ratio > "merge_min_ratio" will 
        be kept fused when a community is exploded, if > 1 all node will be exploded 
    add_args: list
        A list of additional parameter for the executable
    verbose: bool
        If True, verbose
    path: string
        The path where the results will be saved
    seed: int
        The seed used for the multi-level, remember to set also the seed for the binaries using add_args
    save_intermediate: bool
        If True save all intermediate step and grap configurations, WARNING Big sizes expected 
    """
    saved_args = locals()
    t_start = timer()
    prepare_folders(path)
    random.seed(seed)
    log = {}
    log["args"] = saved_args
    # Create G0 from original graph for consistency
    G0 = nx.read_gml(graph, label="id")
    original_G0 = G0
    original_G0_n_nodes = G0.number_of_nodes()
    # G0 = nx.convert_node_labels_to_integers(G0)  # Make sure first label is 0
    write_gml(G0, f"{path}/G/G0.gml")

    trace = pd.DataFrame()  # Empty dataframe to save the traceback

    R_i = None  # Needed for exploding the best result instead of the last
    after_expl_R = {}
    fit_hist, time_hist = [], []  # History of modularities and times
    best_1R = -1
    explode_pool = []
    h_it = []

    # Needed to give communities non-conflicting ids with original nodes
    offset = max(G0.nodes()) + 1
    if verbose:
        print(
            "Graph".rjust(5),
            "Nodes".rjust(5),
            "Edges".rjust(5),
            "Comm".ljust(5),
            "Fit".ljust(8),
            "Iter".ljust(4),
            "H.Time".rjust(5),
            "C.Comm".rjust(5),
        )
    for i in range(max_levels):  # Each loop: G"i" graph -compute-> create G"i+1"
        t_loop = timer()
        ## Reset varibles

        # Preparing args, computing hybrid-ia and gettin results
        h_it = get_hybrid_it(hybrid_it, original_G0_n_nodes, G0.number_of_nodes())
        args = (
            [
                to_run,
                "-i",
                f"{path}/G/G{i if save_intermediate or i == 0 else 'f'}.gml",
            ]
            + add_args
            + h_it
        )
        # res = subprocess.run(args, capture_output=True) #3.8 version
        res = subprocess.run(args, stdout=subprocess.PIPE)  # 3.6 version

        # Saving Raw Output in R file
        arrRes = res.stdout.decode("UTF-8").replace("\n", "")
        with open(f"{path}/R.txt", "a") as text_file:
            print(f"{arrRes}", file=text_file)

        # Result to array
        arrRes = arrRes.split("\t")

        # Saving resulting communities & update support variables
        R0 = dict(
            (int(val[0]), int(val[1]) + offset)
            for val in [pair.split(":") for pair in arrRes[11].split(",")]
        )
        # Adding res to trace
        trace = add_trace(
            i, R0, trace, after_expl_R, prev=R_i
        )  # Updating traceback dataframe
        # Reset used values
        R_i = None
        after_expl_R = {}

        # Fix Disconnected Comms
        trace, fixed_mod = fix_disconnected_comms(original_G0, trace, i, offset)

        # Print Results
        if verbose:
            print(
                f"{'G'+str(i):5}",
                f"{arrRes[1]:5}",
                f"{arrRes[2]:5}",
                f"{arrRes[-3]:5}",
                f"{float(arrRes[9]):6.5f}",
                f"{h_it[1]:>5}",
                f"{float(arrRes[-1]):>6.2f}",
                f"{len(trace[f'R{i}'].unique()):6}",
                f"{fixed_mod:6.5f}",
                end=" ",
                sep=" ",
            )

        # Update modularity history
        # fit_hist = fit_hist + [float(arrRes[9])]
        fit_hist = fit_hist + [fixed_mod]

        # Find latest best level index
        best_R = -1 - ((fit_hist[::-1].index(max(fit_hist))) - len(fit_hist))

        # Creating exploding pool if new Best
        if best_1R != fit_hist.index(max(fit_hist)):
            best_1R = fit_hist.index(max(fit_hist))
            explode_pool = list(trace[f"R{best_1R}"].unique()) * try_close

        # Check if stagnating
        # if check_close_condition(fit_hist):
        if len(fit_hist) > 1 and (fit_hist[-1] == fit_hist[-2]):
            # Check if explosion is needed, exit if pool is empty
            if explosion:
                if not explode_pool:  # If Explode Pool is empty
                    time_hist += [timer() - t_start]  # Save Time_hist
                    print(f"CLOSING, can't find better result")
                    break
                R_i = best_1R
                # exploding_comm = random.randint(
                #     offset+1, trace[(f"R{R_i}")].max())
                exploding_comm = random.sample(
                    list(set(explode_pool)),
                    k=explosion
                    if len(list(set(explode_pool))) >= explosion
                    else len(list(set(explode_pool))),
                )
                if verbose:
                    print(f"R{R_i} -> G{i+1} expl{exploding_comm} ", end="")
                # display(trace)
                if try_close:
                    for c in exploding_comm:
                        explode_pool.remove(c)
                G1, after_expl_R = explode_community_beta(
                    original_G0,
                    trace,
                    exploding_comm,
                    R_i,
                    min_ratio=expl_min_ratio,
                    verbose=verbose,
                )
            else:  # Close for modularity stagnation
                time_hist += [timer() - t_start]  # Save Time_hist
                print(f"CLOSING, can't find better result")
                break
        else:
            G1, after_expl_R = explode_community_beta(
                original_G0,
                trace,
                explode_id=[],
                i=i,
                min_ratio=merge_min_ratio if smart_merge else -1,
                verbose=verbose,
            )
        # else: #Normal Merge
        #     G1 = merge_nodes(G0, )
        #     if verbose:
        #         print(f"R{i} -> G{i+1}", end=" ")

        # Create next level Graph
        if save_intermediate:
            write_gml(G1, f"{path}/G/G{i+1}.gml")
        else:
            write_gml(G1, f"{path}/G/Gf.gml")
        G0 = G1

        # Print Overhead and overall time
        if verbose:
            print(
                f"{(timer()-float(arrRes[-1])-t_loop): 5.2f} {timer()-t_start : 5.2f}"
            )  # \n

        # Save Time_hist
        time_hist += [timer() - t_start]

        # Check exit conditions
        if mod_goal is not None and mod_goal <= fit_hist[-1]:
            print(f"CLOSING, Found modularity goal!")
            break
        if max_time is not None and max_time <= time_hist[-1]:
            print(f"CLOSING, Max time reached!")
            break

    # Closing procedure
    t_end = timer()
    print(f"Computation took {t_end - t_start}s")
    print(
        f"Best modularity {max(fit_hist)} first R{fit_hist.index(max(fit_hist))}, last R{best_R}"
    )

    print(f"Saving results... ", end="")
    if save_intermediate:
        trace.sort_index().to_csv(f"{path}/trace.csv")
    else:
        trace[f"R{best_R}"].sort_index().to_csv(f"{path}/trace.csv")

    log.update(
        {
            "exe_time": t_end - t_start,
            "best_fit": max(fit_hist),
            "best_fit_fi": fit_hist.index(max(fit_hist)),
            "best_fit_li": best_R,
            "fit_hist": fit_hist,
            "time_hist": time_hist,
        }
    )
    with open(f"{path}/res.json", "w") as f:
        json.dump(log, f)
        print(f"Done!")

    return log


# %%
