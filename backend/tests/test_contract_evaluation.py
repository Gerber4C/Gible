import unittest

from engine.contract_evaluation import ContractTarget, compare_contract_targets


class ContractEvaluationTests(unittest.TestCase):
    def test_compares_each_declared_target_on_the_same_sampled_deals(self):
        deals = ({"sample": 1}, {"sample": 2})
        seen = []

        def solve(deal):
            seen.append(deal)
            hearts = 12 if deal["sample"] == 1 else 10
            return {"H": {"n": hearts}, "NT": {"n": 9}}

        results = compare_contract_targets(
            deals,
            (ContractTarget(4, "H", "n"), ContractTarget(6, "H", "n"), ContractTarget(3, "NT", "n")),
            solve_table=solve,
        )

        self.assertEqual(seen, list(deals))
        self.assertEqual([(r.contract, r.made, r.sample_count, r.completion_rate) for r in results], [
            ("4H", 2, 2, 1.0),
            ("6H", 1, 2, 0.5),
            ("3NT", 2, 2, 1.0),
        ])

    def test_rejects_invalid_targets_and_empty_samples(self):
        for args in ((0, "H", "n"), (8, "H", "n"), (4, "Z", "n"), (4, "H", "x")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                ContractTarget(*args)
        with self.assertRaises(ValueError):
            compare_contract_targets((), (ContractTarget(4, "H", "n"),), solve_table=lambda _: {})

    def test_rejects_out_of_range_solver_result(self):
        with self.assertRaises(ValueError):
            compare_contract_targets(({"sample": 1},), (ContractTarget(4, "H", "n"),),
                                     solve_table=lambda _: {"H": {"n": 14}})


if __name__ == "__main__":
    unittest.main()
