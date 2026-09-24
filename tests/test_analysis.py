"""Checks for source integrity, analytical semantics, SQL parity and UI data."""
import ast
import hashlib
import json
from pathlib import Path
import sqlite3
import unittest
import numpy as np
import pandas as pd
import nbformat

ROOT = Path(__file__).resolve().parents[1]


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_parquet(ROOT / 'data/processed/vehicles_features.parquet')
        cls.payload = json.loads((ROOT / 'dashboard/data.json').read_text())
        cls.agg = pd.DataFrame(cls.payload['rows'], columns=cls.payload['columns'])

    def test_source_fingerprint(self):
        digest = hashlib.sha256((ROOT / 'data/raw/vehicles.xlsx').read_bytes()).hexdigest()
        self.assertEqual(digest, '00ae6483082f03d23bf2f21715db2cc0055c981cbe30ab1674705db983eb3fb0')

    def test_record_integrity(self):
        self.assertEqual(self.df.shape, (50242, 43))
        self.assertTrue(self.df.id.is_unique)
        self.assertEqual((self.df.year.min(), self.df.year.max()), (1984, 2027))
        self.assertTrue(self.df.comb08.gt(0).all())

    def test_powertrain_edge_cases(self):
        notebook = nbformat.read(ROOT / 'notebooks/02_feature_engineering.ipynb', as_version=4)
        code = next(c.source for c in notebook.cells if 'def classify_powertrain' in c.source)
        function = next(n for n in ast.parse(code).body if isinstance(n, ast.FunctionDef))
        scope = {'pd': pd}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<classification>', 'exec'), scope)
        for fuel1, fuel2, atv, expected in [
            ('Hydrogen', None, None, 'Hydrogen'),
            ('Natural Gas', None, None, 'CNG'),
            ('Regular Gasoline', 'Electricity', None, 'PHEV'),
            ('Electricity', None, None, 'BEV'),
            ('Regular Gasoline', 'E85', None, 'Flex-Fuel'),
            ('Regular Gasoline', None, 'Hybrid', 'HEV'),
            ('Unknown', None, None, 'Other'),
        ]:
            with self.subTest(expected=expected):
                self.assertEqual(scope['classify_powertrain'](pd.Series({'fuelType1':fuel1, 'fuelType2':fuel2, 'atvType':atv})), expected)
        gas = self.df[self.df.powertrain.eq('Gasoline')]
        self.assertTrue(gas.fuelType1.str.contains('Gasoline').all())

    def test_features_and_range_semantics(self):
        df = self.df
        np.testing.assert_allclose(df.epa_gap_city, df.UCity-df.city08, equal_nan=True)
        self.assertTrue(df.loc[df.transmission_type.eq('CVT'), 'num_gears'].isna().all())
        phev = df[df.powertrain.eq('PHEV')]
        self.assertTrue(phev.fuelType2.eq('Electricity').all())
        self.assertTrue(phev.rangeA.between(1, 150).all())
        self.assertGreater(phev['range'].mean(), 300)

    def test_dashboard_aggregates_preserve_weights(self):
        self.assertEqual(self.agg.n.sum(), len(self.df))
        for start, end, segment, make in [(1984,2027,None,None),(2018,2026,'SUV',None),(2010,2026,None,'Toyota')]:
            raw=self.df[self.df.year.between(start,end)]
            agg=self.agg[self.agg.year.between(start,end)]
            for key,value in [('segment',segment),('make',make)]:
                if value: raw=raw[raw[key].eq(value)]; agg=agg[agg[key].eq(value)]
            self.assertEqual(len(raw), agg.n.sum())
            self.assertAlmostEqual(raw.comb08.mean(), agg.mpg_sum.sum()/agg.mpg_n.sum())
            self.assertEqual(raw.powertrain.isin(['HEV','PHEV','BEV']).sum(),agg.loc[agg.powertrain.isin(['HEV','PHEV','BEV']),'n'].sum())

    def test_sql_matches_dataframe(self):
        with sqlite3.connect(':memory:') as conn:
            self.df.to_sql('vehicles',conn,index=False)
            outputs={p.stem:pd.read_sql_query(p.read_text(encoding='utf-8-sig'),conn) for p in (ROOT/'sql').glob('*.sql')}
        annual=outputs['01_annual_efficiency'].set_index('year')
        expected=self.df[self.df.powertrain.eq('Gasoline')].groupby('year').comb08.mean()
        np.testing.assert_allclose(annual.mean_mpg,expected)
        np.testing.assert_allclose(annual.rolling_3_year_mpg,expected.rolling(3,min_periods=1).mean())
        shares=outputs['02_powertrain_shares'].groupby('year').record_share_pct.sum()
        np.testing.assert_allclose(shares,100)
        ranges=outputs['04_electric_range']
        sql_phev=ranges[ranges.powertrain.eq('PHEV')].set_index('year').mean_electricity_range_miles
        expected_phev=self.df[self.df.powertrain.eq('PHEV')].groupby('year').rangeA.mean()
        np.testing.assert_allclose(sql_phev,expected_phev)

    def test_temporal_model_outputs(self):
        metrics=json.loads((ROOT/'reports/modeling/metrics.json').read_text())
        self.assertLess(metrics['train_through'],metrics['test_years'][0])
        for file in ['mpg_predictions.csv','electrification_predictions.csv']:
            predictions=pd.read_csv(ROOT/'reports/modeling'/file)
            self.assertTrue(predictions.year.between(*metrics['test_years']).all())
            self.assertTrue(predictions.id.is_unique)
        forecast=pd.read_csv(ROOT/'reports/modeling/forecast_scenarios.csv')
        self.assertEqual(len(forecast),5)
        self.assertTrue(forecast.electrified_record_share_scenario.between(0,1).all())
        self.assertTrue(np.isfinite(forecast.select_dtypes('number')).all().all())
        self.assertEqual(metrics,self.payload['metrics'])
        forbidden={'powertrain','fuelType1','fuelType2','atvType','comb08','phevComb','range'}
        self.assertFalse(forbidden.intersection(metrics['electrification_classification']['features']))

    def test_notebooks_executed_without_errors(self):
        for path in (ROOT/'notebooks').glob('*.ipynb'):
            notebook=nbformat.read(path,as_version=4)
            nbformat.validate(notebook)
            for cell in notebook.cells:
                if cell.cell_type=='code' and cell.source.strip():
                    self.assertIsNotNone(cell.execution_count, f'{path.name} has an unexecuted cell')
                    self.assertFalse(any(o.output_type=='error' for o in cell.get('outputs',[])))


if __name__=='__main__':
    unittest.main()
