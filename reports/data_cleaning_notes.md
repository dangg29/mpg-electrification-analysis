# Cleaning and feature engineering decisions

## Cleaning notebook

The raw workbook contains 50,242 records and 84 fields. Notebook 01 retains 35 fields and preserves all records. Identifier duplication and full-row duplication checks returned zero duplicates.

- The designated range, PHEV-efficiency, and charging fields have numeric `-1` and `0` replaced with missing values. This rule applies to all rows, including electric vehicles; it is a missing-value convention, not a vehicle-specific inference. These fields are not all exclusively electric (for example, PHEV primary range is not its electricity-only range).
- Recorded zero cylinders or displacement values are preserved. Most BEV values are actually missing: 1,572 missing cylinder values and 1,571 missing displacement values. The earlier statement that BEVs were generally represented by zero was inaccurate.
- `trany = Not Available` becomes missing.
- Numeric-looking fields are scanned for values that cannot be coerced to numbers. Composite slash-separated `rangeA` values cannot be reduced to a single range without assumptions and are coerced to missing.
- Excel date objects in model names are converted to month-day strings. This is an imperfect repair: the original text cannot always be established from the parsed date alone.
- Original make labels are retained; no broad manufacturer deduplication is claimed.
- Clean data are saved as Parquet. The raw workbook is unchanged.

## Feature notebook

- Powertrain classification prioritizes `atvType`, then checks fuel fields. Explicit hydrogen and natural-gas handling prevents contamination of the gasoline group. Electricity as an alternate fuel maps to PHEV; E85 maps to Flex-Fuel; unrecognized primary fuels map to Other. Source flags still require scrutiny, especially for historical records.
- Transmission strings map to Manual, Automatic, or CVT. Regex patterns recover fixed gear counts; CVTs retain missing gear counts by design.
- Vehicle classes map to seven segments. Unknown new class labels would currently fall back to Car and require review.
- Decade and post-2012 flags support grouping, not causal identification.
- Zero `UCity`/`UHighway` values become missing before computing unadjusted minus adjusted efficiency gaps. These are laboratory-rating gaps, not user-reported MPG deviations.
- The friendly Excel export selects 16 fields and includes a data dictionary, frozen headers, and bounded column widths. Its MPG labels must be interpreted by fuel type.

## Review corrections

The completion pass corrected powertrain fallbacks, switched the PHEV electricity-mode range analysis to `rangeA`, fixed the inclusive last-ten-model-years boundary (`max_year - 9`), restored the first-appearance timeline, removed a duplicate ANOVA calculation, corrected the unequal-sample pooled variance for Cohen's d, and added chi-square expected-cell diagnostics. The source data were preserved and generated outputs rebuilt.

The reviewed field meanings are documented by [FuelEconomy.gov](https://www.fueleconomy.gov/feg/ws/index.shtml). The exact data download date remains unknown.
