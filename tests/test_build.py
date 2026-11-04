"""Smoke tests: build data.json from data/ and check invariants."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(tmp_path: Path) -> dict:
    out = tmp_path / "data.json"
    subprocess.run([sys.executable, "-I", "src/build.py", "data", str(out)], cwd=ROOT, check=True, capture_output=True)
    return json.loads(out.read_text())


def test_all_items_have_scores_in_range(tmp_path):
    items = build(tmp_path)["items"]
    assert len(items) == 60
    for x in items:
        assert 0 <= x["total"] <= 100
        assert 0 <= x["quality"] <= 100


def test_pack_prices_follow_unit_price(tmp_path):
    for x in build(tmp_path)["items"]:
        if x["best100"]:
            assert x["p300"] == round(x["best100"] * 3)
            assert x["p1500"] == round(x["best100"] * 15)


def test_best_shop_is_cheapest_in_stock(tmp_path):
    for x in build(tmp_path)["items"]:
        stocked = {k: v["unit100"] for k, v in x["shops"].items() if v["in_stock"]}
        if stocked:
            assert x["best100"] == min(stocked.values())
