# Author: ray
# Date: 5/8/24
# Description:
from typing import Tuple, List, Union

import numpy as np
from scipy import linalg

from Interfaces.min_distance_strategy import MinDistanceStrategy


class MinDistanceBruteforceStoreAll(MinDistanceStrategy):
    @classmethod
    def get_dis_matrix(cls, vectors: np.ndarray) -> np.ndarray:
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
        return dis_matrix

    def get_closest_vector_index_by_index(self, vector_set: Union[np.ndarray, List],
                                          vector_index: int) -> int:
        dis_matrix = MinDistanceBruteforceStoreAll.get_dis_matrix(vector_set)
        closest_point_index = np.argmin(dis_matrix[vector_index])
        return closest_point_index

    def get_closest_vector_index(self, vector_set: Union[np.ndarray, List],
                                          vector: np.ndarray) -> int:
        raise NotImplementedError("Get closes vector index method must be implemented")