"""
This script creates the data for the
percolation probability as a function
of site occupation fraction p, and for
various system sizes N with replicas.

The output is used for one of the figures
in the streamlit app
"""

from dask.distributed import Client
import numpy as np
from collections import defaultdict
import json

import sys
sys.path.append('..')  # makes next import work
from percolation import PercolationSimulation  # noqa


def runTrials(args):
    L = args[0]
    p = args[1]
    num_samples = args[2]
    print(f"Working on L={L}, p={p}")

    sim = PercolationSimulation(L, L, p)

    trials = []
    for _ in range(num_samples):
        sim.trial()
        trials.append(int(sim.max_cluster_size / (L*L) > 0.5))
    return trials


if __name__ == '__main__':

    c = Client()  # Creates local dask worker pool

    # We initialize one simulation object
    # each job, so we also want to do more
    # trials in each job to amoritize cost

    values_to_map = []
    trials_per_job = 50
    jobs_per_statepoint = 20
    Lpts = [10, 15, 20, 25, 30, 35, 40]
    ppts = np.arange(0.50, 0.65, 0.01)

    for L in Lpts:
        for p in ppts:
            values_to_map.append(
                (L, p, trials_per_job)
                )
    values_to_map *= jobs_per_statepoint

    maps = c.map(runTrials, values_to_map, pure=False)

    data = c.gather(maps)

    # Aggregate replicas of same params
    d = defaultdict(list)
    for state, values in zip(values_to_map, data):
        # d[(L,p)]) to list of sim outcomes
        d[(state[0], state[1])] += values

    for L in Lpts:
        x = [k for k in d.keys() if k[0] == L]
        ld = defaultdict(list)
        for Lp in x:
            # print(f"{Lp}: {np.mean(d[Lp])}")
            ld[Lp[1]] = d[Lp]
            ld[Lp[1]] = np.mean(d[Lp])

        with open(f"{L}.json", 'w') as f:
            f.write(json.dumps(ld))
