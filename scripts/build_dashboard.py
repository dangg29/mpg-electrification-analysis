"""Export compact additive aggregates so browser filters retain correct weights."""
from pathlib import Path
import json
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]


def run():
    df = pd.read_parquet(ROOT / 'data/processed/vehicles_features.parquet')
    groups = df.groupby(['year', 'make', 'segment', 'powertrain'], observed=True)
    aggregate = groups.agg(n=('id', 'size'), mpg_sum=('comb08', 'sum'), mpg_n=('comb08', 'count'), range_sum=('range', 'sum'), range_n=('range', 'count')).reset_index()
    payload = {'columns': aggregate.columns.tolist(), 'rows': aggregate.values.tolist(), 'records': len(df), 'minYear': int(df.year.min()), 'maxYear': int(df.year.max()), 'metrics': json.loads((ROOT / 'reports/modeling/metrics.json').read_text(encoding='utf-8')), 'forecasts': pd.read_csv(ROOT / 'reports/modeling/forecast_scenarios.csv').to_dict(orient='records')}
    (ROOT / 'dashboard/data.json').write_text(json.dumps(payload, separators=(',', ':'), allow_nan=False), encoding='utf-8')
    print('Dashboard:', len(aggregate), 'groups;', len(df), 'records')


if __name__ == '__main__':
    run()
