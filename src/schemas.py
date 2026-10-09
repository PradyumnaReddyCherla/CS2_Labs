"""Response models (Tool Tutorial Part 2): claim extraction (Lab 14), the answer schema with its
reference rules (Lab 18), the deal profile (Lab 14 cont.), and small models for Labs 21-22."""
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator

class MgmtClaim(BaseModel):                       # Lab 14
    metric: str = Field(description="vocab metric name")
    value: float
    unit: Literal["USD", "pct", "count", "ratio"]
    scale: Literal[1, 1_000, 1_000_000, 1_000_000_000]
    period: str = Field(description="e.g. FY2025, LTM")
    qualifier: Literal["reported", "adjusted", "run-rate", "pro forma", "LTM", "FY"]
    quote: str = Field(description="exact source span")

class MgmtClaims(BaseModel):
    claims: list[MgmtClaim]

class Citation(BaseModel):                        # Lab 18
    doc_id: str; block_id: str; tier: int
    page: Optional[int] = None     # None: HTML, xlsx

class Number(BaseModel):
    value: float; unit: str
    fact_id: Optional[str] = None    # tiers 1-3
    calc_id: Optional[str] = None    # derived
    claim_id: Optional[str] = None   # tiers 4-5
    @model_validator(mode="after")
    def one_reference(self):
        refs = (self.fact_id, self.calc_id, self.claim_id)
        if sum(r is not None for r in refs) != 1:
            raise ValueError("exactly one reference")
        return self

class Claim(BaseModel):
    text: str
    numbers: list[Number]
    citations: list[Citation]
    tier_label: Literal["filed", "seller", "management claim", "web"]
    @model_validator(mode="after")
    def claim_ids_need_a_label(self):
        ok = ("management claim", "web")
        uses = any(n.claim_id for n in self.numbers)
        if uses and self.tier_label not in ok:
            raise ValueError("claim_id needs a claim label")
        return self

class Answer(BaseModel):
    claims: list[Claim]
    abstained: bool = False
    abstain_reason: Optional[str] = None

class KPI(BaseModel):                             # Lab 14 (cont.)
    name: str; value: float; unit: str
    period: str; source: Citation  # where, and its tier

class Customer(BaseModel):
    name: str; revenue_share: float; period: str

class DealProfile(BaseModel):
    overview: str
    business_model: str
    revenue_history: list[KPI]
    ebitda_history: list[KPI]
    kpis: list[KPI]
    top_customers: list[Customer]
    management: list[str]
    stated_addbacks: list[KPI]
    process_terms: str
    disclosure_gaps: list[str]   # "Not disclosed."

class DealScore(BaseModel):                       # Lab 21: LLM-as-scorer
    deal_id: str; p: float

class Scores(BaseModel):
    scores: list[DealScore]

class SupportLabel(BaseModel):                    # Lab 22: LLM-as-judge
    item_id: str; supported: bool

class JudgeLabels(BaseModel):
    labels: list[SupportLabel]
