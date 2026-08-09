# Test fixtures

## `timeskjema_sample.xls` (parser unit tests)

A trimmed R26 Timeskjema export — 2 turnuser (`OSL_01`, `OSL_Utland_4`) instead
of 57, ~9 KB instead of 222 KB — used by `tests/test_timeskjema_parser.py` for
everything that does not need the full file. Committed, so the parser tests run
anywhere.

Despite the `.xls` extension it is **not** Excel: it is tab-separated
ISO-8859-1 text, exactly as NLF exports it. Keep it that way. Several tests
re-encode it in memory (`TestEncodingDiagnosis`) to check that a wrong encoding
is diagnosed as one error rather than a cascade, so an editor that silently
rewrites it as UTF-8 — or as a real spreadsheet — breaks them.

To regenerate it, take the header lines plus two complete `Turnus:` blocks from
a real export, keeping each block's `Dag` header, all 42 day rows, its
`Sum uke` rows and its `Totalsummer for turnus` row. The parser checks each
block's arithmetic, so partial blocks will not parse.

**Not** the structural baseline. That is the full export at
`turnusdata/r26/R26 endelig.xls`, which is tracked in git (only
`turnusdata/**/*.pdf` and `**/*.png` are ignored). It is what
`scripts/probe_timeskjema.py` diffs new exports against, and what
`tests/test_timeskjema_structure.py` guards. Do not add a second copy here —
two copies of the same file drift.

## `turnuser_R26.pdf` (golden-file regression test)

`tests/test_data_integrity.py::TestScraperRoundtrip` re-scrapes the real R26
source PDF and asserts the output matches the committed
`turnusdata/r26/turnus_schedule_R26.json` (names, count, `tid`,
`dagsverk`, totals, and `start`/`slutt`). This locks the scraper's behavior so
any future change — or the eventual switch to a structured data source — is
caught immediately.

To enable it, drop the source PDF here:

```
tests/fixtures/turnuser_R26.pdf
```

This path is **not** covered by the `.gitignore` rule
`turnusdata/**/*.pdf`, so committing it keeps the regression test
runnable in CI. If the file is absent, the roundtrip tests `skip` (the rest of
the suite still runs).

The test also falls back to `turnusdata/r26/pdf/turnuser_R26.pdf`
(where an admin upload writes it) if no fixture is committed here.
