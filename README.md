# Multimodal Perfume-Market RAG

Ask questions about the global perfume/fragrance market (2015–2026) over a
folder of market-research PDFs. Unlike plain-text RAG, this reads the **charts
and tables inside the reports** with Claude's vision and re-sends the actual
chart images to Claude at answer time — and it surfaces *conflicting* market
estimates instead of hallucinating one number.

## Why multimodal matters here
Market reports put their best data inside chart images and tables that text-only
RAG ignores. And fragrance market size estimates vary wildly by definition
(fine fragrance only vs. all fragrance products) — roughly **$17B to $89B for
2026** depending on the source. The system's job is to retrieve from multiple
reports and present the *range with attribution*.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # the only key you need
```
Only the Anthropic key is required. Embeddings run locally via
`sentence-transformers` (Anthropic has no embeddings endpoint), and the vector
store (Chroma) is local too.

## Use
```bash
# 1. Drop market-report PDFs into ./data  (see sources below)
# 2. Build the index (parses text + reads every chart/table with Claude vision)
python ingest.py
# 3. Ask questions
python query.py "What was the global perfume market size by year?"
python query.py "Which region grew fastest, and from which chart?"
python query.py "Why do 2026 estimates disagree so much?"
python query.py "Compare women's vs men's fragrance growth."
python query.py            # interactive mode
```

## Where to get report PDFs for ./data
Grand View Research, Mordor Intelligence, Fortune Business Insights, Coherent
Market Insights, Global Market Insights, Statista, Business Research Insights —
all publish free summary reports / sample PDFs with charts and tables. For the
2015–2020 historical backbone (forecasts dominate the free reports), add
Statista historical tables and France customs perfume-export data.

## How it works
```
ingest.py   PDF page ─┬─ PyMuPDF text ─────────────┐
                      └─ render PNG ─> Claude vision ┤─> chunk ─> local embed ─> Chroma
                         (reads charts/tables)       │           (+ page image path in metadata)
query.py    question ─> embed ─> Chroma top-k ─> retrieved text + source chart images
                      ─> Claude (multimodal, cite-and-flag-conflicts prompt) ─> answer
```

## Files
- `config.py`  — models, paths, chunking, retrieval knobs (swap to `claude-opus-4-8` here)
- `utils.py`   — embeddings, Chroma, PDF→PNG, image encoding
- `ingest.py`  — build the index
- `query.py`   — ask questions

## Next steps to make it portfolio-grade
- Add a reranker (two-stage retrieval) for better precision.
- Add metadata filtering (filter to a region/year before similarity search).
- Re-plot extracted numbers with Plotly so answers come with a clean chart.
- Add a small eval set of Q→expected-source pairs to measure retrieval quality.
- Wrap `query.py` in a Streamlit UI.
