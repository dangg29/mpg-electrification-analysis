# Data provenance and dictionary

## Snapshot

| Property | Value |
| --- | --- |
| Raw file | `raw/vehicles.xlsx`, sheet `vehicles` |
| Raw shape | 50,242 rows × 84 columns |
| Clean shape | 50,242 rows × 35 columns |
| Feature shape | 50,242 rows × 43 columns |
| Model years | 1984–2027 |
| Manufacturer labels | 146 distinct values; original spellings retained |
| Unique key | `id`; no duplicate identifiers |
| SHA-256 | `00ae6483082f03d23bf2f21715db2cc0055c981cbe30ab1674705db983eb3fb0` |

The workbook is the project's pre-existing input. Its schema corresponds to the [FuelEconomy.gov vehicle table](https://www.fueleconomy.gov/feg/ws/index.shtml); original acquisition date and prior spreadsheet conversion history are unknown. The review verified field definitions, not a byte-for-byte match against a newly downloaded dataset. Current downloads can contain revisions and additional records.

Do not replace this file if reproducing the committed results. To update the study, preserve a new snapshot separately, document its date and checksum, rerun the pipeline, and update the snapshot-specific tests and findings deliberately. The notebook expects an Excel sheet named `vehicles` with the source columns it selects.

## Generated artifacts

- `processed/vehicles_clean.parquet`: selected and cleaned analysis fields.
- `processed/vehicles_features.parquet`: cleaned fields plus eight engineered features.
- `processed/vehicles_clean.xlsx`: readable export with a `Vehicle Data` sheet and `Data Dictionary` sheet. Despite its filename, it includes a selection of engineered fields. Headers mentioning MPG require the fuel-specific interpretation below.
- `processed/vehicles.sqlite`: locally generated SQLite copy, excluded from Git.
- `../dashboard/data.json`: additive group summaries, model metrics, and forecast scenarios for the static app.

## Retained fields

| Column | Meaning / treatment |
| --- | --- |
| `id` | Vehicle configuration identifier |
| `year` | Model year |
| `make` | Manufacturer label |
| `model` | Model label; date-parsed cells repaired to month-day text |
| `VClass` | Original vehicle class |
| `drive` | Drivetrain label |
| `trany` | Original transmission description |
| `cylinders` | Engine cylinders; missing retained |
| `displ` | Engine displacement in liters; missing retained |
| `fuelType` | Combined fuel description |
| `fuelType1` | Primary fuel |
| `fuelType2` | Alternate fuel |
| `atvType` | Technology / alternative-fuel label |
| `city08`, `highway08`, `comb08` | Adjusted primary-fuel efficiency |
| `UCity`, `UHighway` | Unadjusted primary-fuel efficiency |
| `cityA08`, `highwayA08`, `combA08` | Alternate-fuel efficiency |
| `fuelCost08` | Source annual primary-fuel cost estimate; not historical spending |
| `co2TailpipeGpm` | Tailpipe CO₂ per mile; not lifecycle emissions |
| `mpgData` | Availability flag for owner MPG data; no owner readings loaded |
| `startStop` | Start/stop system flag |
| `phevCity`, `phevHwy`, `phevComb` | Composite PHEV efficiency |
| `range`, `rangeCity`, `rangeHwy` | Source range fields; BEV trend uses `range` |
| `rangeA` | Alternate-fuel range; used for electricity-mode PHEV trend |
| `charge120`, `charge240` | Charging duration fields |
| `evMotor` | Source electric motor description |

The table groups related fields; it covers all 35 retained columns. Efficiency units depend on fuel. Compare gasoline MPG separately from electric MPGe. PHEV `comb08` describes its primary gasoline fuel rather than its composite operation. Definitions: [FuelEconomy.gov](https://www.fueleconomy.gov/feg/ws/index.shtml).

## Engineered fields

| Column | Implementation |
| --- | --- |
| `powertrain` | Source technology flag first, fuel inference second; observed groups: Gasoline, Diesel, HEV, PHEV, BEV, Flex-Fuel, CNG, Hydrogen, Other |
| `transmission_type` | Regex/string parsing into Manual, Automatic, CVT, or missing |
| `num_gears` | Parsed discrete gear count; CVT remains missing |
| `segment` | Car, SUV, Truck/Pickup, Van/Minivan, Wagon, Sports/Two-Seater, Special Purpose |
| `decade` | Integer floor of model year to a decade |
| `post_2012` | Model year ≥ 2012; descriptive grouping only |
| `epa_gap_city` | `UCity - city08`, after zero unadjusted values become missing |
| `epa_gap_hwy` | `UHighway - highway08`, with the same handling |

Classification has explicit LPG handling, although no LPG group is observed after applying these rules to this snapshot. Unknown primary fuels become `Other`; they are not silently treated as gasoline. Segment fallback is `Car` and should be reviewed before using new source categories.

## Missing values and limitations

See [cleaning notes](../reports/data_cleaning_notes.md). Most BEV engine fields are missing in this snapshot; missing values are not automatically zeros. Numeric coercion discards composite `rangeA` strings; original values remain in the raw workbook. The model-name date repair cannot guarantee recovery of the original textual label. No sales weights, observed driving records, charging behavior, or lifecycle emissions data are included.
