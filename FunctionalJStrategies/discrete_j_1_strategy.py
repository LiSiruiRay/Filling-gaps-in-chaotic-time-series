# Author: ray
# Date: 5/8/24
# Description:
from typing import Callable

import numpy as np
from scipy import linalg

from Interfaces.functional_J_strategy import FunctionalJStrategy


class DiscreteJ1Strategy(FunctionalJStrategy):
    def J(self, gap_filling_vectors: np.ndarray, reconstructed_vectors: np.ndarray, t: np.ndarray,
          F: Callable[[int, np.ndarray, np.ndarray, np.ndarray], np.ndarray]) -> int:
        w = gap_filling_vectors
        l = len(w)
        sum_squares = 0
        for j in range(l):
            delta_w = (w[j] - w[j - 1]) / t[j + 1] - t[j]
            F_value = F(j=j, vectors=reconstructed_vectors, vector_list=gap_filling_vectors, t=t)
            sum_squares += linalg.norm(delta_w - F_value) ** 2
        return sum_squares
