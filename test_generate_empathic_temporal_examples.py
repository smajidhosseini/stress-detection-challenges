import unittest

from generate_empathic_temporal_examples import SELECTED_EXAMPLES


class SelectedExamplesTests(unittest.TestCase):
    def test_contains_only_the_two_approved_examples(self):
        self.assertEqual(
            [(item["subject"], item["subject_event"]) for item in SELECTED_EXAMPLES],
            [("1.0", 2), ("2.0", 6)],
        )

    def test_both_examples_are_one_to_two_transitions(self):
        self.assertTrue(all(item["transition"] == (1, 2) for item in SELECTED_EXAMPLES))


if __name__ == "__main__":
    unittest.main()
