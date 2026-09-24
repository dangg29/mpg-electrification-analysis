"""Train reproducible, temporally evaluated models and export static results."""
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, OptimizeWarning
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score, accuracy_score, balanced_accuracy_score, roc_auc_score, average_precision_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/modeling'
SEED = 42


def preprocessor(numeric, categorical):
    return ColumnTransformer([
        ('numeric', make_pipeline(SimpleImputer(strategy='median'), StandardScaler()), numeric),
        ('category', make_pipeline(SimpleImputer(strategy='most_frequent'), OneHotEncoder(handle_unknown='ignore', sparse_output=False)), categorical),
    ])


def logistic_curve(year, ceiling, rate, midpoint):
    return ceiling / (1 + np.exp(np.clip(-rate * (np.asarray(year) - midpoint), -700, 700)))


def fit_curve(years, shares):
    with warnings.catch_warnings():
        warnings.simplefilter('error', OptimizeWarning)
        parameters, _ = curve_fit(logistic_curve, years, shares, p0=[0.8, 0.2, 2030], bounds=([0.01, 0.001, 1990], [1.0, 2.0, 2100]), maxfev=20000)
    return parameters


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(ROOT / 'data/processed/vehicles_features.parquet')
    # Conservatively exclude the newest observed model year; completeness is unknown.
    excluded = int(df.year.max())
    last = excluded - 1
    test_start = last - 2
    base = df[df.year <= last].copy()
    results = {'seed': SEED, 'excluded_latest_year': excluded, 'train_through': test_start - 1, 'test_years': [test_start, last], 'forecast_through': last + 5}

    gas = base[base.powertrain.eq('Gasoline')].dropna(subset=['comb08'])
    numeric = ['year', 'displ', 'cylinders', 'num_gears']
    categorical = ['drive', 'segment', 'transmission_type']
    features = numeric + categorical
    train, test = gas[gas.year < test_start], gas[gas.year >= test_start]
    reg = make_pipeline(preprocessor(numeric, categorical), RandomForestRegressor(n_estimators=150, min_samples_leaf=5, max_depth=18, random_state=SEED, n_jobs=2))
    reg.fit(train[features], train.comb08)
    pred = reg.predict(test[features])
    dummy = DummyRegressor().fit(train[features], train.comb08).predict(test[features])
    results['mpg_regression'] = {'train_records': len(train), 'test_records': len(test), 'features': features, 'mae': mean_absolute_error(test.comb08, pred), 'rmse': root_mean_squared_error(test.comb08, pred), 'r2': r2_score(test.comb08, pred), 'baseline_mae': mean_absolute_error(test.comb08, dummy)}
    pd.DataFrame({'id': test.id, 'year': test.year, 'actual_mpg': test.comb08, 'predicted_mpg': pred}).to_csv(OUT / 'mpg_predictions.csv', index=False)
    importance = pd.Series(reg[-1].feature_importances_, index=reg[0].get_feature_names_out()).sort_values(ascending=False)
    importance.rename('importance').to_csv(OUT / 'regression_feature_importance.csv', index_label='feature')
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(test.comb08, pred, alpha=.12, s=10)
    limits = [min(test.comb08.min(), pred.min()), max(test.comb08.max(), pred.max())]
    ax.plot(limits, limits, '--', color='black')
    ax.set(xlabel='Actual combined MPG', ylabel='Predicted combined MPG', title=f'Gasoline MPG: held-out model years {test_start}-{last}')
    fig.tight_layout(); fig.savefig(OUT / 'mpg_predictions.png', dpi=150); plt.close(fig)

    # Deliberately omit fuel, engine and efficiency fields that reveal the target.
    numeric_c, category_c = ['year'], ['make', 'segment', 'drive']
    features_c = numeric_c + category_c
    base['is_electrified'] = base.powertrain.isin(['HEV', 'PHEV', 'BEV']).astype(int)
    train_c, test_c = base[base.year < test_start], base[base.year >= test_start]
    classifier = make_pipeline(preprocessor(numeric_c, category_c), LogisticRegression(max_iter=2000, class_weight='balanced', random_state=SEED))
    classifier.fit(train_c[features_c], train_c.is_electrified)
    probs = classifier.predict_proba(test_c[features_c])[:, 1]
    labels = (probs >= .5).astype(int)
    dummy_c = DummyClassifier(strategy='most_frequent').fit(train_c[features_c], train_c.is_electrified).predict(test_c[features_c])
    results['electrification_classification'] = {'train_records': len(train_c), 'test_records': len(test_c), 'features': features_c, 'threshold': .5, 'accuracy': accuracy_score(test_c.is_electrified, labels), 'balanced_accuracy': balanced_accuracy_score(test_c.is_electrified, labels), 'roc_auc': roc_auc_score(test_c.is_electrified, probs), 'average_precision': average_precision_score(test_c.is_electrified, probs), 'test_prevalence': float(test_c.is_electrified.mean()), 'baseline_accuracy': accuracy_score(test_c.is_electrified, dummy_c), 'baseline_balanced_accuracy': balanced_accuracy_score(test_c.is_electrified, dummy_c), 'confusion_matrix': confusion_matrix(test_c.is_electrified, labels, labels=[0, 1]).tolist()}
    pd.DataFrame({'id': test_c.id, 'year': test_c.year, 'actual_electrified': test_c.is_electrified, 'probability': probs, 'predicted_electrified': labels}).to_csv(OUT / 'electrification_predictions.csv', index=False)

    annual = gas.groupby('year').comb08.agg(['mean', 'count'])
    # Fixed trailing ten-year linear fit, evaluated on three unseen years.
    hist = annual.loc[test_start - 10:test_start - 1]
    holdout = annual.loc[test_start:last]
    fit = np.polyfit(hist.index - hist.index.min(), hist['mean'], 1)
    pred_holdout = np.polyval(fit, holdout.index - hist.index.min())
    results['mpg_forecast'] = {'method': 'linear trend over previous 10 annual means', 'holdout_mae': mean_absolute_error(holdout['mean'], pred_holdout), 'last_value_baseline_mae': mean_absolute_error(holdout['mean'], np.repeat(hist['mean'].iloc[-1], len(holdout)))}
    final_hist = annual.loc[last - 9:last]
    final_fit = np.polyfit(final_hist.index - final_hist.index.min(), final_hist['mean'], 1)
    future = np.arange(last + 1, last + 6)
    forecast = np.polyval(final_fit, future - final_hist.index.min())

    share = base.groupby('year').is_electrified.mean().loc[2000:last]
    curve_train = share.loc[:test_start - 1]
    curve_parameters = fit_curve(curve_train.index, curve_train.values)
    predicted_share = logistic_curve(holdout.index, *curve_parameters)
    final_parameters = fit_curve(share.index, share.values)
    results['electrification_s_curve'] = {'definition': 'HEV/PHEV/BEV share of database records, not sales adoption', 'holdout_mae_percentage_points': mean_absolute_error(share.loc[test_start:last], predicted_share) * 100, 'last_value_baseline_mae_percentage_points': mean_absolute_error(share.loc[test_start:last], np.repeat(curve_train.iloc[-1], len(holdout))) * 100, 'ceiling': float(final_parameters[0]), 'growth_rate': float(final_parameters[1]), 'midpoint_year': float(final_parameters[2]), 'ceiling_at_bound': bool(np.isclose(final_parameters[0], 1, atol=.001))}
    future_share = logistic_curve(future, *final_parameters)
    pd.DataFrame({'year': future, 'gasoline_mpg_scenario': forecast, 'electrified_record_share_scenario': future_share}).to_csv(OUT / 'forecast_scenarios.csv', index=False)
    pd.DataFrame({'year': holdout.index, 'actual_gasoline_mpg': holdout['mean'], 'predicted_gasoline_mpg': pred_holdout, 'actual_electrified_share': share.loc[test_start:last], 'predicted_electrified_share': predicted_share}).to_csv(OUT / 'forecast_backtest.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(annual.index, annual['mean'], label='Observed annual mean')
    axes[0].plot(future, forecast, '--', label='Linear scenario')
    axes[0].set(title='Gasoline efficiency', ylabel='Combined MPG', xlabel='Model year')
    axes[1].plot(share.index, share * 100, label='Observed record share')
    axes[1].plot(share.index, logistic_curve(share.index, *final_parameters) * 100, label='Fitted S-curve')
    axes[1].plot(future, future_share * 100, '--', label='S-curve scenario')
    axes[1].set(title='Electrified configurations', ylabel='Share of records (%)', xlabel='Model year', ylim=(0, 100))
    for ax in axes: ax.legend(fontsize=8); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(OUT / 'forecast_scenarios.png', dpi=150); plt.close(fig)
    (OUT / 'metrics.json').write_text(json.dumps(results, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2))
    return results


if __name__ == '__main__':
    run()
