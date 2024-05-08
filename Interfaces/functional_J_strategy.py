# Author: ray
# Date: 5/8/24
# Description:
from typing import Callable

import numpy as np


class FunctionalJStrategy:
    """
    This is the discrete form of functional J in the paper.
    """
    def J(self, gap_filling_vectors: np.ndarray, reconstructed_vectors: np.ndarray, t: np.ndarray,
          F: Callable[[int, np.ndarray, np.ndarray, np.ndarray], np.ndarray]) -> int:
        raise NotImplementedError("J must be implemented")
