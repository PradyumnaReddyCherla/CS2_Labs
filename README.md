# Project LANTERN · Lab 2 Starter Kit

**DAMG 7245 · Tool Tutorial Part 2 (Labs 12–22) · Fall 2026**

This repository is your sandbox for the Part 2 tutorial. It contains:

- **one Jupyter notebook per lab**, running the slides' code on real files;
- **a small classroom deal**, Project Wren (`deal_a`), and its rival, Project Heron (`deal_b`);
- **the course LLM client** (`src/llm/client.py`);
- **recorded model responses**, so every notebook runs in **replay mode with no API key**.

The directory layout is Case Study 2's, so the slide code runs unchanged.

Project Wren is fictional and small. It is **not** your graded variant: your Deal A, Deal B and the Kestrel practice deal arrive with Case Study 2.

---

## Quick start (about 10 minutes)

```bash
python3.11 -m venv .venv && source .venv/bin/activate     # Windows: use WSL, or .venv\Scripts\activate
pip install -r requirements.txt
python tools/seed_replay_cache.py                          # builds the replay cache on your machine
jupyter lab notebooks                                      # open 00_setup_and_client.ipynb and run it first
```

With `make`: `make setup`, then `make lab`; after setup, `make` uses `.venv` automatically. To check everything: `make check`, which runs the tests and every notebook.

## Which notebook goes with which lab

| Notebook | Lab and slides |
|---|---|
| `00_setup_and_client` | Orientation: record/replay, parts 1–4 (run first) |
| `12_ingestion_at_scale` | Lab 12: submissions API, companyfacts, value-tiered routing, the synthetic-web crawl |
| `13_fact_store` | Lab 13: the DuckDB fact table, xlsx facts with cell citations, XBRL citations |
| `14_claims_and_reconciliation` | Lab 14: claim extraction, period alignment, reconciliation scored against the answer key |
| `15_chunking_and_embeddings` | Lab 15: block-aware, section-aware and recursive chunking; cached embeddings |
| `16_hybrid_retrieval` | Lab 16: Chroma with scope in the store, BM25, reciprocal rank fusion |
| `17_retrieval_evaluation` | Lab 17: recall, MRR, nDCG; the isolation test, and proving it has teeth |
| `18_grounded_qa` | Lab 18: the answer schema, the numeric-claim linter, regeneration, abstention, the FastAPI service |
| `19_deal_profile_and_memo` | Lab 14 (cont.): single-prompt versus staged extraction with bootstrap intervals; the screening memo |
| `20_comps_and_figures` | Labs 19–20: LTM and EV calculators with traces, comps quartiles, chart versus table |
| `21_calibrated_scoring` | Lab 21: a calibrated model versus an LLM asked for a probability |
| `22_evaluation_and_economics` | Lab 22: citation precision and recall, judge agreement (κ), unit economics |

Run the notebooks in order: 18 writes the answers that 22 evaluates. Each notebook ends with the slide's exercise.

## Replay, record and live

- **Replay** (default, `llm.mode: replay` in `params.yaml`): every model call is served from `data/llm_cache/`. A prompt nobody recorded raises an error naming the missing key. No key, no network, no cost.
- **Record** (`export LANTERN_LLM_MODE=record`): makes the call, then caches it. Needs `pip install instructor openai` and `OPENAI_API_KEY`.
  - Every live call is costed in `logs/cost_ledger.jsonl` from `llm.prices`.
  - Calls stop at `budget.usd_cap_total`.
  - Update `llm.prices` from your provider's page first.
- **Embeddings:** in class we use `lsa-sample-v1`, an offline TF-IDF model seeded into the cache. Case Study 2 requires one hosted and one open model: install `sentence-transformers`, switch to record mode, and embed with your open model.

## What carries over to your Case Study 2 repository

| Copy | Do not copy |
|---|---|
| `src/llm/client.py` (it is the slides' code) | Anything in `data/`: it is the classroom sample, not your variant |
| The `params.yaml` keys, with your own values | The recorded fixtures and caches |
| `tests/test_isolation_ci.py`, as the pattern for your CI isolation test | |

For your CS2 repository, install the package list on the tutorial's "Environment setup" slide; it adds `instructor`, a provider SDK and `sentence-transformers` for live calls and open embeddings.

**The notebooks teach; your Case Study 2 code is your own work.** The pieces CS2 grades (fact store, reconciliation, retrieval, linter, service, evaluation) start from the slides, but you build them in your repository, on your variant, and they must meet the CS2 acceptance criteria.

## Repository map

```
params.yaml                  CS2 Appendix B keys, classroom values
src/llm/client.py            the course LLM client (slides, parts 1-4) + live adapter
src/schemas.py               response models: claims, answer schema with validators, deal profile
src/prompts.py               prompt builders shared by notebooks and the seeder
src/sample_data.py           loaders for the classroom sample
data/dataroom/deal_a|deal_b  data rooms (raw PDFs, xlsx, transcript, scanned contract) + CS1-style records
data/dataroom/variant.json   archetype, synthetic-web host, sitemap URL (as your real variant will)
data/reference/              deal log with true probabilities, prices, comps facts, human-minute baselines
data/eval/qrels.jsonl        sample relevance judgments; evals/tasks/dev.jsonl sample Q&A tasks
data/llm_fixtures/           recorded model responses; tools/seed_replay_cache.py turns them into the cache
notebooks/                   one per lab
tests/                       client, sample integrity, and the CI isolation pattern
```

## Troubleshooting

- **"cache miss" in replay:** run `python tools/seed_replay_cache.py`. If you changed a prompt or a schema, the recorded response no longer matches; switch to record mode or restore the original.
- **`chromadb` fails to install:** upgrade pip (`pip install -U pip`) and use Python 3.11.
- **Re-running cells:** notebooks 13, 16 and 17 reset their database or collection before rebuilding, so re-running in the same session is safe.
- **Notebook 22 says to run notebook 18 first:** it evaluates the answers notebook 18 writes to `outputs/qa/`.
