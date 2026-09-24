"""Build a local SQLite database and execute every versioned SQL analysis."""
from pathlib import Path
import sqlite3
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]


def run():
    df = pd.read_parquet(ROOT / 'data/processed/vehicles_features.parquet')
    output = ROOT / 'reports/sql'
    output.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ROOT / 'data/processed/vehicles.sqlite') as conn:
        df.to_sql('vehicles', conn, if_exists='replace', index=False)
        conn.execute('CREATE UNIQUE INDEX vehicle_id ON vehicles(id)')
        conn.execute('CREATE INDEX vehicle_year_powertrain ON vehicles(year, powertrain)')
        for path in sorted((ROOT / 'sql').glob('*.sql')):
            result = pd.read_sql_query(path.read_text(encoding='utf-8-sig'), conn)
            result.to_csv(output / (path.stem + '.csv'), index=False)
            print(path.name, len(result), 'rows')


if __name__ == '__main__':
    run()
