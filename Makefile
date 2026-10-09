PY ?= $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)

.PHONY: setup seed lab check sample clean

setup:
	python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt

seed:
	$(PY) tools/seed_replay_cache.py

lab: seed
	$(PY) -m jupyter lab notebooks

check: seed
	$(PY) -m pytest -q tests
	$(PY) -m pytest -q --nbmake notebooks

sample:
	$(PY) tools/make_sample_data.py && $(PY) tools/make_fixtures.py && $(PY) tools/seed_replay_cache.py

clean:
	rm -rf data/work data/index outputs reports logs services/qa/app.py data/llm_cache data/embed_cache
