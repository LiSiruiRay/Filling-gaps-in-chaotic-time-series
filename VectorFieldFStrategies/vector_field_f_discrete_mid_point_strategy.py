# Author: ray
# Date: 5/8/24
# Description:
import numpy as np
from scipy import linalg

from Interfaces.vector_field_f_stategy import VectorFieldFStrategy


class VectorFieldFDiscreteMidPointStrategy(VectorFieldFStrategy):
    def F(self, j: int, gap_filling_vectors: np.ndarray, reconstructed_vectors: np.ndarray, t: np.ndarray):
        # vector_list is the gapped vector
        # closes to x_j
        # second close to x_j
        # predecesor of both
        x_j = gap_filling_vectors[j]
        dis_list = self.get_distance_list(vector=x_j, reconstructed_vectors=reconstructed_vectors)
        closest_x_j_index = np.argmin(dis_list)
        while closest_x_j_index - 1 < 0 or any(np.isnan(reconstructed_vectors[closest_x_j_index - 1])):
            dis_list[closest_x_j_index] = np.inf
            closest_x_j_index = np.argmin(dis_list)
        x_j_bar = reconstructed_vectors[closest_x_j_index]
        p_x_j_bar = reconstructed_vectors[closest_x_j_index - 1]

        dis_list[closest_x_j_index] = np.inf
        sec_closest_x_j_index = np.argmin(dis_list)

        while sec_closest_x_j_index - 1 < 0 or any(np.isnan(reconstructed_vectors[sec_closest_x_j_index - 1])):
            dis_list[sec_closest_x_j_index] = np.inf
            sec_closest_x_j_index = np.argmin(dis_list)

        x_j_bar_bar = reconstructed_vectors[sec_closest_x_j_index]
        p_x_j_bar_bar = reconstructed_vectors[sec_closest_x_j_index - 1]
        delta_t = t[1] - t[0]

        return (x_j_bar - p_x_j_bar + x_j_bar_bar - p_x_j_bar_bar) / (2 * delta_t)

    def get_distance_list(self, vector, reconstructed_vectors):
        dis_list = np.zeros(len(reconstructed_vectors))
        for n, j in enumerate(reconstructed_vectors):
            if any(np.isnan(j)):
                dis_list[n] = np.inf
                continue
            dis_list[n] = linalg.norm(vector - j)
        return dis_list
