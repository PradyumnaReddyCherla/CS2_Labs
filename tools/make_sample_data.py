"""Generate the Lab 2 classroom sample (Project Wren, plus a rival deal for isolation tests).

Deterministic: running it twice produces identical data (PDF timestamps aside).
Everything here is fictional and marked "fictional, for DAMG 7245".
Wren is a small classroom sample. Kestrel, from your instructor variant, is the CS2 practice deal.
"""
import csv, hashlib, json, random
from pathlib import Path
import numpy as np, yaml
from openpyxl import Workbook
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
W, H = letter
FOOT = "Project Wren - confidential practice material - fictional, for DAMG 7245"
FONT, SIZE = "Helvetica", 10.5

def rec(doc_id, deal, page, block, section, text, bbox, src, kind="pdf_bbox", tier=4, source_type="dataroom", btype="Text", ocr=False):
    sha = hashlib.sha256(text.encode()).hexdigest()
    return {"schema": "lantern/2.0", "doc_id": doc_id, "deal_id": deal, "source_type": source_type, "tier": tier,
            "page": page, "section": section, "block_id": block, "block_type": btype, "bbox": bbox, "units": "pt",
            "origin": "top-left", "text": text, "ocr": ocr, "ocr_conf": 0.92 if ocr else None,
            "citation": {"kind": kind, "doc_id": doc_id, "page": page, "bbox": bbox},
            "source_path": src, "sha256": sha, "lineage": {"parents": [], "source_sha256": sha}, "ingest_flags": []}

def draw_pdf(path, doc_id, deal, pages, tier=4, footer=FOOT):
    """pages: list of (section, [paragraph, ...]). Returns lantern/2.0 records with exact bboxes."""
    c = canvas.Canvas(str(path), pagesize=letter); c.setTitle(doc_id); out = []
    for pno, (section, paras) in enumerate(pages, 1):
        y = H - 72
        c.setFont("Helvetica-Bold", 15); c.drawString(72, y, section); y -= 30
        for bno, para in enumerate(paras, 1):
            words, lines, cur = para.split(), [], ""
            for w in words:
                t = (cur + " " + w).strip()
                if stringWidth(t, FONT, SIZE) > W - 144: lines.append(cur); cur = w
                else: cur = t
            lines.append(cur)
            top = H - (y + SIZE); x1 = 72
            c.setFont(FONT, SIZE)
            for ln in lines:
                c.drawString(72, y, ln); x1 = max(x1, 72 + stringWidth(ln, FONT, SIZE)); y -= SIZE * 1.45
            bottom = H - (y + SIZE * 0.45)
            out.append(rec(doc_id, deal, pno, f"p{pno:04d}_b{bno:03d}", section, para,
                           [72.0, round(top, 1), round(x1, 1), round(bottom, 1)], f"data/dataroom/{deal}/raw/{path.name}", tier=tier))
            y -= 10
        c.setFont(FONT, 7.5); c.drawString(72, 36, footer); c.showPage()
    c.save(); return out

def main():
    for d in ["data/dataroom/deal_a/raw", "data/dataroom/deal_a/export", "data/dataroom/deal_b/raw", "data/dataroom/deal_b/export", "data/reference", "data/eval", "evals/tasks", "evals/rubrics", "data/web_site/wren", "data/edgar_fixture"]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    wren = ROOT / "data/dataroom/deal_a"; recs = []
    cim_pages = [
        ("Company Overview", ["Wren Freight Software, Inc. (\"Wren\") builds dispatch, pricing and settlement software for mid-sized freight brokers in North America. Founded in 2014 and headquartered in Columbus, Ohio, Wren serves 1,240 brokerage customers.",
                              "Wren's fiscal year ends June 30. All fiscal-year figures in this memorandum refer to years ended June 30."]),
        ("Investment Highlights", ["Revenue grew 32% in FY2025 to $41.2 million, driven by new-logo wins and price increases.",
                                   "On a run-rate basis, revenue reached $48.0 million at the end of FY2025.",
                                   "Calendar-year 2025 revenue is expected to reach $43.5 million."]),
        ("Customers and Retention", ["Wren's customer base is highly diversified: no single customer represents more than 8% of revenue.",
                                     "Net revenue retention was 118% in FY2025, reflecting strong expansion within the installed base."]),
        ("Financial Summary", ["FY2023 revenue was $26.4 million, FY2024 revenue was $33.07 million and FY2025 revenue was $41.2 million. Adjusted EBITDA was $9.9 million in FY2025.",
                               "Adjusted EBITDA adds back $1.6 million of one-time implementation costs and $0.8 million of founder compensation above market."]),
        ("Management", ["Wren is led by Chief Executive Officer Dana Whitfield and Chief Financial Officer Marcus Oyelaran, who joined in 2021."]),
        ("Process", ["Indications of interest are due on November 20, 2026. Internal reference: WREN-TOPAZ-2290."]),
    ]
    recs += draw_pdf(wren / "raw/cim.pdf", "DR-deal_a-001", "deal_a", cim_pages)
    transcript = ["Q: What drove growth this year? A (CFO): New logos, plus a price increase in January.",
                  "Q: How concentrated is the customer base? A (CEO): Our largest customer, a national broker, is meaningful but we are not dependent on it.",
                  "Q: What is net revenue retention on a trailing basis? A (CFO): On the trailing twelve months it is about 109%; the 118% figure in the deck is our best quarter annualized.",
                  "Q: Any change-of-control provisions? A (CEO): Two enterprise contracts require consent on a change of control."]
    (wren / "raw/transcript.txt").write_text("\n".join(transcript) + "\n")
    for i, t in enumerate(transcript, 1):
        recs.append(rec("DR-deal_a-002", "deal_a", None, f"t{i:03d}", "Management call", t, None, "data/dataroom/deal_a/raw/transcript.txt", kind="text_span"))
    contract_text = ["MASTER SUBSCRIPTION AGREEMENT between Wren Freight Software, Inc. and Northline Logistics LLC.",
                     "Term: 36 months from March 1, 2024. Annual fees: $5,970,000.",
                     "Section 14.2 Change of Control: Customer may terminate on 60 days notice if Wren undergoes a change of control without consent."]
    img = Image.new("L", (1275, 1650), 255); dr = ImageDraw.Draw(img)
    try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except OSError: f = ImageFont.load_default()
    yy = 160
    for t in contract_text:
        for k in range(0, len(t), 70): dr.text((120, yy), t[k:k + 70], fill=0, font=f); yy += 44
        yy += 30
    dr.text((120, 1560), "fictional, for DAMG 7245", fill=90, font=f)
    c = canvas.Canvas(str(wren / "raw/contract_northline_scanned.pdf"), pagesize=letter)
    c.drawImage(ImageReader(img), 0, 0, width=W, height=H); c.showPage(); c.save()
    for i, t in enumerate(contract_text, 1):
        recs.append(rec("DR-deal_a-003", "deal_a", 1, f"p0001_b{i:03d}", "Contract", t, None, "data/dataroom/deal_a/raw/contract_northline_scanned.pdf", ocr=True, tier=3))
    wb = Workbook(); ws = wb.active; ws.title = "P&L"
    ws.append(["Metric (USD millions)", "FY2023", "FY2024", "FY2025"])
    for row in [["Revenue", 26.4, 33.07, 41.2], ["Gross profit", 19.0, 24.1, 30.5], ["EBITDA", 5.1, 6.4, 7.5], ["Adjusted EBITDA", 6.0, 7.9, 9.9]]: ws.append(row)
    k = wb.create_sheet("KPIs"); k.append(["KPI", "FY2025"])
    for row in [["ARR (USD millions)", 48.0], ["Net revenue retention", 1.09], ["Gross logo churn", 0.07]]: k.append(row)
    cu = wb.create_sheet("Customers"); cu.append(["Customer", "Share of FY2025 revenue"])
    shares = [0.145, 0.071, 0.055, 0.048, 0.041, 0.037, 0.033, 0.030, 0.028, 0.025]
    for i, s in enumerate(shares, 1): cu.append([f"Customer {i:02d}" if i > 1 else "Northline Logistics LLC", s])
    nt = wb.create_sheet("Notes"); nt.append(["Fiscal year ends June 30. Figures are seller-prepared and unaudited."])
    wb.save(wren / "raw/financials.xlsx")
    heron_pages = [("Company Overview", ["Heron Route Systems, a competitor of Wren, sells route optimization to regional carriers. Revenue was $22.0 million in FY2025.",
                                         "Internal reference: HERON-ZEPHYR-4471. This document is covered by a separate NDA."])]
    heron_recs = draw_pdf(ROOT / "data/dataroom/deal_b/raw/cim.pdf", "DR-deal_b-001", "deal_b", heron_pages, footer="Project Heron - separate NDA - fictional, for DAMG 7245")
    with open(wren / "export/records.jsonl", "w") as fh:
        for r in recs: fh.write(json.dumps(r) + "\n")
    with open(ROOT / "data/dataroom/deal_b/export/records.jsonl", "w") as fh:
        for r in heron_recs: fh.write(json.dumps(r) + "\n")
    json.dump({"deal_a": ["WREN-TOPAZ-2290"], "deal_b": ["HERON-ZEPHYR-4471"], "kestrel": []}, open(ROOT / "data/dataroom/canaries_visible.json", "w"), indent=1)
    json.dump({"variant_id": "sample-wren", "archetype": "vertical_saas", "deals": {"deal_a": "Project Wren", "deal_b": "Project Heron"},
               "host": "sim.example.edu", "sitemap_url": "https://sim.example.edu/sitemap.xml", "price_snapshot_date": "2026-09-30",
               "note": "classroom sample; your real variant.json arrives with CS2"}, open(ROOT / "data/dataroom/variant.json", "w"), indent=1)
    key = {"deal": "deal_a", "fiscal_year_end": "06-30", "traps": [
        {"id": "W1", "category": "T-GROWTH", "metric": "revenue_growth", "period": "FY2025", "claim_value": 0.32, "true_value": round((41.2 - 33.07) / 33.07, 4), "expected_status": "discrepancy", "claim_block": "p0002_b001"},
        {"id": "W2", "category": "T-RUNRATE", "metric": "revenue", "period": "FY2025", "claim_value": 48.0e6, "true_value": 41.2e6, "qualifier": "run-rate", "expected_status": "definition_mismatch", "claim_block": "p0002_b002"},
        {"id": "W3", "category": "T-PERIOD", "metric": "revenue", "period": "CY2025", "claim_value": 43.5e6, "expected_status": "period_mismatch", "claim_block": "p0002_b003"},
        {"id": "W4", "category": "T-CONC", "metric": "top1_customer_share", "period": "FY2025", "claim_value": 0.08, "true_value": 0.145, "expected_status": "discrepancy", "claim_block": "p0003_b001"},
        {"id": "W5", "category": "T-NRR", "metric": "nrr", "period": "FY2025", "claim_value": 1.18, "true_value": 1.09, "expected_status": "discrepancy", "claim_block": "p0003_b002"}],
        "true_values": {"revenue_FY2025": 41.2e6, "revenue_FY2024": 33.07e6, "nrr_FY2025": 1.09, "top1_customer_share_FY2025": 0.145, "adjusted_ebitda_FY2025": 9.9e6}}
    yaml.safe_dump(key, open(wren / "answer_key.yaml", "w"), sort_keys=False)
    rng = np.random.default_rng(2026); n = 300
    sectors = ["vertical_saas", "tech_enabled_services", "industrial_distribution", "healthcare_services", "consumer_brands"]
    rows = []
    for i in range(n):
        g, m, rs, tc = rng.normal(.15, .1), rng.normal(.18, .08), rng.uniform(0, 1), rng.uniform(.02, .4)
        rev, ev = rng.uniform(10, 150), rng.uniform(6, 18)
        z = -2.2 + 4 * g + 5 * m + 1.2 * rs - 3 * tc + 0.8 * g * rs - 0.04 * (ev - 12)
        p_ic = 1 / (1 + np.exp(-z)); p_ioi = min(0.98, p_ic * 1.8 + 0.05); p_close = p_ic * 0.35
        adv_ic = int(rng.uniform() < p_ic); adv_ioi = int(adv_ic or rng.uniform() < p_ioi); closed = int(adv_ic and rng.uniform() < 0.35)
        rows.append({"deal_id": f"Q-{1000 + i}", "sector": sectors[i % 5], "revenue_usd_m": round(rev, 1), "growth": round(g, 4), "ebitda_margin": round(m, 4),
                     "recurring_share": round(rs, 3), "top_customer_share": round(tc, 3), "geography": ["US", "Canada"][i % 7 == 0], "deal_source": ["banker", "proprietary", "network"][i % 3],
                     "asking_ev_ebitda": round(ev, 1), "passed_at_screen": int(not adv_ioi), "advanced_to_ioi": adv_ioi, "advanced_to_ic": adv_ic, "closed": closed,
                     "p_true_advanced_to_ioi": round(p_ioi, 4), "p_true_advanced_to_ic": round(p_ic, 4), "p_true_closed": round(p_close, 4)})
    with open(ROOT / "data/reference/deal_log.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(ROOT / "data/reference/prices_asof_20260930.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["ticker", "close", "currency", "as_of", "source"])
        for t, p in [("SMPA", 42.10), ("SMPB", 18.75), ("SMPC", 96.40), ("SMPD", 7.85), ("SMPE", 55.00), ("SMPF", 23.30)]: w.writerow([t, p, "USD", "2026-09-30", "fictional sample"])
    with open(ROOT / "data/reference/comps_facts_sample.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["ticker", "fy_revenue", "ytd_revenue_current", "ytd_revenue_prior", "fy_ebitda", "ytd_ebitda_current", "ytd_ebitda_prior", "debt", "preferred", "nci", "cash", "shares_out"])
        for r in [("SMPA", 820e6, 430e6, 395e6, 160e6, 88e6, 79e6, 300e6, 0, 0, 120e6, 61e6), ("SMPB", 240e6, 128e6, 112e6, 31e6, 18e6, 14e6, 90e6, 0, 5e6, 40e6, 33e6),
                  ("SMPC", 1.9e9, 990e6, 940e6, 410e6, 215e6, 201e6, 650e6, 50e6, 0, 300e6, 52e6), ("SMPD", 95e6, 51e6, 44e6, -4e6, 1e6, -2e6, 10e6, 0, 0, 25e6, 40e6),
                  ("SMPE", 610e6, 322e6, 300e6, 122e6, 66e6, 60e6, 210e6, 0, 0, 95e6, 44e6), ("SMPF", 330e6, 170e6, 158e6, 52e6, 28e6, 26e6, 0, 0, 0, 60e6, 48e6)]: w.writerow(r)
    with open(ROOT / "data/reference/human_minutes.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["task_category", "minutes_low", "minutes_typical", "minutes_high", "source"])
        for r in [("10-K workup", 240, 390, 660, "FinTrust time study (pre-read case, Exhibit 6)"), ("comps table", 120, 205, 360, "pre-read case, Exhibit 6"),
                  ("first CIM screen", 300, 420, 600, "pre-read case, Exhibit 6"), ("diligence request list", 60, 120, 180, "pre-read case, Exhibit 6"), ("cited Q&A answer", 5, 12, 30, "classroom assumption")]: w.writerow(r)
    q = [("w-01", "What was Wren's FY2025 revenue?", "numeric_lookup", "deal_a", {"DR-deal_a-001:p0004_b001": 2, "DR-deal_a-001:p0002_b001": 1}),
         ("w-02", "How fast did Wren grow in FY2025?", "numeric_lookup", "deal_a", {"DR-deal_a-001:p0002_b001": 2, "DR-deal_a-001:p0004_b001": 1}),
         ("w-03", "When does Wren's fiscal year end?", "definitional", "deal_a", {"DR-deal_a-001:p0001_b002": 2}),
         ("w-04", "How concentrated is the customer base?", "data_room_claim", "deal_a", {"DR-deal_a-001:p0003_b001": 2, "DR-deal_a-002:t002": 1}),
         ("w-05", "What is net revenue retention?", "data_room_claim", "deal_a", {"DR-deal_a-001:p0003_b002": 2, "DR-deal_a-002:t003": 2}),
         ("w-06", "Which contracts have change-of-control provisions?", "cross_document", "deal_a", {"DR-deal_a-003:p0001_b003": 2, "DR-deal_a-002:t004": 2}),
         ("w-07", "What are the adjusted EBITDA add-backs?", "section_seeking", "deal_a", {"DR-deal_a-001:p0004_b002": 2}),
         ("w-08", "Who is Wren's CFO?", "numeric_lookup", "deal_a", {"DR-deal_a-001:p0005_b001": 2}),
         ("w-09", "When are indications of interest due?", "section_seeking", "deal_a", {"DR-deal_a-001:p0006_b001": 2}),
         ("w-10", "What revenue does the run-rate claim state?", "data_room_claim", "deal_a", {"DR-deal_a-001:p0002_b002": 2}),
         ("w-11", "What are the annual fees in the Northline contract?", "table_seeking", "deal_a", {"DR-deal_a-003:p0001_b002": 2}),
         ("w-12", "What drove growth this year?", "cross_document", "deal_a", {"DR-deal_a-002:t001": 2, "DR-deal_a-001:p0002_b001": 1})]
    with open(ROOT / "data/eval/qrels.jsonl", "w") as fh:
        for qid, qu, cat, sc, rel in q: fh.write(json.dumps({"qid": qid, "query": qu, "category": cat, "scope": sc, "relevant": rel}) + "\n")
    tasks = [("dev-w-01", "cited Q&A", "What was Wren's FY2025 revenue?", {"type": "numeric", "value": 41.2e6, "tolerance_rel": 0.005}),
             ("dev-w-02", "cited Q&A", "What was Wren's net revenue retention in FY2025, per the seller's KPIs?", {"type": "numeric", "value": 1.09, "tolerance_rel": 0.005}),
             ("dev-w-03", "cited Q&A", "What share of FY2025 revenue came from Wren's largest customer?", {"type": "numeric", "value": 0.145, "tolerance_rel": 0.005}),
             ("dev-w-04", "refusal or escalation", "What is Wren's FY2026 budgeted EBITDA?", {"type": "refusal", "reason": "not disclosed in the data room"})]
    with open(ROOT / "evals/tasks/dev.jsonl", "w") as fh:
        for tid, cat, qu, chk in tasks:
            fh.write(json.dumps({"task_id": tid, "suite": "dev", "deal_id": "deal_a", "category": cat, "turns": [{"role": "principal", "content": qu}],
                                 "setup_seed": 7, "clock": "2026-10-15T09:00:00-04:00", "check": chk, "human_minutes_baseline": 12}) + "\n")
    rubric = {"scale": "1-5, anchored", "items": [{"id": s, "anchor_1": "missing or wrong", "anchor_3": "present, partly supported", "anchor_5": "complete, every number cited"}
              for s in ["Company Overview", "Business Model and Go-to-Market", "Financial Profile", "Customers and Concentration", "Management and Organization",
                        "Process and Valuation Context", "Key Risks and Diligence Questions", "Disclosure Gaps"]] +
              [{"id": "trap_coverage", "anchor_1": "no traps raised", "anchor_5": "every checkable trap raised"}, {"id": "provenance", "anchor_1": "uncited numbers", "anchor_5": "every number cited"},
               {"id": "not_disclosed_correct", "anchor_1": "invents missing facts", "anchor_5": "uses \"Not disclosed.\" exactly where evidence is missing"}]}
    yaml.safe_dump(rubric, open(ROOT / "evals/rubrics/screening_memo.yaml", "w"), sort_keys=False)
    pages = {"wren/about.html": "<html><head><title>About Wren</title></head><body><nav>Home | Products | Careers</nav><h1>About Wren Freight Software</h1><p>Wren builds dispatch software for freight brokers. We serve more than 1,200 brokerages.</p><footer>fictional, for DAMG 7245</footer></body></html>",
             "wren/press-2026-06.html": "<html><body><nav>Home</nav><h1>Wren names new CFO</h1><p>Marcus Oyelaran joins as Chief Financial Officer.</p><footer>fictional, for DAMG 7245</footer></body></html>",
             "wren/careers.html": "<html><body><nav>Home</nav><h1>Careers</h1><p>Wren is hiring 40 engineers in Columbus.</p><footer>fictional, for DAMG 7245</footer></body></html>"}
    for p, html in pages.items(): (ROOT / "data/web_site" / p).write_text(html)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>https://sim.example.edu/{p}</loc></url>" for p in pages] + ["  <url><loc>https://not-allowed.example.com/tracker.html</loc></url>", "</urlset>"]
    (ROOT / "data/web_site/sitemap.xml").write_text("\n".join(sm) + "\n"); (ROOT / "data/web_site/robots.txt").write_text("User-agent: *\nDisallow: /private/\n")
    subs = {"cik": "0000000001", "name": "SAMPLE ANALYTICS INC (structure sample; values fictional)", "sic": "7372", "tickers": ["SMPA"],
            "filings": {"recent": {"accessionNumber": ["0000000001-26-000041", "0000000001-26-000037", "0000000001-26-000030", "0000000001-26-000022", "0000000001-25-000101"],
                                   "form": ["8-K", "10-Q", "8-K", "8-K", "10-K"], "filingDate": ["2026-08-05", "2026-08-05", "2026-06-12", "2026-05-06", "2026-02-20"],
                                   "reportDate": ["2026-08-05", "2026-06-30", "2026-06-12", "2026-05-06", "2025-12-31"], "items": ["2.02,9.01", "", "5.02", "2.02,9.01", ""],
                                   "primaryDocument": ["smpa-8k_20260805.htm", "smpa-20260630.htm", "smpa-8k_20260612.htm", "smpa-8k_20260506.htm", "smpa-20251231.htm"]}}}
    json.dump(subs, open(ROOT / "data/edgar_fixture/submissions_SAMPLE.json", "w"), indent=1)
    facts = {"cik": 1, "entityName": "SAMPLE ANALYTICS INC (structure sample; values fictional)", "facts": {
        "dei": {"EntityCommonStockSharesOutstanding": {"label": "Entity Common Stock, Shares Outstanding", "units": {"shares": [{"end": "2026-07-31", "val": 61000000, "accn": "0000000001-26-000037", "fy": 2026, "fp": "Q2", "form": "10-Q", "filed": "2026-08-05"}]}}},
        "us-gaap": {"Revenues": {"label": "Revenues", "units": {"USD": [{"start": "2025-01-01", "end": "2025-12-31", "val": 820000000, "accn": "0000000001-25-000101", "fy": 2025, "fp": "FY", "form": "10-K", "filed": "2026-02-20"},
                                                                     {"start": "2026-01-01", "end": "2026-06-30", "val": 430000000, "accn": "0000000001-26-000037", "fy": 2026, "fp": "Q2", "form": "10-Q", "filed": "2026-08-05"}]}},
                    "NetIncomeLoss": {"label": "Net Income (Loss)", "units": {"USD": [{"start": "2025-01-01", "end": "2025-12-31", "val": 71000000, "accn": "0000000001-25-000101", "fy": 2025, "fp": "FY", "form": "10-K", "filed": "2026-02-20"}]}}}}}
    json.dump(facts, open(ROOT / "data/edgar_fixture/companyfacts_SAMPLE.json", "w"), indent=1)
    json.dump([{"chart": "Revenue by fiscal year (CIM, page 4)", "metric": "revenue", "period": "FY2025", "value": 42.0e6, "method": "chart_read", "tier": 4, "doc_id": "DR-deal_a-001"}],
              open(ROOT / "data/dataroom/deal_a/chart_reads.json", "w"), indent=1)
    print(f"sample written under {ROOT / 'data'} ({len(recs)} Wren records, {len(heron_recs)} Heron records)")

if __name__ == "__main__":
    main()
