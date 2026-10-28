"""Every slot and every table cell of every core skill, read from the tools by the golden harness, equals its
independent oracle (tests/oracles) on the demo database."""

from __future__ import annotations

import golden
import pytest
from oracles import Oracle, module, same


@pytest.mark.parametrize("name", golden.names())
def test_every_slot_and_table_has_an_oracle(name):
    spec = golden.load(name)["spec"]
    mod = module(name)
    assert set(mod.SLOTS) == set(spec.get("slots", {})), "SLOTS must cover exactly the slots of spec.json"
    assert set(mod.TABLES) == set(spec.get("tables", {})), "TABLES must cover exactly the tables of spec.json"


@pytest.mark.parametrize("name", golden.names())
def test_slots_and_tables_equal_their_oracle(name, oracle_problems):
    bad = oracle_problems[name]
    assert not bad, "\n".join(bad)


def test_oracles_catch_a_wrong_field(demo, rendered):
    """A column read from the wrong field (actual units shown as planned) is caught."""
    name = "resource-wbs-summary"
    _skill, _text, results, _raw, args = rendered[name]
    spec = golden.load(name)["spec"]
    next(c for c in spec["tables"]["resources"]["columns"] if c["key"] == "planned")["path"] = "actual_qty"
    got = golden.table_rows(spec, results)["resources"]
    o = Oracle(demo["db"], demo["work"], args)
    try:
        want = module(name).TABLES["resources"](o)
    finally:
        o.close()
    assert any(same(g["planned"], w["planned"], "n1") for g, w in zip(got, want, strict=True))
