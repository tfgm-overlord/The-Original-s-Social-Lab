import unittest

from run import dependency_status, load_scenario, state_aware


def base_events():
    return [
        {
            "id": "A",
            "kind": "state",
            "subject": "db",
            "state_version": 1,
            "claim": "db=PostgreSQL",
        },
        {
            "id": "C",
            "kind": "derived",
            "subject": "config",
            "state_version": 1,
            "claim": "postgres config",
            "derived_from": ["A"],
        },
        {
            "id": "D",
            "kind": "derived",
            "subject": "portable",
            "state_version": 1,
            "claim": "portable config",
            "derived_from": ["A"],
            "independent_support": ["I"],
        },
        {
            "id": "I",
            "kind": "evidence",
            "subject": "portable",
            "state_version": 2,
            "claim": "independent portable test",
        },
        {
            "id": "B",
            "kind": "state",
            "subject": "db",
            "state_version": 2,
            "claim": "db=SQLite",
            "supersedes": ["A"],
        },
    ]


class HarnessTests(unittest.TestCase):
    def test_core_scenario(self):
        result = state_aware(load_scenario()["events"])
        self.assertEqual(result["current_by_subject"], {"database": "E4", "migration_window": "E5"})
        self.assertEqual(result["needs_revalidation"], ["E2", "E8"])
        self.assertEqual(result["usable_derived_claims"], ["E7"])
        self.assertEqual(result["superseded"], ["E1", "E3"])

    def test_transitive_invalidation(self):
        events = base_events() + [
            {
                "id": "F",
                "kind": "derived",
                "subject": "driver",
                "state_version": 2,
                "claim": "driver",
                "derived_from": ["C"],
            }
        ]
        self.assertEqual(dependency_status(events)["F"], "needs_revalidation")

    def test_independent_support_prevents_over_invalidation(self):
        self.assertEqual(dependency_status(base_events())["D"], "current")

    def test_explicitly_superseded_derived_claim_wins(self):
        events = base_events() + [
            {
                "id": "D2",
                "kind": "derived",
                "subject": "portable",
                "state_version": 2,
                "claim": "new portable",
                "supersedes": ["D"],
                "independent_support": ["I"],
            }
        ]
        status = dependency_status(events)
        self.assertEqual(status["D"], "superseded")
        self.assertEqual(status["D2"], "current")

    def test_unknown_reference_rejected(self):
        events = base_events() + [
            {
                "id": "X",
                "kind": "derived",
                "subject": "x",
                "state_version": 2,
                "claim": "x",
                "derived_from": ["MISSING"],
            }
        ]
        with self.assertRaises(ValueError):
            state_aware(events)

    def test_dependency_cycle_rejected(self):
        events = base_events() + [
            {
                "id": "X",
                "kind": "derived",
                "subject": "x",
                "state_version": 1,
                "claim": "x",
                "derived_from": ["Y"],
            },
            {
                "id": "Y",
                "kind": "derived",
                "subject": "y",
                "state_version": 1,
                "claim": "y",
                "derived_from": ["X"],
            },
        ]
        with self.assertRaises(ValueError):
            state_aware(events)

    def test_equal_current_versions_rejected(self):
        events = base_events() + [
            {
                "id": "B2",
                "kind": "state",
                "subject": "db",
                "state_version": 2,
                "claim": "db=MySQL",
            }
        ]
        with self.assertRaises(ValueError):
            state_aware(events)

    def test_event_order_does_not_change_state_aware_result(self):
        events = base_events()
        self.assertEqual(state_aware(events), state_aware(list(reversed(events))))


if __name__ == "__main__":
    unittest.main()
