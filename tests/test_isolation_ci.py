"""The CI pattern from Case Study 2 Part 3: CI has no DVC access, so the isolation test runs on a tiny
committed fixture (two toy deals with planted canaries). Run the same test on your full index locally."""
import json, os
from pathlib import Path
import pytest
ROOT = Path(os.environ.get("LANTERN_ISOLATION_FIXTURE", "tests/fixtures/isolation"))
CHUNKS = json.load(open(ROOT / "chunks.json"))
QUERIES = [json.loads(l) for l in open(ROOT / "eval/qrels.jsonl")]
CANARIES_B = json.load(open(ROOT / "dataroom/canaries_visible.json"))["deal_b"]

def retrieve(query, scope, k=10):
    """Toy lexical retriever with the scope filter applied before ranking."""
    if not scope: raise ValueError("scope is required")
    q = set(query.lower().split())
    pool = [c for c in CHUNKS if c["deal_id"] in (scope, "public")]
    return sorted(pool, key=lambda c: -len(q & set(c["text"].lower().split())))[:k]

@pytest.mark.parametrize("q", QUERIES)
def test_deal_a_never_sees_deal_b(q):
    for c in retrieve(q["query"], scope="deal_a"):
        assert c["deal_id"] in ("deal_a", "public")
        assert not any(x in c["text"] for x in CANARIES_B)

def test_scope_is_required():
    with pytest.raises(ValueError):
        retrieve("revenue", scope="")
