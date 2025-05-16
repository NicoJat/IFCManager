"""
Geometry Utilities

Helper functions for geometric calculations and transformations.
"""

import math
import numpy as np
import logging

logger = logging.getLogger(__name__)

def normalize_vector(vector):
    """Normalizes a 3D vector."""
    magnitude = math.sqrt(sum(x**2 for x in vector))
    if magnitude < 1e-9:
        return (0.0, 0.0, 0.0)
    return tuple(x/magnitude for x in vector)

def transform_point(point, transformation_matrix):
    """Applies a 4x4 transformation matrix to a 3D point."""
    x, y, z = point
    return (
        transformation_matrix[0][0]*x + transformation_matrix[0][1]*y + 
        transformation_matrix[0][2]*z + transformation_matrix[0][3],
        transformation_matrix[1][0]*x + transformation_matrix[1][1]*y + 
        transformation_matrix[1][2]*z + transformation_matrix[1][3],
        transformation_matrix[2][0]*x + transformation_matrix[2][1]*y + 
        transformation_matrix[2][2]*z + transformation_matrix[2][3]
    )

def calculate_centroid(vertices):
    """Calculates centroid of a set of vertices."""
    if not vertices:
        return (0.0, 0.0, 0.0)
    sum_x = sum(v[0] for v in vertices)
    sum_y = sum(v[1] for v in vertices)
    sum_z = sum(v[2] for v in vertices)
    n = len(vertices)
    return (sum_x/n, sum_y/n, sum_z/n)

def calculate_element_length(start_point, end_point):
    """Calculates length between two 3D points."""
    return math.sqrt(
        (end_point[0]-start_point[0])**2 +
        (end_point[1]-start_point[1])**2 +
        (end_point[2]-start_point[2])**2
)