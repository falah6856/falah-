import json, math, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search_metrics as sm  # noqa: E402


class TestNormalize(unittest.TestCase):
    def test_url_variants_collapse(self):
        a = sm.norm_url("https://www.Example.com/Path/?utm_source=x&id=3#frag")
        b = sm.norm_url("http://example.com/Path?id=3")
        self.assertEqual(a, b)

    def test_title_normalization(self):
        self.assertEqual(sm.norm_title("  Hello, World!  "), sm.norm_title("hello world"))


class TestFuse(unittest.TestCase):
    def test_rrf_prefers_items_high_in_many_lists(self):
        rows = [
            {"title": "A", "url": "https://a.com", "query": "q1", "rank": 1},
            {"title": "B", "url": "https://b.com", "query": "q1", "rank": 2},
            {"title": "B", "url": "https://www.b.com/", "query": "q2", "rank": 1},
            {"title": "C", "url": "https://c.com", "query": "q2", "rank": 2},
        ]
        fused = sm.fuse(rows)
        self.assertEqual(fused[0]["title"], "B")
        self.assertEqual(len(fused), 3)
        self.assertAlmostEqual(fused[0]["score"], 1 / 62 + 1 / 61)


class TestSaturation(unittest.TestCase):
    def test_new_items_per_round(self):
        rows = [
            {"url": "https://a.com", "round": 1},
            {"url": "https://b.com", "round": 1},
            {"url": "https://a.com", "round": 2},
            {"url": "https://c.com", "round": 2},
            {"url": "https://c.com", "round": 3},
        ]
        rep = sm.saturation(rows)
        self.assertEqual([r["new"] for r in rep], [2, 1, 0])
        self.assertEqual(rep[-1]["cumulative"], 3)


class TestRecapture(unittest.TestCase):
    def test_chapman_estimate(self):
        # n1=10, n2=8, overlap m=4 -> (11*9)/5 - 1 = 18.8
        est = sm.chapman(10, 8, 4)
        self.assertAlmostEqual(est["N"], 18.8)
        self.assertLess(est["low"], est["N"])
        self.assertGreater(est["high"], est["N"])

    def test_zero_overlap_is_flagged(self):
        est = sm.chapman(5, 5, 0)
        self.assertTrue(est["warning"])


class TestRecall(unittest.TestCase):
    def test_recall_by_title_or_url(self):
        rows = [{"title": "Attention Is All You Need", "url": "https://arxiv.org/abs/1706.03762"}]
        known = ["attention is all you need", "https://bert.example/", "https://arxiv.org/abs/1706.03762"]
        rep = sm.recall(rows, known)
        self.assertEqual(rep["found"], 2)
        self.assertEqual(rep["n"], 3)
        self.assertTrue(0 <= rep["ci_low"] <= rep["recall"] <= rep["ci_high"] <= 1)


class TestCLI(unittest.TestCase):
    def test_fuse_cli_runs(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"title": "A", "url": "https://a.com", "query": "q", "rank": 1}) + "\n")
            path = f.name
        out = subprocess.run([sys.executable, os.path.join(HERE, "search_metrics.py"), "fuse", path],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("https://a.com", out.stdout)


if __name__ == "__main__":
    unittest.main()
