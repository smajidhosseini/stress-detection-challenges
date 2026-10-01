import unittest

import numpy as np
import pandas as pd

from generate_figure4_all_subjects import detect_transitions, centered_event_window, dataset_specs


class TransitionTests(unittest.TestCase):
    def test_dataset_scope_excludes_nurses(self):
        self.assertEqual(
            [spec["name"] for spec in dataset_specs()],
            ["WESAD", "EmpathicSchool", "AffectiveROAD"],
        )

    def test_detects_all_bidirectional_changes_among_zero_one_two(self):
        labels = pd.Series([0, 0, 1, 1, 2, 1, 0, 2, 2])
        events = detect_transitions(labels)
        self.assertEqual(
            [(e.index, e.before, e.after) for e in events],
            [(2, 0, 1), (4, 1, 2), (5, 2, 1), (6, 1, 0), (7, 0, 2)],
        )

    def test_ignores_nan_gaps_instead_of_inventing_transitions(self):
        labels = pd.Series([0, np.nan, 2, 2, 1])
        events = detect_transitions(labels)
        self.assertEqual([(e.index, e.before, e.after) for e in events], [(4, 2, 1)])

    def test_centered_window_uses_seconds_and_clips_boundaries(self):
        frame = pd.DataFrame({"value": range(8)})
        window = centered_event_window(frame, event_index=1, step_seconds=15, radius_seconds=60)
        self.assertEqual(window["relative_seconds"].tolist(), [-15.0, 0.0, 15.0, 30.0, 45.0, 60.0])
        self.assertEqual(window["value"].tolist(), [0, 1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
