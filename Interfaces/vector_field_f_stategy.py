# Author: ray
# Date: 5/8/24
# Description:
import numpy as np


class VectorFieldFStrategy:
    def F(self, j: int, gap_filling_vectors: np.ndarray, reconstructed_vectors: np.ndarray, t: np.ndarray):
        raise NotImplementedError("F must be implemented")