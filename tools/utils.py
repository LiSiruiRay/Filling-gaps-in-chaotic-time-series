# Author: ray
# Date: 5/6/24
# Description:
from typing import List, Dict, Set

from pylab import *


def iterate_solver(sol, fun, xstart, tstart, h, tend):
    """
        Iterate a one-step solver with time step h starting from initial
        condition xstart at tstart, until tend is reached.

        Inputs
        sol:    a function that implements a one-step solver. sol(f,x,t,h) must
                yield an estimate of x(t+h)
        fun:    the vector field that defines the (system) of ordinary differential
                equation(s). The time derivative of the state x must be given by f(x,t)
        xstart: the initial condition, a vector of n elements, or a float for 1D
                problems.
        tstart: the time corresponding to the initial condition. It's ignored for
                autonomous problems (that is, problems where f does not explicitly
                depend on time).
        tend:   the time after which the iterations must stop.

        Returns
        xs:    an (m+1)xn matrix containing the state vectors of the solution.
               xs[0,:] is equal to the initial condition xstart. m is the number of
               time steps performed. n is the number of elements of xstart.
        times: the times correspoding to the vectors in xs. times[0] is tstart
    """
    xs = [xstart]
    times = [tstart]
    iter = 0
    while times[-1] < tend:
        iter += 1
        xnew = sol(fun, xs[-1], times[-1], h)
        xs.append(xnew)
        times.append(tstart + iter * h)

    return array(xs), array(times)


def Runge_Kutta(f, x, t, h):
    """
    Runge-Kutta method
    Parameters
    ----------
    f
    x
    t
    h

    Returns
    -------

    """
    s_1 = f(x, t)
    s_2 = f(x + h / 2 * s_1, t + h / 2)
    s_3 = f(x + h / 2 * s_2, t + h / 2)
    s_4 = f(x + h * s_3, t + h)
    return x + h / 6 * (s_1 + 2 * s_2 + 2 * s_3 + s_4)


def tree_to_layers(tree: Dict[Set], queue: list, max_layer: int) -> List[List]:
    """
    Takes a tree and converts it into a tree of layers.
    Parameters
    ----------
    tree : dict
        The tree to convert.
    queue : list
        The queue of layers to convert. Queue of tuples (node, layer_index)
    max_layer : int
        The maximum number of layers to convert.

    Returns
    -------
    list
        List of layers. Each layer is a list.
    """
    layers = []
    # queue = [("root", 0)]

    prev_layer = None
    while queue and max_layer > 0:
        print(f"while --------------")
        print(queue)
        # max_layer -= 1
        current_node, layer = queue.pop(0)
        if prev_layer != layer:
            max_layer -= 1
            prev_layer = layer

        # Ensure the layer exists in the layers list
        if len(layers) <= layer:
            layers.append([])

        # Append the current node to its respective layer
        layers[layer].append(current_node)

        # Enqueue all children of the current node
        for child in tree.get(current_node, []):
            queue.append((child, layer + 1))

    return layers
