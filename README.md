# SSSWET

**Super Soldier Space Warping Engeriening Tech**  
*ETDESS — Équivalent français du nom SSSWET*

SSSWET is an experimental, open research-software project for organizing scientific inquiry, computational studies, evidence review and collaboration between specialized research agents.

The project explores a disciplined workflow for turning research questions into structured work, comparing approaches, documenting evidence and identifying what still needs to be tested. Ambitious scientific ideas are treated as hypotheses—not as established capabilities.

## Project goals

- Organize research objectives into manageable tasks and specialist roles.
- Support literature discovery and local document analysis.
- Preserve source provenance and research history.
- Represent hypotheses, findings, sources, datasets and experiments in a knowledge graph.
- Identify research gaps and recorded contradictions for further review.
- Plan experiments and keep simulations distinct from real-world observations.
- Compare computational models and propose bounded follow-up scenarios.
- Coordinate research campaigns, resources and knowledge transfers.
- Provide a multilingual web interface and a local research environment.

## Current capabilities

| Area | Available functionality |
|---|---|
| Research workflow | Task decomposition, role-based allocation, strategy changes and bounded orchestration |
| Literature discovery | Crossref, OpenAlex and arXiv metadata discovery |
| Local documents | JSON corpus and page-based PDF text extraction |
| Model integration | Configurable OpenAI-compatible chat-completions provider |
| Research memory | SQLite persistence for tasks, events, sources and shared knowledge |
| Evidence provenance | DOI, dataset and provenance-group records |
| Knowledge graph | Typed nodes and explicit relationships |
| Research review | Gap analysis and contradiction reporting |
| Experimentation | Structured plans, simulation records and real-observation records |
| Simulation studies | Bounded multi-model comparisons and reproducible output records |
| Optimization | Human-reviewed adaptive scenario proposals |
| Campaign coordination | Pipeline-integrated milestone scheduling, specialist allocation, resource quotas, retry tracking and explicit completion review |
| Web interface | Responsive multilingual interface, global research dashboard and 15 initial language catalogues |

Capabilities are implemented incrementally. The public web interface is a static application; the Python research engine runs locally and is not hosted by GitHub Pages.

## Architecture

The repository is organized into two main parts:

- **`core/`** — Python research engine, command-line tools, local API, persistence, verification and simulation utilities.
- **`web/`** — static multilingual web application and progressive web app assets.

The local service binds to `127.0.0.1` by default and exposes read-only API endpoints for the web interface. Research state is stored locally in SQLite unless another database path is configured.

## Getting started

### Requirements

- Python 3.11 or newer
- Git
- Node.js 22 or newer for web-interface checks

### Install the research core

```bash
git clone https://github.com/gudjencio/SSSWET.git
cd SSSWET/core
python -m pip install -e .
ssswet-local
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) in a browser.

### Run a research task

```bash
ssswet-run --objective "Review methods for measuring wave propagation" --domain physics
```

A local JSON corpus can be supplied with `--corpus`. PDF extraction is available through the optional dependency:

```bash
python -m pip install -e ".[pdf]"
ssswet-run --objective "Compare experimental methods" --domain physics --pdf ./paper.pdf
```

For literature metadata discovery, use `--provider crossref`, `openalex`, `arxiv` or `literature`. A compatible language-model provider can be configured with local environment variables; API credentials must never be committed to the repository.

See the [core developer guide](core/README.md) for command options, provider configuration, data formats and API details.

## Scientific integrity and responsible research

SSSWET is a research-support tool, not an authority on scientific truth. Its outputs may be incomplete, inaccurate or biased.

- Model agreement is not proof, and generated text is not a scientific source.
- Bibliographic discovery does not establish the validity of a publication or claim.
- Provenance indicators support review; they do not automatically establish source independence.
- Simulation outputs are not real-world observations.
- Optimization scores are not probabilities, confidence intervals or proof of an optimum.
- Verification states require explicit evidence and review; they are not inferred from presentation or consensus.
- Medical, biological, aerospace and other safety-critical work requires qualified domain experts, appropriate ethics review and all applicable legal and regulatory approvals.
- The project does not provide instructions for weapon construction or intentional harm.
- Physical experiments are not launched automatically. High-impact actions require human authorization.

The project aims to make uncertainty, limitations, provenance and unresolved questions visible rather than conceal them.

## Languages

The web interface currently includes initial catalogues for English, French, Spanish, German, Italian, Portuguese, Dutch, Russian, Ukrainian, Arabic, Hebrew, Japanese, Korean, Chinese and Hindi.

Arabic and Hebrew use right-to-left layout. Translation coverage and quality are evolving; contributions from fluent speakers are welcome.

## Public links

- **Web application:** [gudjencio.github.io/SSSWET](https://gudjencio.github.io/SSSWET/)
- **Source code:** [github.com/gudjencio/SSSWET](https://github.com/gudjencio/SSSWET)
- **Google Sites mirror instructions:** [GOOGLE_SITES_MIRROR.md](GOOGLE_SITES_MIRROR.md)
- **X:** [@ssswetech](https://x.com/ssswetech)
- **Instagram:** [@ssswetech](https://www.instagram.com/ssswetech)
- **YouTube:** [@ssswetech](https://www.youtube.com/@ssswetech)
- **Contact:** [ssswetindustries@gmail.com](mailto:ssswetindustries@gmail.com)

The Google Sites page is intended to embed the canonical web application, avoiding a separate copy that could become outdated.

## License

SSSWET is distributed under the [MIT License](LICENSE). The license permits use, modification and redistribution subject to its terms.

## Development and contributions

Bug reports, reproducible test cases, documentation improvements, accessibility work and translation reviews are welcome through the repository's issue tracker and pull requests.

Please do not publish API keys, private datasets, personal information or confidential research material in issues or commits. Contributions should include relevant tests and clearly distinguish measured results, simulations, assumptions and hypotheses.

## Project status

SSSWET is under active development. Interfaces, APIs and data formats may change between releases. Features described as available are implemented in the repository, but their scientific usefulness depends on the quality of supplied data, methods and independent review.

---

**Project:** SSSWET  
**French designation:** ETDESS  
**Contact:** ssswetindustries@gmail.com
