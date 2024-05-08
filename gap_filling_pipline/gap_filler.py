# Author: ray
# Date: 5/8/24
# Description:
from collections import defaultdict

import numpy as np

from Interfaces.min_distance_strategy import MinDistanceStrategy


class GapFiller:
    ts: np.ndarray
    m: int
    t: int
    last_valid_v_index: int  # predecessor of the gap
    next_valid_v_index: int  # successor of the gap
    l: int  # gap length
    n_f: int  # forward branching time
    n_b: int  # backward branching time
    r: int  # stride step
    last_valid_closest_neighbor_index: int
    next_valid_closest_neighbor_index: int
    mds: MinDistanceStrategy
    reconstructed_vectors: np.ndarray

    def __init__(self, ts: np.ndarray, m: int, t: int, n_f: int, n_b: int, r: int, mds: MinDistanceStrategy,):
        self.ts = ts
        self.m = m
        self.t = t
        self.n_f = n_f
        self.n_b = n_b
        self.r = r
        self.mds = mds
        self.reconstruct_timeseries()
        self.get_breaking_points()

    def get_branches_backward(self):

        l = self.next_valid_v_index - self.last_valid_v_index - 1

        back_branches_df = defaultdict(set)
        back_branches_df_reverse = dict()

        curr_node_index = self.next_valid_v_index

        for i in range(self.n_b):
            if self.last_valid_v_index + (i * (1 + self.r)) >= self.next_valid_v_index:
                break
            jump_to_index = self.mds.get_closest_vector_index_by_index(vector_set=self.reconstructed_vectors,
                                                                       vector_index=curr_node_index)
            back_branches_df[curr_node_index].add(jump_to_index)
            back_branches_df_reverse[jump_to_index] = curr_node_index
            back_branches_df, back_branches_df_reverse = (
                self.get_one_branch(index=jump_to_index,
                                    rest_steps=l - (i * (self.r + 1)) - 1,
                                    forward_branches_df=back_branches_df,
                                    forward_branches_df_reverse=back_branches_df_reverse,
                                    forward=False))
            curr_node_index = jump_to_index - self.r
        return back_branches_df, back_branches_df_reverse

    def get_branches_forward(self):
        l = self.next_valid_v_index - self.last_valid_v_index - 1

        forward_branches_df = defaultdict(set)
        forward_branches_df_reverse = dict()

        curr_node_index = self.last_valid_v_index

        for i in range(self.n_f):
            if self.last_valid_v_index + (i * (1 + self.r)) >= self.next_valid_v_index:
                break
            jump_to_index = self.mds.get_closest_vector_index_by_index(vector_set=self.reconstructed_vectors,
                                                                       vector_index=curr_node_index)
            forward_branches_df[curr_node_index].add(jump_to_index)
            forward_branches_df_reverse[jump_to_index] = curr_node_index
            forward_branches_df, forward_branches_df_reverse \
                = self.get_one_branch(index=jump_to_index,
                                      rest_steps=l - (i * (self.r + 1)) - 1,
                                      forward_branches_df=forward_branches_df,
                                      forward=True,
                                      forward_branches_df_reverse=forward_branches_df_reverse)
            curr_node_index = jump_to_index + self.r
        return forward_branches_df, forward_branches_df_reverse

    def get_one_branch(self, index: int, rest_steps: int, forward_branches_df: dict,
                       forward_branches_df_reverse, forward: bool = True):
        #        next_node
        #         /
        # vectors[index]
        #         \
        #        next_node_2

        step = 1 if forward else -1

        curr_root = index
        curr_child = curr_root + step
        for i in range(rest_steps):
            if curr_child >= len(self.reconstructed_vectors):
                break
            if np.any(np.isnan(self.reconstructed_vectors[curr_child])):
                break
            forward_branches_df[curr_root].add(curr_child)
            forward_branches_df_reverse[curr_child] = curr_root
            curr_root = curr_root + step
            curr_child = curr_root + step

        return forward_branches_df, forward_branches_df_reverse

    def calc_last_valid_closest_neighbor_index(self):
        self.last_valid_closest_neighbor_index = (
            self.mds.get_closest_vector_index_by_index(vector_set=self.reconstructed_vectors,
                                                       vector_index=self.last_valid_v_index)
        )

    def reconstruct_timeseries(self):
        indices_list = []
        for i in range(self.m):
            indices_list.append(np.arange(i, len(self.ts), self.t))

        shortest_length = len(indices_list[-1])
        indices_list = [i[:shortest_length] for i in indices_list]
        vector_entries = [self.ts[i] for i in indices_list]
        self.reconstructed_vectors = np.column_stack(vector_entries)

    def get_breaking_points(self):
        """
        Get the first invalid (first_nan_index) gap points and next gap point (last_nan_index).

        Returns
        -------

        """
        # Create a boolean mask where each sub-array is checked for NaN
        contains_nan = np.array([np.any(np.isnan(vector)) for vector in self.reconstructed_vectors])

        # Find the index of the first sub-array containing NaN
        first_nan_index = np.argmax(contains_nan)

        # Find the index of the last sub-array containing NaN
        last_nan_index = np.max(np.where(contains_nan)[0]) if np.any(contains_nan) else None

        last_valid_v_index = first_nan_index - 1
        next_valid_v_index = last_nan_index + 1

        if last_valid_v_index < 0 or next_valid_v_index >= len(self.reconstructed_vectors):
            raise ValueError('Invalid gap points, this method is not applicable for forcasting '
                             '(neither forward or backward)')

        self.last_valid_v_index = last_valid_v_index
        self.next_valid_v_index = next_valid_v_index
        self.l = next_valid_v_index - last_valid_v_index
