# open-harness-atlas — common workflows
#
# All targets are repeatable, idempotent, and have no side effects outside
# the working directory unless explicitly stated.

PY ?= python
VENV ?= .venv

.PHONY: help
help:  ## Show this help message
	@echo "open-harness-atlas — Makefile targets"
	@echo ""
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

.PHONY: setup
setup:  ## Create venv and install dev + visuals extras
	$(PY) -m venv $(VENV)
	$(VENV)/Scripts/pip install -e ".[dev,visuals,network]" 2>/dev/null || \
	  $(VENV)/bin/pip install -e ".[dev,visuals,network]"

# ---------------------------------------------------------------------------
# Validation & tests
# ---------------------------------------------------------------------------

.PHONY: validate
validate:  ## Validate registry YAML files against schema
	$(PY) scripts/validate_registry.py

.PHONY: test
test:  ## Run hermetic unit tests (no network)
	$(PY) -m pytest -q

.PHONY: test-network
test-network:  ## Run all tests including link checks (network required)
	$(PY) -m pytest -q -m "network or not network" --network

.PHONY: lint
lint:  ## Lint Python sources
	$(PY) -m ruff check scripts tests

# ---------------------------------------------------------------------------
# Build artefacts
# ---------------------------------------------------------------------------

.PHONY: matrices
matrices:  ## Regenerate comparison matrices under docs/
	$(PY) scripts/build_matrices.py

.PHONY: visuals
visuals:  ## Regenerate data-driven SVGs under visuals/
	$(PY) scripts/build_visuals.py

.PHONY: build
build: matrices visuals  ## Regenerate all build artefacts

# ---------------------------------------------------------------------------
# Metadata refresh (weekly)
# ---------------------------------------------------------------------------

.PHONY: refresh
refresh:  ## Refresh GitHub metadata into registry/_metadata/
	$(PY) scripts/refresh_metadata.py

# ---------------------------------------------------------------------------
# Optional interactive companion (Neo4j + create-context-graph)
# ---------------------------------------------------------------------------

.PHONY: companion
companion:  ## Generate the interactive knowledge-graph companion app
	$(PY) scripts/build_companion_domain.py
	@echo ""
	@echo "Companion domain emitted to companion/domain/open-harnesses.yaml"
	@echo "Run:  cd companion && create-context-graph ./app --domain ./domain/open-harnesses.yaml --framework pydanticai --demo-data"
	@echo ""

.PHONY: neo4j-local
neo4j-local:  ## Launch a local Neo4j 5 container for the companion
	docker run --rm -d \
	  --name oha-neo4j \
	  -p 7474:7474 -p 7687:7687 \
	  -e NEO4J_AUTH=neo4j/change-me-please \
	  -e NEO4J_PLUGINS='["apoc"]' \
	  neo4j:5
	@echo "Neo4j running at http://localhost:7474 (user: neo4j, pass: change-me-please)"

# ---------------------------------------------------------------------------
# Housekeeping
# ---------------------------------------------------------------------------

.PHONY: clean
clean:  ## Remove caches and rendered artefacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache **/__pycache__
	rm -rf build dist *.egg-info
