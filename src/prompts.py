"""Prompt builders shared by the notebooks and tools/seed_replay_cache.py.
A notebook replays a recorded response only if it sends exactly the messages built here."""
import json
VOCAB = ["revenue", "revenue_growth", "gross_margin", "ebitda", "adjusted_ebitda", "ebitda_margin", "arr", "nrr",
         "gross_logo_churn", "top1_customer_share", "top10_customer_share", "headcount"]
J = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"))

def claims_messages(block_text):
    return [{"role": "system", "content": "You extract numeric management claims from confidential deal documents. For every numeric claim, return "
             "metric (one of: " + ", ".join(VOCAB) + "), value, unit, scale, period, qualifier and the exact quote. Express percentages as "
             "fractions (32% is 0.32, unit pct, scale 1). Never add a number the text does not state."},
            {"role": "user", "content": block_text}]

ANSWER_RULES = ("You answer questions about a private deal for a private-equity associate. Answer as a list of one-sentence claims. "
                "Every number must equal a provided fact and carry its fact_id; a management claim may instead carry a claim_id and must be "
                "labelled 'management claim'. Never use numbers from your own knowledge. If the evidence is insufficient, abstain and give a reason "
                "that starts with 'Not disclosed'.")

def answer_messages(question, facts, claims, evidence):
    payload = {"question": question,
               "facts": [{k: f[k] for k in ("fact_id", "metric", "period", "value", "unit", "tier")} for f in facts],
               "management_claims": [{k: c[k] for k in ("claim_id", "metric", "period_label", "value_abs")} for c in claims],
               "evidence": [{k: e[k] for k in ("doc_id", "block_id", "tier", "text")} for e in evidence]}
    return [{"role": "system", "content": ANSWER_RULES}, {"role": "user", "content": J(payload)}]

def regenerate_messages(messages, draft_json, bad_numbers):
    fb = (f"Your answer contained numbers that do not match the referenced facts or claims: {sorted(bad_numbers)}. "
          "Use only numbers from the facts provided, or label a management claim as such with its claim_id.")
    return messages + [{"role": "assistant", "content": draft_json}, {"role": "user", "content": fb}]

def profile_single_messages(cim_text):
    return [{"role": "system", "content": "Fill the DealProfile from this confidential information memorandum in a single pass. "
             "Cite every KPI with doc_id, block_id, tier and page."}, {"role": "user", "content": cim_text}]

def scorer_messages(rows):
    return [{"role": "system", "content": "For each deal, estimate the probability that it advances to the investment committee. "
             "Return one probability between 0 and 1 per deal_id."}, {"role": "user", "content": J(rows)}]

def judge_messages(items):
    return [{"role": "system", "content": "For each item, decide whether the cited text supports the claim. Return supported true or false per item_id."},
            {"role": "user", "content": J(items)}]
