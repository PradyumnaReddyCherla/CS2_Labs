import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.schemas import Answer
from src.llm.client import MODE
from src import sample_data as sd
facts = {f["fact_id"]: f for f in sd.seller_facts()}
def grounded_answer(question, scope):
    return Answer(claims=[], abstained=True, abstain_reason="Not disclosed: wire in the notebook-18 pipeline here.")
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="LANTERN QA")
ALLOWED_SCOPES = {"deal_a", "deal_b", "kestrel", "public"}

class Ask(BaseModel):
    question: str
    scope: str                   # required, no default

@app.post("/answer", response_model=Answer)
def answer(req: Ask) -> Answer:
    if req.scope not in ALLOWED_SCOPES:
        raise HTTPException(400, "unknown scope")
    # grounded_answer: retrieve, generate, lint, cite
    return grounded_answer(req.question, req.scope)
@app.get("/facts/{fact_id}")        # and /calc/{calc_id}
def fact(fact_id: str):
    if fact_id not in facts:
        raise HTTPException(404, "unknown fact")
    return facts[fact_id]
@app.get("/health")
def health():
    return {"ok": True, "llm_mode": MODE}