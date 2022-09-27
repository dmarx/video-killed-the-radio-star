import time

import numpy as np
from scipy.spatial.distance import pdist, squareform
from toolz.itertoolz import partition_all
from python_tsp.exact import solve_tsp_dynamic_programming


def tsp_permute_frames(frames, verbose=False):
    """
    Permutes images using traveling salesman solver to find frame-to-frame 
    ordering that minimizes difference between subsequent frames, i.e.
    the ordering of the images that gives the smoothest animation.
    """
    frames_m = np.array([np.array(f).ravel() for f in frames])
    dmat = pdist(frames_m, metric='cosine')
    dmat = squareform(dmat)

    start = time.time()
    permutation, _ = solve_tsp_dynamic_programming(dmat)
    if verbose:
        print(f"elapsed: {time.time() - start}")

    frames_permuted = [frames[i] for i in permutation]
    return frames_permuted

def batched_tsp_permute_frames(frames, batch_size):
    """
    TSP solver is O(n^2). Instead of limiting how many variations a user can
    request for a particular image, we set an upperbound on how many images we
    send to the solver at any given time. TODO: Faster solver.
    """
    ordered = []
    for batch in partition_all(batch_size, frames):
        ordered.extend( tsp_permute_frames(batch) )
    return ordered
