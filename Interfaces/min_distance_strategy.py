# Author: ray
# Date: 5/8/24
# Description:
from typing import Tuple, List, Union

import numpy as np


class MinDistanceStrategy:
    def get_closest_vector_index_by_index(self, vector_set: Union[np.ndarray, List],
                                          vector_index: int) -> int:
        raise NotImplementedError("Get closes vector index by index method must be implemented")

    def get_closest_vector_index(self, vector_set: Union[np.ndarray, List],
                                          vector: np.ndarray) -> int:
        raise NotImplementedError("Get closes vector index method must be implemented")
