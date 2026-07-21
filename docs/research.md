# Research Areas

## Open Research Questions

### 1. Behavioral Gaps in OOXML Specifications
What percentage of real-world OOXML behavior is undocumented? Systematic gap analysis between ECMA-376/ISO 29500 and observed behavior.

### 2. Cross-Implementation Variance
How do different office suites interpret the same OOXML structures? Quantified variance analysis across LibreOffice, ONLYOFFICE, and other implementations.

### 3. Legacy Compatibility Modes
How do historical compatibility flags (e.g., `compatMode="15"`, `wordProcessingML` legacy namespaces) affect document rendering? Catalog of undocumented compatibility behaviors.

### 4. Rendering Algorithm Documentation
What rendering algorithms are underspecified or implementation-dependent? Focus on text layout, table sizing, image positioning.

### 5. AI for Document Understanding
Can machine learning models predict rendering behavior from XML structure alone? Feasibility and accuracy benchmarks.

### 6. Automated Repair
Can AI models learn to fix broken OOXML to achieve reference-compatible output? Repair success rate analysis.

## Relevant Academic Fields

| Field | Relevance |
|-------|-----------|
| Document Intelligence | Multimodal understanding of document structure and content |
| Software Engineering | Reverse engineering, compatibility testing, differential analysis |
| NLP / NLU | Document structure parsing, semantic understanding |
| Program Synthesis | Automated repair of structured document formats |
| Digital Preservation | Long-term document accessibility and format migration |
| Human-Computer Interaction | Usability of document compatibility tools |

## Prior Art

| Project | Domain | Lessons |
|---------|--------|---------|
| Web Platform Tests | Browser compatibility | Automated cross-implementation testing at scale |
| Wine | Windows API | Community-driven behavioral documentation |
| ReactOS | OS kernel | Reverse engineering with legal safeguards |
| Apache POI | Java OOXML | Long-running open-source OOXML implementation |
| python-docx | Python OOXML | Popular OOXML library with known limitations |
| ODF Toolkit | OpenDocument | Similar effort for ODF format |

## Research Outputs

This project aims to produce:
- **Annotated behavioral datasets** — structured, searchable, versioned
- **Benchmarks** — standardized compatibility test suites
- **Publications** — open-access papers on findings
- **Models** — open-weight AI models for document understanding and repair

---

## Active Research Questions

| ID | Question | Method | Expected Output | Status |
|----|----------|--------|-----------------|--------|
| **RQ1** | Can Microsoft Office behavior be approximated from input/output examples alone? | Supervised learning on paired (document, rendering) data | Behavioral prediction model | Open |
| **RQ2** | Can AI models predict OOXML compatibility failures before rendering? | Classification on feature vectors extracted from document XML | Pre-flight compatibility checker | Open |
| **RQ3** | Can LLMs generate OOXML repair patches for broken documents? | Sequence-to-sequence fine-tuning on (broken, fixed) pairs | Automated document repair tool | Open |
| **RQ4** | Can visual rendering differences be automatically explained and classified? | Vision-language models on paired screenshots + structured diffs | Automated diff explainer | Open |
| **RQ5** | What percentage of real-world OOXML behavior is undocumented in ECMA-376/ISO 29500? | Systematic gap analysis: spec vs observed behavior in corpus | Empirical coverage report with quantified gaps | Open |

### RQ1 Detail: Behavioral Approximation

**Hypothesis:** For a subset of OOXML features, Microsoft Office rendering behavior can be modeled as a function `f(document_XML, environment) → rendered_output`.

**Approach:**
1. Build a dataset of paired (OOXML XML, reference rendering)
2. Train supervised models to predict rendering characteristics
3. Evaluate accuracy and generalization across feature categories

**Success criterion:** >90% accuracy in predicting rendering outcomes for common features.

### RQ2 Detail: Compatibility Prediction

**Hypothesis:** Compatibility failures are predictable from document XML structure alone, without rendering.

**Approach:**
1. Extract feature vectors from OOXML documents (extensions used, legacy flags, structural complexity)
2. Label documents by compatibility outcome across implementations
3. Train binary/multi-class classifiers

**Success criterion:** >85% accuracy in predicting compatibility failures for unseen documents.

### RQ3 Detail: Automated Repair

**Hypothesis:** Many OOXML compatibility failures result from specific XML patterns that can be automatically rewritten.

**Approach:**
1. Collect (broken_document, working_document) pairs
2. Generate XML diffs as repair patches
3. Train sequence-to-sequence models to generate patches

**Success criterion:** >50% of test documents successfully repaired to reference-equivalent output.

### RQ4 Detail: Visual Explanation

**Hypothesis:** Visual rendering differences can be automatically described in natural language, similar to image captioning.

**Approach:**
1. Generate visual diffs (pixel-level comparison of rendered outputs)
2. Pair with structured XML diffs and human-written explanations
3. Train vision-language models to generate explanations

**Success criterion:** Human evaluation rates >70% of generated explanations as useful.

### RQ5 Detail: Specification Gap Analysis

**Hypothesis:** A significant portion of OOXML behavior required for correct rendering is not documented in the standard.

**Approach:**
1. Build corpus of documents exercising specific OOXML features
2. Map observed behaviors to corresponding specification sections
3. Identify behaviors without specification coverage

**Success criterion:** Quantified gap report with per-feature coverage percentages.

---

## How to Contribute to Research

1. **Pick a research question** — Comment on the corresponding GitHub issue
2. **Propose methodology** — Open a discussion with your approach
3. **Request data** — We provide datasets for approved research projects
4. **Publish** — We encourage open-access publication and co-authorship

See [PARTNERS.md](PARTNERS.md) for research partnership details.
