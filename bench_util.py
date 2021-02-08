# %%
import datetime
import json
from statistics import mean
import os
from itertools import zip_longest
import numpy as np
import pandas as pd

# from tqdm import tqdm
import tqdm as tq

# import tqdm.notebook as tq

# %%
def multiAverage(rootdir):
    """
    Returns avg and log, log contains all processed data divided by run, each object contains: "h_best_fit", "h_time", "res".
    avg contains the average of processed results, contains: "h_best_fit", "h_time", "fit_hist"

    Parameters
    ----------
    rootdir : string
        directory with subfolders of results

    Returns
    -------
    avg: {"h_best_fit", "h_time", "fit_hist"}
    log: [{"h_best_fit", "h_time", "res"}, ...]
    """
    log = {}
    max_time = 0
    max_lev = 0
    min_time = np.inf
    for subdir, dirs, files in os.walk(rootdir):
        break
    # dirs=[float(i) for i in dirs]
    # dirs = sorted(dirs, key=lambda x: int("".join([i for i in x if i.isdigit()])))
    for i in tq.tqdm(dirs, desc=rootdir):
        with open(f"./{rootdir}/{i}/res.json") as j:
            r = json.load(j)
        s = []
        best = []

        # Search for cache
        if os.path.exists(f"./{rootdir}/{i}/cache.json"):
            with open(f"./{rootdir}/{i}/cache.json") as j:
                cache = json.load(j)
                if "time_hist" in r:
                    s = r["time_hist"]
                else:
                    s = cache["cumulative_R_Time"]
                best = cache["best_fit_hist"]
                # s = cache["cumulative_R_Time"] + [r["exe_time"]]
                # best = cache["best_fit_hist"] + [r["best_fit"]]
                # r["fit_hist"] += [r["best_fit"]]
        else:
            for ii in range(len(r["fit_hist"])):
                with open(f"./{rootdir}/{i}/R/R{ii}.txt") as t:
                    arr = t.read().replace("\n", "").split("\t")
                    s += [(0 if not s else s[-1]) + float(arr[-1])]
                    if not best:
                        best += [float(arr[9])]
                    else:
                        if float(arr[9]) > best[-1]:
                            best += [float(arr[9])]
                        else:
                            best += [best[-1]]
            with open(f"./{rootdir}/{i}/cache.json", "w") as f:
                json.dump({"cumulative_R_Time": s, "best_fit_hist": best}, f)
        
        if "time_hist" in r:
            s = r["time_hist"]
        max_time = s[-1] if s[-1] > max_time else max_time
        min_time = s[0] if s[0] < min_time else min_time
        max_lev = len(r["fit_hist"]) if len(r["fit_hist"]) > max_lev else max_lev
        # print(i, datetime.timedelta(seconds=s[-1]), datetime.timedelta(seconds=r["exe_time"]), r["best_fit"])
        log[i] = {"h_best_fit": best, "h_time": s, "res": r}
    
    # AVG computation time correct
    a_best = False
    a_fit = False
    a_best_lvl = False
    a_time = np.linspace(min_time, max_time, max_lev)
    a_lvl = list(range(max_lev))
    for l in log.values():
        a_best_lvl_tmp = np.array(
            np.interp(a_lvl, list(range(len(l["h_best_fit"]))), l["h_best_fit"])
        )[:, np.newaxis]
        a_best_lvl = (
            np.concatenate((a_best_lvl, a_best_lvl_tmp), axis=1)
            if type(a_best_lvl) != bool
            else a_best_lvl_tmp
        )
        a_best_tmp = np.array(np.interp(a_time, l["h_time"], l["h_best_fit"]))[
            :, np.newaxis
        ]
        a_best = (
            np.concatenate((a_best, a_best_tmp), axis=1)
            if type(a_best) != bool
            else a_best_tmp
        )

        a_fit_tmp = np.array(np.interp(a_time, l["h_time"], l["res"]["fit_hist"]))[
            :, np.newaxis
        ]
        a_fit = (
            np.concatenate((a_fit, a_fit_tmp), axis=1)
            if type(a_fit) != bool
            else a_fit_tmp
        )

    # print(a_best)
    avg = {
        "h_best_fit": list(map(lambda x: mean(x), a_best)),
        "h_best_lvl_fit": list(map(lambda x: mean(x), a_best_lvl)),
        "h_time": a_time,
        "fit_hist": list(map(lambda x: mean(x), a_fit)),
    }
    return avg, log

    # avg = {
    #     "h_best_fit": list(filter(lambda x: x != False, list(map(lambda x: mean(x) if x else False, a_best)))),
    #     "h_time": list(filter(lambda x: x != False, list(map(lambda x: mean(x) if x else False, a_time)))),
    #     "fit_hist": list(filter(lambda x: x != False, list(map(lambda x: mean(x) if x else False, a_fit_hist))))
    # }


# %%
def hyAverage(rootdir):
    """
    Returns avg and log, log contains all processed results contains: "h_best_fit", "h_time", "res".
    avg contains the average of processed results, contains: "h_best_fit", "h_time", "fit_hist"

    Parameters
    ----------
    rootdir : string
        directory with subfolders of results

    Returns
    -------
    avg: {"h_best_fit", "h_time", "fit_hist"}
    log: [{"h_best_fit", "h_time", "res"}]
    """
    log = {}
    max_time = 0
    max_lev = 0
    min_time = np.inf
    for subdir, dirs, files in os.walk(rootdir):
        break
    # dirs=[float(i) for i in dirs]
    # dirs = sorted(dirs, key=lambda x: int("".join([i for i in x if i.isdigit()])))
    for i in tq.tqdm(dirs, desc=rootdir):

        with open(f"{rootdir}/{i}/T_M.txt") as j:
            r = json.load(j)
            s = [float(x) for x in r["time_hist"]]
            best = [float(x) for x in r["fit_hist"]]

        max_time = s[-1] if s[-1] > max_time else max_time
        min_time = s[0] if s[0] < min_time else min_time
        max_lev = len(r["fit_hist"]) if len(r["fit_hist"]) > max_lev else max_lev
        # print(i, datetime.timedelta(seconds=s[-1]), datetime.timedelta(seconds=r["exe_time"]), r["best_fit"])
        log[i] = {"fit_hist": best, "time_hist": s}
    # AVG computation time correct
    a_best = False
    a_fit = False
    a_best_lvl = False
    a_time = np.linspace(min_time, max_time, max_lev)
    a_lvl = list(range(max_lev))
    for l in log.values():
        a_fit_tmp = np.array(np.interp(a_time, l["time_hist"], l["fit_hist"]))[
            :, np.newaxis
        ]
        a_fit = (
            np.concatenate((a_fit, a_fit_tmp), axis=1)
            if type(a_fit) != bool
            else a_fit_tmp
        )

    # print(a_best)
    avg = {"time_hist": a_time, "fit_hist": list(map(lambda x: mean(x), a_fit))}
    return avg, log

    # avg = {
    #     "h_best_fit": list(filter(lambda x: x != False, list(map(lambda x: mean(x) if x else False, a_best)))),
    #     "h_time": list(filter(lambda x: x != False, list(map(lambda x: mean(x) if x else False, a_time)))),
    #     "fit_hist": list(filter(lambda x: x != False, list(map(lambda x: mean(x) if x else False, a_fit_hist))))
    # }


# %%
def rel_timeVgraph(rootdirs, max_n=None):
    """
    Walks inside the rootdir or a list od dirs and dumps all R.txt results in their subfolders
    Time, #nodes, #links of each R
    Parameters
    ----------
    rootdirs : string or list
        directory with subfolders of results
        directories with subfolders of results

    Returns
    -------
    time: []

    #node: []

    #link: []
    """
    rootdirs = rootdirs if type(rootdirs) == list else [rootdirs]
    time = []
    n = []
    l = []
    for rootdir in rootdirs:
        for subdir, dirs, files in os.walk(rootdir):
            break
        # dirs=[float(i) for i in dirs]
        # dirs = sorted(dirs, key=lambda x: int("".join([i for i in x if i.isdigit()])))
        max_n = max_n if max_n else len(dirs)
        for i in dirs[:max_n]:
            with open(f"./{rootdir}/{i}/res.json") as j:
                r = json.load(j)

            for ii in tq.tqdm(range(len(r["fit_hist"])), desc=f"{i}"):
                with open(f"./{rootdir}/{i}/R/R{ii}.txt") as t:
                    arr = t.read().replace("\n", "").split("\t")
                    l += [int(arr[2])]
                    n += [int(arr[1])]
                    time += [float(arr[-1])]
            # print(i, len(r["fit_hist"]))
    return time, n, l


# %%
def batch_stats(rootdirs):
    """
    Execution time, fit, iteration for each execution in directory, and cumulative stats at the end

    Parameters
    ----------
    rootdirs : string or list
        directory with subfolders of results
        directories with subfolders of results

    Returns
    -------
    Complete df with all sta for each run, last 4 row are the cumulative stats
    use [-4:] to select only them

    """
    rootdirs = rootdirs if type(rootdirs) == list else [rootdirs]
    time = []
    bf = []
    it = []
    names = []
    for rootdir in rootdirs:
        for _subdir, dirs, _files in os.walk(rootdir):
            break
        # dirs=[float(i) for i in dirs]
        # dirs = sorted(dirs, key=lambda x: int("".join([i for i in x if i.isdigit()])))
        for i in dirs:
            with open(f"./{rootdir}/{i}/res.json") as j:
                r = json.load(j)
            names += [i]
            time += [r["exe_time"]]
            bf += [r["best_fit"]]
            it += [len(r["fit_hist"])]

            # print(i, r["exe_time"],r["best_fit"], len(r["fit_hist"]))

    # print(mean(time),mean(bf),mean(it))
    df = pd.DataFrame(
        data={"Execution Time (s)": time, "Fit": bf, "Levels": it}, index=names
    )
    df.loc["max"] = df.max()
    df.loc["min"] = df.min()
    df.loc["mean"] = df.mean()
    df.loc["std"] = df.std()
    # print("\n",df.mean(),"\n",df.std(),"\n")
    # print(df,"\n")

    return df


# %%

