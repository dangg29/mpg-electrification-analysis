# Verification record

Verified locally on **September 24, 2026**, using Python 3.14.2 on Windows.

## Reproduction

`python scripts/run_all.py` completed successfully: all four notebooks executed; the regression, classification, and forecast stages produced results; five SQL queries exported CSVs; and the dashboard builder generated 7,109 groups representing 50,242 records.

The notebook runner uses its own Python interpreter, a notebook-specific working directory, project-local runtime files, and explicit kernel shutdown. A final targeted rerun of notebook 02 regenerated the readable workbook after correcting its efficiency headers and missing-engine-field descriptions.

Windows sandbox execution initially blocked an installed SciPy DLL. The same installed library and pipeline executed successfully with approved execution outside the sandbox. No operating-system security controls were changed.

## Automated analytical checks

`python -m unittest discover -s tests -v`: **8 tests passed**.

| Check | Evidence |
| --- | --- |
| Raw source preserved | SHA-256 matches the documented workbook fingerprint |
| Record integrity | 50,242 records, 43 feature fields, unique identifiers, expected year range |
| Powertrain edge cases | Explicit hydrogen, CNG, BEV, PHEV, E85, hybrid, and unknown-fuel examples |
| Feature and range meaning | Laboratory gap arithmetic, CVT gear behavior, and PHEV alternate-fuel range checks |
| Browser data aggregates | Counts, means, and electrified numerators match raw Parquet under multiple filters |
| SQL consistency | Annual means, rolling means, powertrain shares, and PHEV ranges match pandas |
| Model output integrity | Holdout years, unique prediction IDs, finite scenarios, bounded shares, no direct target-proxy fields |
| Notebook execution | Valid notebook format, executed code cells, no saved error outputs |

`node --check dashboard/app.js` passed. These checks establish the documented snapshot's consistency; they do not validate statistical assumptions or guarantee future predictive performance.

## Dashboard browser verification

Story: filter controls select static aggregate records, recompute weighted metrics, render charts/tables, and export a CSV reflecting the same selection.

The local server returned HTTP 200 for the page, styles, JavaScript, and JSON. The browser rendered all controls, four default charts, KPI cards, comparison tables, and saved model results. Browser error and console checks returned no application errors. A favicon request observed during initial verification was eliminated with an inline SVG favicon.

Five browser cases passed against values independently calculated from Parquet:

| Selection | Displayed records | CSV record total | Result |
| --- | ---: | ---: | --- |
| Default 1984–2026 | 49,868 | 49,868 | Four charts; matching metrics |
| Toyota SUVs, 2018–2026 | 240 | 240 | Combined filters and metrics match |
| Tesla BEVs, 2012–2026 | 185 | 185 | Gasoline metric unavailable; other charts/metrics work |
| Tesla, 1984–1985 | 0 | 0 | Explicit empty state; no stale charts |
| Reversed year range | 0 | 0 | Clear validation message |

Reset restored 49,868 records. Browser checks also compared gasoline mean MPG, BEV mean range, and electrified share where applicable. Desktop (1440 × 1000) and mobile (390 × 844) layouts were visually reviewed. See [desktop preview](dashboard_preview.png).

## Delivery boundaries

The GitHub Actions workflow is configured to reproduce the pipeline and run analytical checks on Linux. Its cloud outcome is separate from the completed local verification and must be checked after publication. Package versions pin direct dependencies only; cross-platform results can differ slightly due to floating-point implementations.

External dashboard deployment is verified separately after an actual hosted URL is available. A local screenshot or successful configuration is not proof of a hosted deployment.
