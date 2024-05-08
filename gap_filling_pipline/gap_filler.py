# Author: ray
# Date: 5/8/24
# Description:
from collections import defaultdict
from typing import Set, Dict

import numpy as np
from scipy import linalg

from Interfaces.functional_J_strategy import FunctionalJStrategy
from Interfaces.min_distance_strategy import MinDistanceStrategy
from Interfaces.vector_field_f_stategy import VectorFieldFStrategy
from tools.utils import tree_to_layers


class GapFiller:
    ts: np.ndarray
    m: int
    t: int
    l: int  # gap length
    n_f: int  # forward branching time
    n_b: int  # backward branching time
    r: int  # stride step

    fjs: FunctionalJStrategy
    vffs: VectorFieldFStrategy

    # ----
    last_valid_v_index: int  # predecessor of the gap
    next_valid_v_index: int  # successor of the gap
    last_valid_closest_neighbor_index: int
    next_valid_closest_neighbor_index: int
    mds: MinDistanceStrategy
    reconstructed_vectors: np.ndarray

    # ----
    forward_branches_df: Dict[int, Set]
    forward_branches_df_reverse: Dict[int, int]
    backward_branches_df: Dict[int, Set]
    backward_branches_df_reverse: Dict[int, int]

    def __init__(self, ts: np.ndarray, m: int, t: int, n_f: int, n_b: int, r: int,
                 mds: MinDistanceStrategy, fjs: FunctionalJStrategy, vffs: VectorFieldFStrategy):
        self.ts = ts
        self.m = m
        self.t = t
        self.n_f = n_f
        self.n_b = n_b
        self.r = r
        self.mds = mds
        self.fjs = fjs
        self.vffs = vffs
        self.reconstruct_timeseries()
        self.get_breaking_points()

    def get_branches_backward(self):

        l = self.next_valid_v_index - self.last_valid_v_index - 1

        backward_branches_df = defaultdict(set)
        backward_branches_df_reverse = dict()

        curr_node_index = self.next_valid_v_index

        for i in range(self.n_b):
            if self.last_valid_v_index + (i * (1 + self.r)) >= self.next_valid_v_index:
                break
            jump_to_index = self.mds.get_closest_vector_index_by_index(vector_set=self.reconstructed_vectors,
                                                                       vector_index=curr_node_index)
            backward_branches_df[curr_node_index].add(jump_to_index)
            backward_branches_df_reverse[jump_to_index] = curr_node_index
            backward_branches_df, backward_branches_df_reverse = (
                self.get_one_branch(index=jump_to_index,
                                    rest_steps=l - (i * (self.r + 1)) - 1,
                                    forward_branches_df=backward_branches_df,
                                    forward_branches_df_reverse=backward_branches_df_reverse,
                                    forward=False))
            curr_node_index = jump_to_index - self.r
        self.backward_branches_df, self.backward_branches_df_reverse = backward_branches_df, backward_branches_df_reverse

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
        self.forward_branches_df, self.forward_branches_df_reverse = forward_branches_df, forward_branches_df_reverse

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
        """
        Construct vectors from a timeseries.

        Returns
        -------

        """
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
        # self.l = next_valid_v_index - last_valid_v_index

    def get_closest_points_layer(self):
        """
        This is the function picking out the best forward and backward branch.
        By iterating over all pairs the synchronous points, we find two closest points.

        Parameters
        ----------
        forward_layer: The layer form of branches converted from forward branches
        backward_layer:  The layer form of branches converted from backward branches

        Returns
        -------
            The closest points' information.
        """

        self.forward_layer = tree_to_layers(self.forward_branches_df,
                                       queue=[(self.last_valid_v_index, 0)],
                                       max_layer=self.next_valid_v_index - self.last_valid_v_index)
        self.backward_layer = tree_to_layers(self.backward_branches_df,
                                        queue=[(self.next_valid_v_index, 0)],
                                        max_layer=self.next_valid_v_index - self.last_valid_v_index)

        l = len(self.forward_layer) - 1
        closest_dis = float('inf')
        closest_forward_index = 0
        closest_forward_index_sub = 0
        closest_backward_index_sub = 0
        for i in range(l):
            forward_vectors = self.forward_layer[i]
            backward_vectors = self.backward_layer[l - i]
            forward_sub_index, backward_sub_index, dis = (
                self.get_closest_points_one_layer(forward_vectors,
                                                  backward_vectors))
            if dis < closest_dis:
                closest_dis = dis
                closest_forward_index = i
                closest_forward_index_sub = forward_sub_index
                closest_backward_index_sub = backward_sub_index
        (self.closest_dis, self.closest_forward_index,
         self.closest_forward_index_sub, self.closest_backward_index_sub) = (
            closest_dis, closest_forward_index,
            closest_forward_index_sub, closest_backward_index_sub)

    def get_closest_points_one_layer(self, forward_vectors, backward_vectors):
        """
        Helper function to `get_closest_points_layer`, get the closest point between one layer
        (one forward and one backward)

        Parameters
        ----------
        forward_vectors
        backward_vectors

        Returns
        -------

        """
        min_dis = float('inf')
        forward_sub_index = 0
        backward_sub_index = 0
        for n, i in enumerate(forward_vectors):
            for m, j in enumerate(backward_vectors):
                curr_dis = linalg.norm(self.reconstructed_vectors[i] - self.reconstructed_vectors[j])
                if curr_dis < min_dis:
                    min_dis = curr_dis
                    forward_sub_index = n
                    backward_sub_index = m
        return forward_sub_index, backward_sub_index, min_dis

    def get_gap_vector_index_list(self):
        l = self.next_valid_v_index - self.last_valid_v_index - 1
        forward_vector_index = self.forward_layer[self.closest_forward_index][self.closest_forward_index_sub]
        backward_vector_index = self.backward_layer[l - self.closest_forward_index][self.closest_backward_index_sub]
        vector_index_list = list()
        curr_backward_vector_index = backward_vector_index
        curr_forward_vector_index = forward_vector_index
        for i in range(self.closest_forward_index):
            vector_index_list.insert(0, curr_forward_vector_index)
            curr_forward_vector_index = self.forward_branches_df_reverse[curr_forward_vector_index]

        for i in range(l - self.closest_forward_index):
            vector_index_list.append(curr_backward_vector_index)
            curr_backward_vector_index = self.backward_branches_df_reverse[curr_backward_vector_index]

        return vector_index_list
