# Skills and knowledge applied

This inventory links capabilities to actual project work. It distinguishes the original notebook analysis from the additions made during the completion pass; it does not imply that every installed library or available assistant skill was used.

| Skill / knowledge | Concrete application | Evidence |
| --- | --- | --- |
| Python and pandas | Ingest Excel, inspect types/missingness, filter cohorts, group and pivot records, export Parquet | Notebooks 01–03 |
| Data quality and provenance | Duplicate checks, numeric contamination scan, model-name repair, raw-file checksum, preserved source snapshot | Notebook 01; `data/README.md`; tests |
| Domain-aware missingness | Distinguish recorded zero from missing engine fields; preserve CVT gear-count non-applicability | Notebooks 01–02; cleaning notes |
| Feature engineering | Source-priority powertrain inference, regex transmission parsing, segment mapping, calendar features | Notebook 02 |
| Vehicle efficiency interpretation | Separate MPG/MPGe and PHEV operating modes; distinguish laboratory ratings, configuration shares, and actual adoption | Notebook 03; project report |
| Exploratory analysis | Time trends, rankings, sample-size checks, heatmaps, box plots, and manufacturer timelines | Notebook 03; chart exports |
| Statistics | ANOVA, Welch t-test, Kruskal–Wallis, Cohen's d, Pearson correlation, and chi-square expected-cell diagnostics | Notebook 04 |
| Predictive modeling | Training-only preprocessing, missing-value imputation, one-hot encoding, random forests and logistic regression | `scripts/modeling.py` |
| Evaluation design | Chronological holdout, baseline comparisons, imbalance-aware metrics, target-proxy exclusion, honest reporting of weak results | Model metrics and project report |
| Forecasting | Trailing-window linear trend, constrained nonlinear curve fitting, holdout backtests, explicit scenario limitations | Modeling script and forecast CSVs |
| SQL | Aggregation, CTEs, joins, `LAG`, `DENSE_RANK`, and rolling window calculations | Five files under `sql/` |
| Frontend development | Semantic HTML, responsive CSS, labeled controls, live status messages, SVG charts, CSV Blob downloads, escaped labels | `dashboard/` |
| Aggregation design | Additive sums and counts preserve configuration weights through browser filters | Dashboard builder and parity tests |
| Quality assurance | Analytical invariants, independent SQL/pandas comparisons, raw-versus-browser checks, empty states, viewport checks | `tests/`; verification report |
| Reproducible delivery | Ordered notebook execution, pinned direct dependencies, one-command pipeline, CI configuration, Git hygiene | Scripts, requirements, GitHub workflow |
| Technical communication | README, data dictionary, methods report, explicit roadmap status, operational instructions | Project documentation |

## Existing work and completion work

**Existing:** four notebooks, source/processed data, Excel export, most exploratory chart code, initial statistical analyses, and a ten-stage roadmap.

**Completion pass:** reviewed and corrected analytical semantics and classification; executed the statistical notebook fully; restored the manufacturer timeline; added evaluated models and forecasts, five SQL analyses, an interactive static dashboard, reproducible commands, regression checks, CI, documentation, and GitHub packaging.

## Assistant workflow skills applied

- **vercel:agent-browser**: browser automation for the local static dashboard.
- **vercel:agent-browser-verify**: visual inspection, rendered controls, and console/error checks after server startup.
- **vercel:deployments-cicd**, **vercel:vercel-cli**, and **vercel:vercel-api**: deployment configuration, scoped upload preparation, and Vercel account checks.
- **vercel:verification**: traced filters through selected data, weighted summary calculations, chart rendering, and CSV output.

These are workflow aids used during development, not runtime dependencies. Browser checks used the `agent-browser` npm CLI. The dashboard itself requires no Vercel SDK or JavaScript framework. GitHub account access used the GitHub connector for discovery and the configured Git credential manager for publication; credentials are not included in the repository.

The project uses standard plotting libraries for analytical figures. No generated artwork, LLM feature, sales dataset, or external gas-price/policy dataset is part of the implementation.
