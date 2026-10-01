# LLMClient

> 21 nodes · cohesion 0.14

## Key Concepts

- **LLMClient** (26 connections) — `src/ai/llm_client.py`
- **ingestor.py** (10 connections) — `src/resume/ingestor.py`
- **CVIngestor** (8 connections) — `src/resume/ingestor.py`
- **test_llm_client.py** (6 connections) — `tests/test_llm_client.py`
- **json** (5 connections)
- **.generate_text()** (5 connections) — `src/ai/llm_client.py`
- **.ingest_cv()** (4 connections) — `src/resume/ingestor.py`
- **.generate_json()** (3 connections) — `src/ai/llm_client.py`
- **.__init__()** (3 connections) — `src/applier/form_filler.py`
- **.extract_text_from_pdf()** (3 connections) — `src/resume/ingestor.py`
- **._call_gemini()** (2 connections) — `src/ai/llm_client.py`
- **._call_groq()** (2 connections) — `src/ai/llm_client.py`
- **._call_ollama()** (2 connections) — `src/ai/llm_client.py`
- **.__init__()** (2 connections) — `src/resume/ingestor.py`
- **Path** (2 connections)
- **.__init__()** (2 connections) — `src/scraper/matcher.py`
- **test_llm_client_json_cleaning()** (2 connections) — `tests/test_llm_client.py`
- **test_llm_client_mock_gemini()** (2 connections) — `tests/test_llm_client.py`
- **pdfplumber** (1 connections)
- **.__init__()** (1 connections) — `src/ai/llm_client.py`
- **Any** (1 connections)

## Relationships

- [MasterProfile](MasterProfile.md) (14 shared connections)
- [run.py](run.py.md) (11 shared connections)
- [app.py](app.py.md) (6 shared connections)
- [compiler.py](compiler.py.md) (1 shared connections)

## Source Files

- `src/ai/llm_client.py`
- `src/applier/form_filler.py`
- `src/resume/ingestor.py`
- `src/scraper/matcher.py`
- `tests/test_llm_client.py`

## Audit Trail

- EXTRACTED: 55 (89%)
- INFERRED: 7 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*