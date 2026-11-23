# Italy Budget Law Reader

Static reader for the Italian Budget Law: article navigator, measure classification (thematic area, relevance, low-priority flag, 2026 CSRs) and Excel export of the financial effects for a macro-fiscal model. Built on the architecture of the EU Amendment Reader.

## Structure

- `index.html` — the application (self-contained HTML/JS; SheetJS for the Excel export)
- `data/laws.json` — registry of budget law files used by the selector (empty until the first law is extracted)
- `data/reference.json` — thematic taxonomy, relevance scale, low-priority criteria, CSR structure, alignment/confidence/review scales, balance definitions
- `data/schema.json` — versioned data schema, conventions and change log
- `data/<law_id>.json` — one file per budget law (e.g. `lb-2027.json`)

## Excel workbook

`README`, `Measures`, `Fiscal_effects` (one row per measure, one column per balance-year, like the summary table of financial effects), `Summary_by_area`, `QA`, `Source_rows` (row-level traceability). Values keep the source's sign and unit; a value not in the source is a blank cell, never zero; SNF, fabbisogno and indebitamento netto are never added together.

## Running locally

The page loads its data with `fetch`, so serve the folder over HTTP:

```
python3 -m http.server 8000
```

Then open http://localhost:8000.
