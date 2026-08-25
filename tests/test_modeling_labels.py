import unittest

import pandas as pd

from pecgap.modeling import build_user_feature_table


class ModelingLabelTest(unittest.TestCase):
    def test_rq4_label_uses_zero_overlap_for_empty_preferences_and_negative_median_ties(self):
        alignment = pd.DataFrame(
            {
                "user_id": ["u1", "u2", "u3", "u4"],
                "click_count": [1, 2, 3, 4],
                "category_divergence": [0.5, 0.8, 0.8, float("nan")],
            }
        )

        result = build_user_feature_table(alignment, pd.DataFrame(), pd.DataFrame())

        self.assertEqual(result["divergence_score"].tolist(), [0.5, 0.8, 0.8, 1.0])
        # Median divergence is 0.8: ties are negative and only the empty-profile
        # case, operationalized as D=1, is positive.
        self.assertEqual(
            result["high_divergence"].tolist(), [False, False, False, True]
        )


if __name__ == "__main__":
    unittest.main()
