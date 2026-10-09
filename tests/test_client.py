"""The course client in replay: seeded responses hit, an unrecorded prompt misses, the budget cap holds."""
import json
import pytest
from src.llm import client as llm
from src import schemas, prompts, sample_data as sd

def test_replay_hit_for_a_seeded_extraction():
    blocks = {r["block_id"]: r for r in sd.records("deal_a") if r["doc_id"] == "DR-deal_a-001"}
    out = llm.structured(schemas.MgmtClaims, prompts.claims_messages(blocks["p0003_b002"]["text"]), llm.P["llm"]["models"]["large"])
    assert out.claims[0].metric == "nrr" and abs(out.claims[0].value - 1.18) < 1e-9

def test_replay_miss_raises():
    if llm.MODE != "replay": pytest.skip("replay-mode test")
    with pytest.raises(RuntimeError, match="cache miss"):
        llm.structured(schemas.MgmtClaims, prompts.claims_messages("never recorded"), llm.P["llm"]["models"]["large"])

def test_budget_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "LEDGER", str(tmp_path / "ledger.jsonl")); monkeypatch.setattr(llm, "CAP", 0.001)
    model = llm.P["llm"]["models"]["large"]
    llm.ledger(model, 1000, 300, "test")
    with pytest.raises(llm.BudgetExceeded):
        llm.budget_check(model, 100000)
