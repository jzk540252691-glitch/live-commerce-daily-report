import unittest
from pathlib import Path
from report import render

class BusinessRules(unittest.TestCase):
    def test_correction(self):
        before = render(Path("example.csv"), "2026-01-03")
        after = render(Path("corrected.csv"), "2026-01-03")
        self.assertIn("<td>—</td><td>/</td><td>待补：投流消耗</td>", before)
        self.assertIn("<td>1,200.00</td><td>4.50</td><td>已齐</td>", after)

    def test_zero_and_off_air(self):
        self.assertIn("<td>0.00</td><td>/</td><td>已齐</td>", render(Path("example.csv"), "2026-01-02"))
        self.assertIn("<td>未开播</td>", render(Path("example.csv"), "2026-01-01"))
