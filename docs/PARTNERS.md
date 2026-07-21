# Partner Invitation

**We are building a neutral interoperability research platform. We invite organizations to contribute expertise, datasets, infrastructure, or governance.**

This document outlines partnership opportunities, why this project matters to each organization, and what we're asking for.

---

## Partnership Model

| Tier | Commitment | Benefits |
|------|-----------|----------|
| **Steering Partner** | Active governance, dedicated resources | Strategic direction, named in foundation transfers |
| **Technical Partner** | Code, test cases, infrastructure | Technical influence, contributor recognition |
| **Research Partner** | Datasets, academic collaboration | Co-authorship, research outputs |
| **Infrastructure Partner** | Compute, hosting, CI/CD | Public recognition, case studies |

---

## Tier 1 — Immediate Technical Partners

### LibreOffice (The Document Foundation)

**Priority:** ⭐⭐⭐⭐⭐

**Why:** The largest open-source office suite. LibreOffice development spends significant engineering effort reverse-engineering Microsoft Office behavior. A shared knowledge base directly reduces their maintenance burden.

**Current challenge:** Each LibreOffice developer independently discovers and fixes OOXML compatibility issues. Results are buried in Bugzilla and commit messages — not shared, structured, or searchable.

**What we ask:**
- Regression test cases (anonymized)
- Known compatibility bugs migrated to structured cases
- Developer feedback on the schema and tooling
- Technical steering committee participation

**What they gain:**
- Structured, searchable knowledge base instead of Bugzilla archaeology
- Automated regression testing for OOXML compatibility
- Reduced duplicate reverse-engineering effort
- Community contributions to compatibility cases they don't have to create

**Contact:** Via Bugzilla (bugs.documentfoundation.org) or development mailing list

---

### ONLYOFFICE (Ascensio System SIA)

**Priority:** ⭐⭐⭐⭐⭐

**Why:** Commercial open-source hybrid with the strongest OOXML compatibility focus among non-Microsoft office suites. ONLYOFFICE has invested heavily in DOCX rendering fidelity and would benefit from systematic comparison data.

**What we ask:**
- Anonymized test cases from their QA pipeline
- Technical feedback on the compatibility schema
- Infrastructure support (CI/CD, testing environments)

**What they gain:**
- Systematic comparison data against Microsoft Office reference
- Community-contributed edge cases they haven't encountered
- Public demonstration of their compatibility strengths
- Research collaboration opportunities

**Contact:** https://github.com/ONLYOFFICE/DesktopEditors

---

### SuperDoc

**Priority:** ⭐⭐⭐⭐

**Why:** Modern architecture with native OOXML handling rather than conversion-based approaches. SuperDoc represents the next generation of OOXML consumers, making it an ideal reference point for the diff pipeline and a strong technical partner.

**What we ask:**
- Technical feedback on the diff pipeline design
- Anonymized test cases
- Architecture guidance on modern OOXML processing

**What they gain:**
- Behavioral dataset for their own testing
- Community-generated test cases
- Visibility in a growing research initiative

**Contact:** https://github.com/superdoc-dev/superdoc

---

### Open XML SDK (Microsoft / .NET Foundation)

**Priority:** ⭐⭐⭐⭐

**Why:** The official Microsoft ecosystem SDK for OOXML manipulation. The SDK provides low-level XML access but does not address behavioral compatibility — making this project complementary rather than competitive.

**What we ask:**
- Technical guidance on OOXML structures
- Pointers to known edge cases and undocumented behaviors
- Community engagement

**What they gain:**
- Behavioral data that complements the SDK's structural tools
- Community-driven test cases for SDK validation
- Academic and research visibility

**Contact:** https://github.com/dotnet/Open-XML-SDK

---

## Tier 2 — Research Partners

### Academic Institutions

We seek partnerships with:
- **Document Intelligence researchers** — Benchmark datasets for document understanding
- **NLP/ML labs** — Novel structured prediction problems
- **Software engineering departments** — Reverse engineering methodology research
- **Digital preservation programs** — Long-term format accessibility research

**Benefits for academics:**
- Novel, real-world research problems
- Pre-built datasets and infrastructure
- Co-authorship opportunities
- Industry impact pathway

### AI Research Organizations

**Targets:** Hugging Face, Allen AI, IBM Research (Docling team)

**Why:** OOXML behavioral data represents a unique multimodal ML challenge combining XML structure, visual rendering, and natural language. Existing document AI benchmarks focus on content extraction, not behavioral compatibility.

---

## Tier 3 — Infrastructure Partners

| Need | Description |
|------|-------------|
| **CI/CD** | Automated testing across Windows (Office) and Linux (LibreOffice) |
| **Storage** | Hosting for document corpus and rendered outputs |
| **Compute** | GPU resources for AI model training and evaluation |
| **Hosting** | Web platform for knowledge base browsing |

---

## What We Offer

1. **Neutral platform** — No single company controls the project
2. **Open licensing** — Apache 2.0 (code), CC BY 4.0 (docs)
3. **Structured governance** — Clear path to multi-stakeholder steering
4. **Research credibility** — Academic whitepaper, defined research questions
5. **Growing community** — Early outreach to key organizations

---

## How to Partner

1. **Open an issue** with the `partner-interest` label
2. **Email** the project maintainer at the address in CONTRIBUTING.md
3. **Start contributing** — the best partnership begins with a pull request

We respond to all partner inquiries within 5 business days.
