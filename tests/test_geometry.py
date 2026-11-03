import math
import unittest
from eit_icecube.geometry import angle_deg, dot, norm, solve_3x3, unit


class GeometryTests(unittest.TestCase):
    def test_normalization(self):
        self.assertAlmostEqual(norm(unit([3, 4, 0])), 1.0)

    def test_normalization_rejects_zero(self):
        with self.assertRaises(ValueError):
            unit([0, 0, 0])

    def test_normalization_rejects_nan(self):
        with self.assertRaises(ValueError):
            unit([float('nan'), 0, 0])

    def test_angle_equal(self):
        self.assertAlmostEqual(angle_deg([1, 0, 0], [1, 0, 0]), 0, places=6)

    def test_angle_opposed(self):
        self.assertAlmostEqual(angle_deg([1, 0, 0], [-1, 0, 0]), 180, places=6)

    def test_angle_orthogonal(self):
        self.assertAlmostEqual(angle_deg([1, 0, 0], [0, 1, 0]), 90, places=6)

    def test_dot(self):
        self.assertEqual(dot([2, 3, 4], [5, 6, 7]), 56)

    def test_solve(self):
        x = solve_3x3([[3, 2, 0], [1, -1, 0], [0, 0, 2]], [7, 0, 8])
        self.assertAlmostEqual(x[0], 1.4)
        self.assertAlmostEqual(x[1], 1.4)
        self.assertAlmostEqual(x[2], 4)

    def test_singular(self):
        with self.assertRaises(ValueError):
            solve_3x3([[1, 2, 3], [2, 4, 6], [3, 6, 9]], [1, 2, 3])

    def test_pivot(self):
        sol = solve_3x3([[0, 1, 0], [1, 0, 0], [0, 0, 1]], [3, 4, 5])
        self.assertEqual(sol, [4, 3, 5])
