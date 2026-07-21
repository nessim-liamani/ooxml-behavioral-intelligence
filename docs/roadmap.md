# Roadmap

## Phase 0 — Community Launch (Q3 2026)
**Goal:** Transform from vision repo to credible research initiative.

- [x] Repository creation and initial structure
- [x] Core documentation (README, CONTRIBUTING, GOVERNANCE)
- [x] Academic whitepaper
- [x] Compatibility case schema v1.0
- [x] Partner invitation materials
- [x] Data policy and privacy model
- [ ] Community outreach to Tier 1 partners (in progress)
- [ ] OOXML inspection CLI tool
- [ ] GitHub Discussions enabled

**Success criteria:** 3+ partner organizations aware and engaged

## Phase 1 — MVP: Compatibility Database (Q4 2026 – Q1 2027)
**Goal:** Functioning knowledge base with structured contributions.

### 90 Days
- [ ] Compatibility schema finalized (community feedback incorporated)
- [ ] First 100 compatibility cases submitted and verified
- [ ] CLI analyzer (`ooxml-inspect.py`) with feature detection
- [ ] Knowledge base schema and storage (SQLite)
- [ ] Web interface for browsing compatibility cases

### 6 Months
- [ ] 500+ compatibility cases across all three formats
- [ ] Contribution pipeline (submit → review → merge) operational
- [ ] Contribution from at least 5 external contributors
- [ ] Partnership with at least 1 Tier 1 organization

**Success criteria:** Searchable, structured knowledge base with 500+ verified cases

## Phase 2 — Automated Testing (Q2–Q3 2027)
**Goal:** Automated differential testing across implementations.

- [ ] OOXML Analyzer — full feature extraction and classification
- [ ] Runner for Microsoft Office (automated, CI-compatible)
- [ ] Runner for LibreOffice (automated)
- [ ] XML diff engine — structural comparison
- [ ] Rendering diff engine — visual comparison with ImageMagick
- [ ] CI/CD integration for automated regression testing
- [ ] Public test suite for office suite developers

**Success criteria:** Any OOXML document can be automatically tested across Office + LibreOffice

## Phase 3 — AI Integration (Q4 2027 – Q2 2028)
**Goal:** AI-assisted discovery, repair, and prediction.

### AI-1: Datasets (Q4 2027)
- [ ] Structured training datasets from knowledge base
- [ ] Paired (input, expected output) data
- [ ] Feature-labeled document corpus (10,000+ documents)
- [ ] Host on Hugging Face Datasets

### AI-2: Models (Q1 2028)
- [ ] OOXML structure explanation model
- [ ] XML repair model (broken → working)
- [ ] Compatibility prediction model (classifier)

### AI-3: Copilot (Q2 2028)
- [ ] Interactive OOXML analysis assistant
- [ ] "Why does this render differently?" → behavioral explanation
- [ ] Document repair suggestions with explanation

**Success criteria:** AI models that predict compatibility with >85% accuracy

## Phase 4 — Ecosystem (2028+)
**Goal:** Industry adoption and community self-sustenance.

- [ ] Million-scale document corpus
- [ ] Standardized behavioral test suite (like Web Platform Tests for OOXML)
- [ ] Integration with office suite CI pipelines (LibreOffice, ONLYOFFICE)
- [ ] Academic partnerships and publications
- [ ] Foundation transfer (TDF, ASF, LF, or STF-backed)

---

## Key Milestones

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| Community Launch | Q3 2026 | Schema, tooling, partner outreach |
| First 100 cases | Q4 2026 | Verified compatibility cases |
| Knowledge base MVP | Q1 2027 | Searchable web interface |
| Automated testing | Q3 2027 | Multi-engine CI pipeline |
| Public dataset v1 | Q4 2027 | 10,000+ annotated documents |
| AI models | Q2 2028 | Compatibility prediction + repair |
| Foundation transfer | 2029 | Independent governance |

---

## Success Metrics

| Timeframe | Target |
|-----------|--------|
| 3 months | 100 cases, CLI tool, 1 partner |
| 12 months | 10,000 cases, 100 contributors, 5 partners |
| 36 months | Million-scale corpus, AI models, industry adoption |
