"""Offline classroom embedding fallback: TF-IDF + truncated SVD ("LSA"), fitted on the sample corpus.
Deterministic, no download. Case Study 2 still requires one hosted and one open embedding model;
this exists only so retrieval labs run in class without network access."""
import json
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from src.sample_data import records
MODEL = "lsa-sample-v1"
_pipe = None
def corpus():
    return [r["text"] for r in records("deal_a") + records("deal_b")]
def encode(texts):
    global _pipe
    if _pipe is None:
        _pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True), TruncatedSVD(n_components=16, random_state=7))
        _pipe.fit(corpus())
    v = _pipe.transform(list(texts))
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-12)
