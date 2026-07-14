"""
prepare_dashboard_data.py  (v5)
-------------------------------
Regenerates foodwatch_data.js for the website from the ML pipeline outputs.

Expected layout (run from the project root in PyCharm):
    ./models/                 rf_best_1yr.pkl, rf_best_5yr.pkl, logreg_1yr.pkl,
                              dtree_1yr.pkl, model_config.pkl
    ./data/processed/         master_dataset_2010_2023.csv, features_lagged_*.csv,
                              features_2023_demo.csv, transactions_apriori.csv

Run:  python3 prepare_dashboard_data.py
Output: ./foodwatch_data.js
"""
import os, json
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (f1_score, recall_score, accuracy_score,
                             mean_absolute_error, r2_score)

ROOT      = os.path.dirname(os.path.abspath(__file__))
MODELS    = os.path.join(ROOT, 'models')
PROCESSED = os.path.join(ROOT, 'data', 'processed')
OUT       = os.path.join(ROOT, 'foodwatch_data.js')
YEARS     = list(range(2010, 2024))

# ---------- load master and build features ----------
m = pd.read_csv(os.path.join(PROCESSED, 'master_dataset_2010_2023.csv'))
m = m.sort_values(['country_iso', 'year']).reset_index(drop=True)

def to_tier(p):
    if pd.isna(p): return None
    return 'Low' if p < 5 else ('Medium' if p < 15 else 'High')
m['tier'] = m['pou'].apply(to_tier)

m['pou_change'] = m.groupby('country_iso')['pou'].diff()
m['covid_flag'] = m['year'].isin([2020, 2021]).astype(int)

def slope3(s):
    out = s.copy() * np.nan
    for i in range(len(s)):
        w = s.iloc[max(0, i-2):i+1].dropna()
        if len(w) >= 2:
            out.iloc[i] = np.polyfit(range(len(w)), w.values, 1)[0]
    return out
m['pou_trend3']    = m.groupby('country_iso')['pou'].transform(slope3)
m['des_change']    = m.groupby('country_iso')['des_adequacy'].diff()
m['infl_change']   = m.groupby('country_iso')['inflation_cpi'].diff()
m['pou_vs_region'] = m['pou'] - m.groupby(['region', 'year'])['pou'].transform('mean')

FEAT14 = ['pou','des_adequacy','cereal_import_dep','food_prod_var','gdp_per_capita',
          'gdp_growth','inflation_cpi','pop_growth','pou_change','covid_flag',
          'pou_trend3','des_change','infl_change','pou_vs_region']

# ---------- SERIES / META / GLOB ----------
cols = ['pou','des_adequacy','cereal_import_dep','food_prod_var',
        'gdp_per_capita','gdp_growth','inflation_cpi','pop_growth']
SERIES, META = {}, {}
for iso, g in m.groupby('country_iso'):
    g = g.set_index('year').reindex(YEARS)
    META[iso] = {'n': g['country_name'].dropna().iloc[0],
                 'r': g['region'].dropna().iloc[0],
                 'g': g['income_group'].dropna().iloc[0]}
    d = {'y': YEARS}
    for c in cols:
        d[c] = [None if pd.isna(v) else round(float(v), 2) for v in g[c]]
    d['tier'] = [v if isinstance(v, str) else None for v in g['tier']]
    SERIES[iso] = d

gp = m.groupby('year')['pou'].mean().reindex(YEARS)
regions = {r: [None if pd.isna(v) else round(float(v), 2)
               for v in gr.groupby('year')['pou'].mean().reindex(YEARS)]
           for r, gr in m.groupby('region')}
inc23 = m[m['year'] == 2023].groupby('income_group')['pou'].median().round(1).to_dict()
GLOB = {'years': YEARS, 'global_pou': [round(float(v), 2) for v in gp],
        'regions': regions, 'income_2023': {k: float(v) for k, v in inc23.items()}}

# ---------- multi-indicator forecasts (v5) ----------
IND = {'pou': 'Hunger level', 'gdp_per_capita': 'Income per person',
       'inflation_cpi': 'Inflation', 'des_adequacy': 'Food supply adequacy',
       'pop_growth': 'Population growth'}
FCMETRICS, forecasters = [], {}
for col, label in IND.items():
    row = {'ind': col, 'label': label}
    for h in (1, 5):
        m[f'{col}_t{h}'] = m.groupby('country_iso')[col].shift(-h)
        d = m.dropna(subset=[col, f'{col}_t{h}'])
        cut, tf = (2017, 2020) if h == 1 else (2014, 2017)
        tr, te = d[d.year <= cut], d[d.year >= tf]
        base = mean_absolute_error(te[f'{col}_t{h}'], te[col])
        p = Pipeline([('i', SimpleImputer(strategy='median')),
                      ('r', RandomForestRegressor(n_estimators=250, max_depth=12,
                            min_samples_leaf=3, random_state=42, n_jobs=-1))])
        p.fit(tr[FEAT14], tr[f'{col}_t{h}'])
        pr = p.predict(te[FEAT14])
        row[f'mae{h}']  = round(mean_absolute_error(te[f'{col}_t{h}'], pr), 2)
        row[f'r2_{h}']  = round(r2_score(te[f'{col}_t{h}'], pr), 2)
        row[f'base{h}'] = round(base, 2)
        # production forecaster: refit on all labelled rows
        dall = m.dropna(subset=[col, f'{col}_t{h}'])
        pf = Pipeline([('i', SimpleImputer(strategy='median')),
                       ('r', RandomForestRegressor(n_estimators=250, max_depth=12,
                             min_samples_leaf=3, random_state=42, n_jobs=-1))])
        pf.fit(dall[FEAT14], dall[f'{col}_t{h}'])
        forecasters[(col, h)] = pf
    FCMETRICS.append(row)

FORE = {}
for iso, g in m.groupby('country_iso'):
    r23 = g[g['year'] == 2023]
    if len(r23) == 0 or r23[FEAT14].isna().all(axis=1).iloc[0]:
        continue
    fc = {}
    for col in IND:
        now = r23[col].values[0]
        fc[col] = {'now': None if pd.isna(now) else round(float(now), 1),
                   'y2024': round(float(forecasters[(col, 1)].predict(r23[FEAT14])[0]), 1),
                   'y2028': round(float(forecasters[(col, 5)].predict(r23[FEAT14])[0]), 1)}
    FORE[iso] = fc

# ---------- tier predictions (v4 models) ----------
cfg = joblib.load(os.path.join(MODELS, 'model_config.pkl'))
CF = cfg['features']
demo = pd.read_csv(os.path.join(PROCESSED, 'features_2023_demo.csv'))
PRED = {}
for key, short in [('logreg', 'lr'), ('dtree', 'dt'), ('rf_best', 'rf')]:
    pipe = joblib.load(os.path.join(MODELS, f'{key}_1yr.pkl'))
    classes = list(pipe.named_steps['clf'].classes_); hi = classes.index('High')
    pred, proba = pipe.predict(demo[CF]), pipe.predict_proba(demo[CF])
    for i, iso in enumerate(demo['country_iso']):
        PRED.setdefault(iso, {})[short] = {'t': pred[i],
            'c': round(float(proba[i].max()), 3), 'pH': round(float(proba[i][hi]), 3)}

rf5 = joblib.load(os.path.join(MODELS, 'rf_best_5yr.pkl'))
OUTLOOK = {}
recent = m[m['year'].between(2019, 2023)].dropna(subset=['pou'])
p5, pr5 = rf5.predict(recent[CF]), rf5.predict_proba(recent[CF])
for i, (_, r) in enumerate(recent.iterrows()):
    OUTLOOK.setdefault(r['country_iso'], {})[int(r['year']) + 5] = \
        {'t': p5[i], 'c': round(float(pr5[i].max()), 2)}

# ---------- tier metrics / SHAP / rules / logreg params ----------
METRICS = []
for h, tcol in [('1yr', 'risk_tier_next1'), ('5yr', 'risk_tier_next5')]:
    df = pd.read_csv(os.path.join(PROCESSED, f'features_lagged_{h}.csv'))
    te = df[df['split'] == 'test']; y = te[tcol]
    METRICS.append({'h': h, 'model': 'Persistence',
        'f1': round(f1_score(y, te['risk_tier_current'], average='macro'), 3),
        'hr': round(recall_score(y, te['risk_tier_current'], labels=['High'], average='macro'), 3),
        'acc': round(accuracy_score(y, te['risk_tier_current']), 3)})
    for key, nm in [('logreg', 'Logistic Regression'), ('dtree', 'Decision Tree'),
                    ('rf_best', 'Random Forest')]:
        p = joblib.load(os.path.join(MODELS, f'{key}_{h}.pkl')).predict(te[CF])
        METRICS.append({'h': h, 'model': nm,
            'f1': round(f1_score(y, p, average='macro'), 3),
            'hr': round(recall_score(y, p, labels=['High'], average='macro'), 3),
            'acc': round(accuracy_score(y, p), 3)})

TASKS = [
 {'type': 'Classification', 'name': 'Risk tier', 'note': 'Low / Medium / High next year',
  'score': 0.958, 'metric': 'macro-F1', 'baseline': 0.957},
 {'type': 'Regression', 'name': 'Hunger level', 'note': 'The actual undernourishment %',
  'score': 0.50, 'metric': 'MAE (pp)', 'baseline': 0.52},
 {'type': 'Multi-target', 'name': '5 indicators', 'note': 'Future values, 1 & 5 years',
  'score': 0.99, 'metric': 'best R2', 'baseline': None},
]

import shap
def global_importance(h):
    pipe = joblib.load(os.path.join(MODELS, f'rf_best_{h}.pkl'))
    imp, clf = pipe.named_steps['imp'], pipe.named_steps['clf']
    df = pd.read_csv(os.path.join(PROCESSED, f'features_lagged_{h}.csv'))
    te = df[df['split'] == 'test']
    X = pd.DataFrame(imp.transform(te[CF]), columns=CF)
    sv = np.array(shap.TreeExplainer(clf).shap_values(X))
    fa = [i for i in range(sv.ndim) if sv.shape[i] == len(CF)][0]
    other = tuple(i for i in range(sv.ndim) if i != fa)
    return {f: round(float(v), 4) for f, v in zip(CF, np.abs(sv).mean(axis=other))}
SHAP = {'1yr': global_importance('1yr'), '5yr': global_importance('5yr')}

from mlxtend.frequent_patterns import apriori, association_rules
tx = pd.read_csv(os.path.join(PROCESSED, 'transactions_apriori.csv')) \
       .drop(columns=['country_iso', 'year']).astype(bool)
fi = apriori(tx, min_support=0.05, use_colnames=True)
rr = association_rules(fi, metric='lift', min_threshold=1.2)
rr = rr[rr['consequents'].apply(lambda s: len(s) == 1)]
rr['con'] = rr['consequents'].apply(lambda s: list(s)[0])
rr['ant'] = rr['antecedents'].apply(lambda s: ' + '.join(sorted(s)))
RULES = [{'ant': x['ant'], 'con': x['con'], 'lift': round(x['lift'], 2),
          'conf': round(x['confidence'], 2), 'supp': round(x['support'], 3)}
         for _, x in rr[rr['con'].isin(['HUNGER_HIGH', 'HUNGER_LOW'])]
                      .sort_values('lift', ascending=False).head(8).iterrows()]

lr = joblib.load(os.path.join(MODELS, 'logreg_1yr.pkl'))
LOGREG = {'features': CF,
 'medians': [float(v) for v in lr.named_steps['imp'].statistics_],
 'mean':    [float(v) for v in lr.named_steps['sc'].mean_],
 'scale':   [float(v) for v in lr.named_steps['sc'].scale_],
 'coef':    [[float(c) for c in row] for row in lr.named_steps['clf'].coef_],
 'intercept': [float(v) for v in lr.named_steps['clf'].intercept_],
 'classes': list(lr.named_steps['clf'].classes_)}

FW = {'SERIES': SERIES, 'META': META, 'GLOB': GLOB, 'PRED': PRED,
      'OUTLOOK': OUTLOOK, 'FORE': FORE, 'FCMETRICS': FCMETRICS,
      'SHAP': SHAP, 'METRICS': METRICS, 'TASKS': TASKS, 'RULES': RULES,
      'LOGREG': LOGREG,
      'NICE': {'pou': 'Hunger level', 'des_adequacy': 'Food supply adequacy',
               'cereal_import_dep': 'Import dependence', 'food_prod_var': 'Supply stability',
               'gdp_per_capita': 'Income per person', 'gdp_growth': 'Economic growth',
               'inflation_cpi': 'Inflation', 'pop_growth': 'Population growth',
               'pou_change': 'Hunger momentum', 'covid_flag': 'Pandemic year'},
      'UNIT': {'pou': '%', 'gdp_per_capita': '$', 'inflation_cpi': '%',
               'des_adequacy': '%', 'pop_growth': '%'}}

with open(OUT, 'w') as f:
    f.write('const FW=' + json.dumps(FW, separators=(',', ':')) + ';')
print(f'written {OUT}  ({os.path.getsize(OUT)/1e6:.2f} MB)')
print(f'FORE countries: {len(FORE)} | FCMETRICS: {len(FCMETRICS)} | RULES: {len(RULES)}')
