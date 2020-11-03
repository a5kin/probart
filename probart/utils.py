"""Different utility functions"""

import math


def polar2vec(r, phi):
    """Calculate Cartesian vector from polar coords."""
    x = r * math.cos(phi)
    y = -r * math.sin(phi)
    return x, y
