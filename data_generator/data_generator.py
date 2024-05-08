# Author: ray
# Date: 5/8/24
# Description: This is a script for generating datas for time series
import copy

import numpy as np

from tools.lorenz import Lorenz63
from tools.utils import iterate_solver, Runge_Kutta


def demo_data_generator():
    """
    Demo data generator. Generate data based on
    [Lorenz system](https://en.wikipedia.org/wiki/Lorenz_system)
    with parameter `s` = 10, `r` = 28, and  `b` = 8/3.
    This set of parameter gives all the solution bounded
    (https://www.math.toronto.edu/kzhang/teaching/courses/mat332-2022/_8-lorenz-system/)
    (do not escape to infinity). With initial condition: -1, 1, 18.4

    By doing so we get a list of vector. The first entries of all the vector
    form our testing dataset.

    Returns
    -------
    Generated time series data set.

    """
    x, t = iterate_solver(Runge_Kutta, Lorenz63, [-1., 1., 18.4], 0, 0.01, 50.)
    x_gapped = copy.deepcopy(x)
    x_gapped[2000:2100] = np.nan
    ts = x_gapped[:, 0]
    return ts
