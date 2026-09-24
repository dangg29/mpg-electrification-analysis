# Project report: vehicle efficiency and electrification

## Question and approach

How have listed U.S. vehicle configurations changed in fuel economy and electrification, and how much of their efficiency can be explained by basic design characteristics?

This project follows one fixed workbook through cleaning, feature engineering, exploration, statistical testing, modeling, SQL, and an interactive dashboard. The source has 50,242 configurations, 146 manufacturer labels, and model years 1984–2027. Every row receives equal weight; the analysis does not estimate sales-weighted fleet performance.

The original project already contained four notebooks, prepared datasets, and charts. The completion pass reviewed that work, corrected several interpretation and implementation errors, executed all notebooks, and added the modeling, SQL, dashboard, verification, and documentation layers.

## What the data show

### Gasoline efficiency improved, but the product mix matters

Mean combined MPG for gasoline configurations increased from 19.12 in 1984 to 22.10 in 2026. The annual curve is not monotonic: changes in the types of vehicles offered can move the average even when individual technologies improve. Segment-specific trends, sample sizes, and manufacturer rankings provide context for this compositional effect.

Within gasoline records, engine displacement correlates with combined MPG at **r = −0.778**. Cylinder count is also strongly associated with MPG. These relationships support using engine and vehicle attributes in a predictive model, but do not isolate an engineering or causal effect.

The recent make/model rankings use exactly ten inclusive model years, 2018–2027. They require at least 20 records per manufacturer or five records per make/model group. Their inclusion of the partial newest year differs intentionally from the model evaluation and dashboard default. Model-name suffix removal is heuristic, and manufacturer spellings are preserved.

### Electric range increased alongside the number of configurations

The mean reported BEV range increased from **105.6 miles in 2012** to **302.1 miles in 2026**. The denominators changed from eight to 321 records. This is a comparison of available configurations, not a matched panel of the same vehicles.

HEV, PHEV, and BEV configurations together account for **49.74% of model-year 2026 records**. This percentage should not be called sales share, on-road adoption, or consumer demand. Manufacturers with many variants can contribute disproportionately to the database.

The first-appearance chart identifies the earliest recorded electrified configuration for a manufacturer in this snapshot. It cannot establish the manufacturer's first worldwide product launch.

### Statistical differences are substantial, with important qualifications

| Analysis | Result | Interpretation |
| --- | --- | --- |
| Gasoline MPG by drivetrain, ANOVA | F = 4,309.47 | Group means differ; vehicle mix and unequal variances remain relevant |
| Same groups, Kruskal–Wallis | H = 17,161.26 | Rank distributions differ; this does not adjust for confounding |
| Gasoline MPG by transmission, ANOVA | F = 1,414.45 | Full-history groups combine different model years and designs |
| Gasoline Car segment, before vs. from 2012 | 21.19 vs. 23.87 MPG; n = 13,524 vs. 6,889 | Welch t = 37.23, p ≈ 2.95 × 10⁻²⁸⁷; Cohen's d = 0.58 |
| Displacement and MPG | Pearson r = −0.778 | Strong negative association in gasoline records |
| Segment × powertrain | χ² = 3,743.08; df = 48 | 15 of 63 expected cells below five; asymptotic p-value requires caution |

Some printed p-values underflow to zero. They are not literally zero. The tests are exploratory, not corrected for multiple comparisons, and treat records as independent despite repeated model families and configurations. In particular, the 2012 comparison does **not** identify a policy effect. “Car” is a broad derived segment, not a sedan-only cohort.

## Prediction and forecasting

### Common evaluation design

Vehicle-level models train through 2023 and evaluate on 2024–2026. The newest observed model year, 2027, is excluded. Numeric imputation, scaling, and categorical encoding are fitted only on training records; unseen categories are handled without refitting on the test data. A fixed random seed supports reproducibility.

A temporal split measures performance on later configurations. It does not measure performance on wholly unseen model families; related vehicles may appear on both sides of the time boundary. There is one holdout period and no repeated rolling-origin evaluation. Hyperparameter optimization and calibrated prediction intervals are outside this baseline implementation.

### Gasoline MPG regression

The random forest uses year, displacement, cylinders, gear count, drive, segment, and transmission type. Its 41,290 training records and 1,937 held-out records exclude non-gasoline powertrains.

- MAE: **1.374 MPG**, compared with **4.246 MPG** for the training-mean baseline.
- RMSE: **1.901 MPG**.
- R²: **0.860**.

Predictions and impurity-based feature importance are exported. Importance is descriptive: correlated variables share signal, and impurity importance can favor variables with many possible splits. These importances are not causal effects. No serialized model is loaded by the dashboard; it displays saved evaluation results.

### Electrification classification

The target is whether a configuration is HEV, PHEV, or BEV. The class-weighted logistic baseline uses only year, make, segment, and drive. It excludes direct fuel/powertrain labels and engine, efficiency, or range fields that could reveal the target.

The holdout has 3,722 records and a positive prevalence of 45.51%. ROC AUC is **0.693**, average precision is **0.673**, and balanced accuracy is **0.514**. At the fixed 0.5 threshold, accuracy is **0.473**, below the majority-class baseline of **0.545**.

The confusion matrix, with true class as rows and predicted class as columns, is `[[112, 1916], [47, 1647]]`. The model overpredicts electrification at this threshold. Class weighting and temporal changes in class prevalence make the probability values unsuitable as calibrated adoption estimates. The baseline is retained and reported transparently rather than presented as a successful production classifier.

A future improvement should select weighting and thresholds on a separate chronological validation set, then evaluate once on a new untouched test period.

### Forecasts and S-curve

The gasoline trend fits a line to ten annual means and predicts the next three years for evaluation. Its 2024–2026 MAE is **0.107 MPG**, against **0.155 MPG** for a last-observed-value baseline. It is then refit to 2017–2026 for the 2027–2031 scenarios. This fits equally weighted annual means, unlike the configuration-level model.

The bounded logistic curve fits annual electrified-record shares from 2000 onward. Holdout MAE is **11.90 percentage points**, versus **18.04 points** for the last-value baseline. The final fitted ceiling reaches the imposed 100% upper bound. That boundary behavior signals weak identification of eventual saturation, not evidence that all future vehicles will be electrified.

The scenario outputs should be used to explore extrapolation assumptions. They are not sales adoption forecasts, policy predictions, or uncertainty-qualified estimates. The latest year excluded from fitting can appear as the first scenario year even though a partial snapshot of it already exists.

## Engineering and delivery

Five SQL files recreate annual efficiency, powertrain shares, manufacturer-versus-segment benchmarks, electric range, and first appearances. They demonstrate aggregation, CTEs, joins, ranking windows, lagged year-over-year differences, and rolling averages. SQL results are checked against pandas calculations.

The dashboard uses 7,109 groups keyed by year, make, segment, and powertrain. It stores sums and denominators so filters can recompute weighted means correctly. It never averages group averages without their weights. The app is static, has no account or API-key dependency, and includes explicit handling for missing categories and empty filters.

The eight analytical tests check source integrity, identifiers, classification edge cases, range semantics, dashboard aggregation, SQL parity, temporal model outputs, and executed notebooks. Browser verification checks five filter/download scenarios plus desktop and mobile rendering.

## Corrections made during review

1. Added hydrogen, natural gas, and unknown-fuel handling rather than falling through to Gasoline or broadly assigning every alternate fuel to Flex-Fuel.
2. Changed the PHEV electricity-mode range analysis from `range` to `rangeA`, matching its electricity alternate fuel.
3. Corrected comments that treated unadjusted laboratory ratings as owner-reported economy.
4. Fixed the inclusive ten-year boundary and made the recent-record slice explicit before adding model-name features.
5. Restored and relabeled the existing manufacturer timeline as first appearances in the dataset.
6. Removed duplicate ANOVA execution and corrected the unequal-sample pooled variance for Cohen's d.
7. Added sparse expected-cell diagnostics for chi-square and corrected the claimed zero/missing pattern for BEV engine fields.

## Remaining limitations and extensions

The original download date is unknown. Source estimates may be revised, and the latest years can be incomplete. There are no sales weights, matched longitudinal vehicle cohorts, owner-use observations, external fuel-price histories, or lifecycle emission factors. Optional gas-price and policy-table joins from the initial roadmap were not added because no verified external series was supplied.

Useful next research steps include sales-weighted comparisons, year/segment-adjusted statistical models, a chronological validation period for classifier calibration, multiple rolling-origin forecast backtests, bootstrap uncertainty, and explicit manufacturer/model-family holdouts. None of those extensions is claimed as completed here.

Data definitions: [FuelEconomy.gov](https://www.fueleconomy.gov/feg/ws/index.shtml). Reproduction commands and artifact links: [README](../README.md).
