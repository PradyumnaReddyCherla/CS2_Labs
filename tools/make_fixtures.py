"""Write the recorded model responses for the classroom sample to data/llm_fixtures/.
Each fixture stores the response plus the recipe (builder + args) for its prompt, not a cache key:
tools/seed_replay_cache.py rebuilds the prompt and computes the key in the student's environment."""
import csv, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import os; os.chdir(ROOT)
from src.sample_data import fact_id, claim_id, XLSX_DOC, test_split
OUT = ROOT / "data/llm_fixtures"; OUT.mkdir(parents=True, exist_ok=True)
F = lambda m, p: fact_id("deal_a", m, p, XLSX_DOC)
def cit(doc, block, tier, page=None): return {"doc_id": doc, "block_id": block, "tier": tier, "page": page}
def mc(metric, value, unit, scale, period, qualifier, quote): return {"metric": metric, "value": value, "unit": unit, "scale": scale, "period": period, "qualifier": qualifier, "quote": quote}
fx = []
claims = {"p0002_b001": [mc("revenue_growth", 0.32, "pct", 1, "FY2025", "reported", "Revenue grew 32% in FY2025"), mc("revenue", 41.2, "USD", 1_000_000, "FY2025", "reported", "to $41.2 million")],
          "p0002_b002": [mc("revenue", 48.0, "USD", 1_000_000, "FY2025", "run-rate", "On a run-rate basis, revenue reached $48.0 million")],
          "p0002_b003": [mc("revenue", 43.5, "USD", 1_000_000, "CY2025", "reported", "Calendar-year 2025 revenue is expected to reach $43.5 million")],
          "p0003_b001": [mc("top1_customer_share", 0.08, "pct", 1, "FY2025", "reported", "no single customer represents more than 8% of revenue")],
          "p0003_b002": [mc("nrr", 1.18, "pct", 1, "FY2025", "reported", "Net revenue retention was 118% in FY2025")]}
for b, cl in claims.items():
    fx.append({"name": f"claims_{b}", "response_model": "MgmtClaims", "model_role": "large", "builder": "claims_messages", "args": {"block": f"DR-deal_a-001:{b}"}, "response": {"claims": cl}})
fx.append({"name": "answer_dev-w-01", "response_model": "Answer", "model_role": "large", "builder": "answer_messages", "args": {"task_id": "dev-w-01"},
           "response": {"claims": [{"text": "Wren's FY2025 revenue was $41.2 million, per seller financials.", "numbers": [{"value": 41200000.0, "unit": "USD", "fact_id": F("revenue", "FY2025")}],
                                    "citations": [cit(XLSX_DOC, "P&L!D2", 3)], "tier_label": "seller"}], "abstained": False, "abstain_reason": None}})
draft = {"claims": [{"text": "Net revenue retention was 118% in FY2025.", "numbers": [{"value": 1.18, "unit": "pct", "fact_id": F("nrr", "FY2025")}],
                     "citations": [cit("DR-deal_a-001", "p0003_b002", 4, 3)], "tier_label": "seller"}], "abstained": False, "abstain_reason": None}
fx.append({"name": "answer_dev-w-02_draft", "response_model": "Answer", "model_role": "large", "builder": "answer_messages", "args": {"task_id": "dev-w-02"}, "response": draft})
fx.append({"name": "answer_dev-w-02_regen", "response_model": "Answer", "model_role": "large", "builder": "regenerate_messages",
           "args": {"task_id": "dev-w-02", "draft": "answer_dev-w-02_draft", "bad_numbers": [118.0]},
           "response": {"claims": [{"text": "Net revenue retention was 109% in FY2025, per seller financials.", "numbers": [{"value": 1.09, "unit": "pct", "fact_id": F("nrr", "FY2025")}],
                                    "citations": [cit(XLSX_DOC, "KPIs!B3", 3)], "tier_label": "seller"},
                                   {"text": "Per the CIM (unverified), net revenue retention was 118%, which management calls its best quarter annualized.",
                                    "numbers": [{"value": 1.18, "unit": "pct", "claim_id": claim_id("DR-deal_a-001", "p0003_b002", 0)}],
                                    "citations": [cit("DR-deal_a-001", "p0003_b002", 4, 3)], "tier_label": "management claim"}], "abstained": False, "abstain_reason": None}})
fx.append({"name": "answer_dev-w-04", "response_model": "Answer", "model_role": "large", "builder": "answer_messages", "args": {"task_id": "dev-w-04"},
           "response": {"claims": [], "abstained": True, "abstain_reason": "Not disclosed: the data room does not include an FY2026 budget."}})
k = lambda name, value, unit, period, block, page: {"name": name, "value": value, "unit": unit, "period": period, "source": cit("DR-deal_a-001", block, 4, page)}
fx.append({"name": "profile_single", "response_model": "DealProfile", "model_role": "large", "builder": "profile_single_messages", "args": {},
           "response": {"overview": "Wren Freight Software sells dispatch, pricing and settlement software to 1,240 mid-sized freight brokers; HQ Columbus, Ohio; founded 2014.",
                        "business_model": "Subscription software for freight brokers.",
                        "revenue_history": [k("revenue", 26.4e6, "USD", "FY2023", "p0004_b001", 4), k("revenue", 33.07e6, "USD", "FY2024", "p0004_b001", 4), k("revenue", 41.2e6, "USD", "FY2025", "p0004_b001", 4)],
                        "ebitda_history": [k("adjusted_ebitda", 9.9e6, "USD", "FY2025", "p0004_b001", 4)],
                        "kpis": [k("revenue_growth", 0.32, "pct", "FY2025", "p0002_b001", 2), k("nrr", 1.18, "pct", "FY2025", "p0003_b002", 3)],
                        "top_customers": [{"name": "Largest customer (not named)", "revenue_share": 0.08, "period": "FY2025"}],
                        "management": ["Dana Whitfield, Chief Executive Officer", "Marcus Oyelaran, Chief Financial Officer"],
                        "stated_addbacks": [k("implementation_costs", 1.6e6, "USD", "FY2025", "p0004_b002", 4), k("founder_compensation", 0.8e6, "USD", "FY2025", "p0004_b002", 4)],
                        "process_terms": "Indications of interest due November 20, 2026.", "disclosure_gaps": ["FY2026 budget: Not disclosed."]}})
Xtr, Xte, ytr, yte, ptr, pte = test_split()
rng = np.random.default_rng(11); ids = list(Xte.index)
from src.sample_data import deal_log
log = deal_log()
# The "LLM" sees only the features (as a real model would), reads growth and margin, rounds to 0.1 and is overconfident
scores = [{"deal_id": log.loc[i, "deal_id"], "p": float(np.clip(round(0.45 + 2.2 * (Xte.loc[i, "growth"] - 0.15) + 1.8 * (Xte.loc[i, "ebitda_margin"] - 0.18) + rng.normal(0, 0.12), 1), 0.05, 0.95))} for i in ids]
fx.append({"name": "scorer_test", "response_model": "Scores", "model_role": "large", "builder": "scorer_messages", "args": {"n": len(ids)}, "response": {"scores": scores}})
items = [("j01", "FY2025 revenue was $41.2 million.", "Revenue | 26.4 | 33.07 | 41.2", 1, 1, True), ("j02", "Revenue grew 32% in FY2025.", "Revenue | 26.4 | 33.07 | 41.2", 0, 0, False),
         ("j03", "NRR was 109% in FY2025.", "Net revenue retention | 1.09", 1, 1, True), ("j04", "NRR was 118% in FY2025.", "Net revenue retention | 1.09", 0, 0, False),
         ("j05", "The largest customer is 14.5% of revenue.", "Northline Logistics LLC | 0.145", 1, 1, True), ("j06", "No customer exceeds 8% of revenue.", "Northline Logistics LLC | 0.145", 0, 0, False),
         ("j07", "The fiscal year ends June 30.", "Fiscal year ends June 30.", 1, 1, True), ("j08", "Adjusted EBITDA was $9.9 million.", "Adjusted EBITDA | 6.0 | 7.9 | 9.9", 1, 1, True),
         ("j09", "EBITDA was $9.9 million.", "EBITDA | 5.1 | 6.4 | 7.5", 0, 0, False), ("j10", "Two contracts need consent on a change of control.", "Two enterprise contracts require consent on a change of control.", 1, 1, True),
         ("j11", "The CFO joined in 2021.", "Chief Financial Officer Marcus Oyelaran, who joined in 2021", 1, 1, True), ("j12", "Wren serves 1,240 brokers.", "Wren serves 1,240 brokerage customers.", 1, 1, True),
         ("j13", "IOIs are due November 20, 2026.", "Indications of interest are due on November 20, 2026.", 1, 1, True), ("j14", "Wren is headquartered in Chicago.", "headquartered in Columbus, Ohio", 0, 0, False),
         ("j15", "Gross logo churn was 7%.", "Gross logo churn | 0.07", 1, 1, True), ("j16", "Revenue grew about 25% in FY2025.", "Revenue | 26.4 | 33.07 | 41.2", 1, 0, True),
         ("j17", "ARR is $48.0 million.", "ARR (USD millions) | 48.0", 1, 1, True), ("j18", "FY2025 revenue was $48.0 million.", "Revenue | 26.4 | 33.07 | 41.2", 0, 0, False),
         ("j19", "Annual fees in the Northline contract are $5.97 million.", "Annual fees: $5,970,000.", 1, 1, True), ("j20", "The contract term is 24 months.", "Term: 36 months", 0, 1, True)]
with open(ROOT / "data/eval/judge_items.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["item_id", "claim", "cited_text", "human_a", "human_b"])
    for it in items: w.writerow(it[:5])
fx.append({"name": "judge_20", "response_model": "JudgeLabels", "model_role": "judge", "builder": "judge_messages", "args": {},
           "response": {"labels": [{"item_id": it[0], "supported": it[5]} for it in items]}})
for f in fx: json.dump(f, open(OUT / f"{f['name']}.json", "w"), indent=1)
print(f"{len(fx)} fixtures written to {OUT}")
