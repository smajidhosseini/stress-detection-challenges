import unittest

from generate_affectiveroad_temporal_examples import SELECTED_EXAMPLES


class SelectedExamplesTests(unittest.TestCase):
    def test_contains_only_the_two_approved_examples(self):
        self.assertEqual(
            [(item["subject"], item["subject_event"]) for item in SELECTED_EXAMPLES],
            [("GM2", 38), ("SJ1", 1)],
        )

    def test_approved_transition_directions_are_preserved(self):
        self.assertEqual(
            [item["transition"] for item in SELECTED_EXAMPLES],
            [(1, 2), (0, 2)],
        )


if __name__ == "__main__":
    unittest.main()
