# Roadmap and completion status

The original ten-stage outline is implemented as an analysis project with a static dashboard. Optional external-data joins remain research extensions. Hosted deployment status is tracked separately from implementation.

- [x] **1. Project setup:** repository structure, documented Python environment, pinned direct dependencies, Git ignore rules.
- [x] **2. Data cleaning:** missingness, type checks, identifier validation, selected-field export, documented repair decisions.
- [x] **3. Feature engineering:** powertrain, transmission/gear parsing, segment buckets, time features, adjusted/unadjusted rating gaps.
- [x] **4. EDA A — MPG evolution:** yearly and segment trends, make/model rankings, segment rankings, drivetrain/cylinder heatmaps, BEV efficiency comparison.
- [x] **5. EDA B — electrification:** powertrain shares, first appearances, manufacturer timeline, BEV range, primary-fuel efficiency distributions, segment shares, PHEV electricity-mode range.
- [x] **6. Statistical testing:** ANOVA, Welch t-test, Cohen's d, Kruskal–Wallis, Pearson correlation, chi-square and expected-count diagnostics.
- [x] **7. Modeling:** MPG regression, electrification classification, trend forecast, S-curve scenario, chronological evaluation and baseline comparisons.
- [x] **8. SQL:** SQLite builder, aggregation, CTEs, joins, window functions, rankings, year-over-year and rolling metrics.
- [x] **9. Dashboard implementation:** four charts, interactive filters, summary/comparison tables, model results, CSV download, responsive layout, deployment configuration.
- [x] **9a. Hosted dashboard:** [Vercel production dashboard](https://mpg-electrification-analysis.vercel.app) deployed and verified with five browser filter/download cases.
- [x] **10. Packaging:** README, project/portfolio write-up, findings, limitations, data dictionary, skills inventory, tests, CI workflow.

## Optional research extensions

- Verified historical gas-price and policy-table joins (no external series has been added).
- Sales weighting, matched model-family studies, multiple chronological validation folds.
- Classifier calibration/threshold selection on a separate validation period.
- Forecast uncertainty and sensitivity to S-curve bounds.

See [README](README.md) for execution and [verification](reports/verification.md) for delivered evidence. Published to the private [GitHub repository](https://github.com/dangg29/mpg-electrification-analysis); the remote commit was verified after pushing.
