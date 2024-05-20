# Author: ray
# Date: 5/8/24
# Description:
from collections import defaultdict
from typing import Set, Dict, List, Callable, Any

import numpy as np
from numpy import row_stack
from scipy import linalg

from Interfaces.functional_J_strategy import FunctionalJStrategy
from Interfaces.min_distance_strategy import MinDistanceStrategy
from Interfaces.vector_field_f_stategy import VectorFieldFStrategy
from tools.utils import tree_to_layers


class GapFiller:
    time_data: np.ndarray  # time
    ts: np.ndarray
    m: int
    t: int
    l: int  # gap length
    n_f: int  # forward branching time
    n_b: int  # backward branching time
    r: int  # stride step
    minimize: Callable[[Any], Any]

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

    # ----
    gap_vector_index_list: List[int]
    gap_vector_list: np.ndarray

    optimized_gap_vector: np.ndarray

    def __init__(self, time_data, ts: np.ndarray, m: int, t: int, n_f: int, n_b: int, r: int,
                 mds: MinDistanceStrategy, fjs: FunctionalJStrategy,
                 vffs: VectorFieldFStrategy, minimize: Callable[[Any], Any]):
        self.time_data = time_data
        self.ts = ts
        self.m = m
        self.t = t
        self.n_f = n_f
        self.n_b = n_b
        self.r = r
        self.mds = mds
        self.fjs = fjs
        self.vffs = vffs
        self.minimize = minimize
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
        N_bar = len(self.ts)
        for i in range(N_bar - (self.m-1)*self.t):
            indices_list.append(np.arange(i, i + (self.m - 1)*self.t + 1, self.t))

        shortest_length = len(indices_list[-1])
        indices_list = [i[:shortest_length] for i in indices_list]
        vector_entries = [self.ts[i] for i in indices_list]
        self.reconstructed_vectors = np.row_stack(vector_entries)
        # print(indices_list)
        print(self.reconstructed_vectors.shape)
        print(self.reconstructed_vectors[:, 0])
        # for i in self.reconstructed_vectors[0]:
        #     print(i)

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
            raise ValueError(f'Invalid gap points, this method is not applicable for forcasting '
                             f'(neither forward or backward)， first point is {last_valid_v_index}, last is {next_valid_v_index}')

        self.last_valid_v_index = last_valid_v_index
        self.next_valid_v_index = next_valid_v_index
        print(f"last_valid_v_index: {self.last_valid_v_index}")
        print(f"next_valid_v_index: {self.next_valid_v_index}")
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

    def get_gap_vector_and_index_list(self):
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

        self.gap_vector_index_list = vector_index_list
        gap_vector_list = [self.reconstructed_vectors[i] for i in self.gap_vector_index_list]
        gap_vector_list = row_stack(gap_vector_list)
        self.gap_vector_list = gap_vector_list

    def minimize_gap_vectors(self):
        def wrapper_J_for_minimize(v_f):
            return self.fjs.J(gap_filling_vectors=v_f.reshape((self.next_valid_v_index - self.last_valid_v_index - 1, self.m)),
                              reconstructed_vectors=self.reconstructed_vectors,
                              t=self.time_data, F=self.vffs.F)

        result = self.minimize(wrapper_J_for_minimize,
                              self.gap_vector_list.flatten(),
                              method='L-BFGS-B')
        self.optimized_gap_vector = result.x.reshape((self.next_valid_v_index - self.last_valid_v_index - 1, self.m))