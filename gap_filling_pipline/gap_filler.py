# Author: ray
# Date: 5/8/24
# Description:
import numpy as np

from Interfaces.min_distance_strategy import MinDistanceStrategy


class GapFiller:
    ts: np.ndarray
    m: int
    t: int
    mds: MinDistanceStrategy
    reconstructed_vectors: np.ndarray

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

        return first_nan_index, last_nan_index
