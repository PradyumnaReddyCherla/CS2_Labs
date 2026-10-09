"""Seed data/llm_cache and data/embed_cache from data/llm_fixtures, so every notebook runs in replay
mode with no API key. Run once after installing requirements:  python tools/seed_replay_cache.py
Keys are computed here, with your installed pydantic, exactly as llm.structured computes them."""
import json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
os.environ["LANTERN_LLM_MODE"] = "record"            # embeddings below are computed and saved
from src.llm import client as llm
from src import schemas, prompts
from src.sample_data import records, seller_facts, claim_rows, evidence_for, dev_tasks, cim_text, test_split, deal_log
from src import sample_lsa
import csv
FX = {p.stem: json.load(open(p)) for p in sorted((ROOT / "data/llm_fixtures").glob("*.json"))}
llm.CACHE.mkdir(parents=True, exist_ok=True); llm.EMB.mkdir(parents=True, exist_ok=True)
def validated(fx):
    return getattr(schemas, fx["response_model"]).model_validate(fx["response"])
blocks = {f'{r["doc_id"]}:{r["block_id"]}': r for r in records("deal_a")}
extracted = {n.split("_", 1)[1]: validated(f) for n, f in FX.items() if n.startswith("claims_")}
CLAIMS, FACTS, TASKS = claim_rows(extracted), seller_facts(), dev_tasks()
def build(fx):
    a = fx["args"]
    if fx["builder"] == "claims_messages": return prompts.claims_messages(blocks[a["block"]]["text"])
    if fx["builder"] == "answer_messages":
        t = TASKS[a["task_id"]]; return prompts.answer_messages(t["turns"][0]["content"], FACTS, CLAIMS, evidence_for(a["task_id"]))
    if fx["builder"] == "regenerate_messages":
        t = TASKS[a["task_id"]]; base = prompts.answer_messages(t["turns"][0]["content"], FACTS, CLAIMS, evidence_for(a["task_id"]))
        return prompts.regenerate_messages(base, validated(FX[a["draft"]]).model_dump_json(), a["bad_numbers"])
    if fx["builder"] == "profile_single_messages": return prompts.profile_single_messages(cim_text())
    if fx["builder"] == "scorer_messages":
        Xtr, Xte, *_ = test_split(); log = deal_log()
        rows = [{"deal_id": log.loc[i, "deal_id"], **{c: float(Xte.loc[i, c]) for c in Xte.columns}} for i in list(Xte.index[:a["n"]])]
        return prompts.scorer_messages(rows)
    if fx["builder"] == "judge_messages":
        items = [{"item_id": r["item_id"], "claim": r["claim"], "cited_text": r["cited_text"]} for r in csv.DictReader(open("data/eval/judge_items.csv"))]
        return prompts.judge_messages(items)
    raise ValueError(fx["builder"])
n = 0
for name, fx in FX.items():
    cls = getattr(schemas, fx["response_model"]); model = llm.P["llm"]["models"][fx["model_role"]]
    key = llm.cache_key(llm.PROVIDER, model, build(fx), schema=cls.model_json_schema())
    (llm.CACHE / f"{key}.json").write_text(validated(fx).model_dump_json()); n += 1
qrels = [json.loads(l)["query"] for l in open("data/eval/qrels.jsonl")]
texts = sample_lsa.corpus() + qrels + ["customer concentration", "change of control"]
llm.embed(texts, sample_lsa.MODEL, compute=sample_lsa.encode)
print(f"seeded {n} model responses into {llm.CACHE} and {len(set(texts))} embeddings into {llm.EMB}")
