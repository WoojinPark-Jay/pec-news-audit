import math
import unittest

from pecgap.metrics import jaccard


class JaccardTest(unittest.TestCase):
    def test_one_empty_set_has_zero_overlap(self):
        self.assertEqual(jaccard([], ["AI", "World"]), 0.0)
        self.assertEqual(jaccard(["AI"], []), 0.0)

    def test_two_empty_sets_are_undefined(self):
        self.assertTrue(math.isnan(jaccard([], [])))

    def test_nonempty_sets_use_union_denominator(self):
        self.assertAlmostEqual(jaccard(["AI", "World"], ["AI", "Sports"]), 1 / 3)


if __name__ == "__main__":
    unittest.main()
