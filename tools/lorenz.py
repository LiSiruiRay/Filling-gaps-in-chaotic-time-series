# Author: ray
# Date: 5/6/24
# Description:

from pylab import *


def Lorenz63(x, t=None):
    """
        Saltzman's equations studied by Lorenz in his 1963 paper on chaos.
        Inputs
        x:  a 3-elements vector
        t:  dummy variable that allows to use this function with integrators written
            for non-autonomous problems

        Returns the right-hand side of equations (6.53) in the book, but with
        different parameters.

    """
    s = 10.  # Prandtl's number
    r = 28.  # 13.92655741 #16.    #28.   #Rayleigh number
    b = 8. / 3.  # aspect ratio
    x = array(x)
    if x.shape != (3,):
        raise ValueError("The state of Lorenz's system is described by a vector with 3 elements")
    return array([- s * (x[0] - x[1]),
                  - x[0] * (x[2] - r) - x[1],
                  x[0] * x[1] - b * x[2]])
