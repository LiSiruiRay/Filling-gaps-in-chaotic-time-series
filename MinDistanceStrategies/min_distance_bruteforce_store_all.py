# Author: ray
# Date: 5/8/24
# Description:
from typing import Tuple, List, Union

import numpy as np
from scipy import linalg

from Interfaces.min_distance_strategy import MinDistanceStrategy


class MinDistanceBruteforceStoreAll(MinDistanceStrategy):
    """
    This strategy will brute force find all distance between each other in the set.
    The advantage of this method is that only once calculation is required with time complexity O(n^2).
    All the rest running has time complexity O(1).
    """
    dis_matrix: np.ndarray

    def get_dis_matrix(self, vectors: np.ndarray):
        dis_matrix = np.zeros((len(vectors), len(vectors)))
        for m, i in enumerate(vectors):
            for n, j in enumerate(vectors):
                if any(np.isnan(i)) or any(np.isnan(j)):
                    dis_matrix[m, n] = np.inf
                    continue
                if m == n:
                    dis_matrix[m, n] = np.inf
                    continue
                dis_matrix[m, n] = linalg.norm(i - j)
        self.dis_matrix = dis_matrix

    def get_closest_vector_index_by_index(self, vector_set: Union[np.ndarray, List],
                                          vector_index: int) -> int:
        if self.dis_matrix is None:
            MinDistanceBruteforceStoreAll.get_dis_matrix(vector_set)
        closest_point_index = np.argmin(self.dis_matrix[vector_index])
        return closest_point_index

    def get_closest_vector_index(self, vector_set: Union[np.ndarray, List],
                                 vector: np.ndarray) -> int:
        raise NotImplementedError("Get closes vector index method must be implemented")
