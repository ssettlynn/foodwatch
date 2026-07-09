"""
prepare_dashboard_data.py  (v2 — 3-model edition)
--------------------------------------------------
Dashboard data preparation — model ၃ ခုလုံး၏ 2024 predictions + SHAP + panel

Run:  python3 prepare_dashboard_data.py
"""
import os, joblib
import pandas as pd
import numpy as np
import shap

ROOT     = os.path.dirname(os.path.abspath(__file__))
MODELS   = os.path.join(ROOT, 'models')
PROCESSED= os.path.join(ROOT, 'data', 'processed')
OUT      = os.path.join(ROOT, 'dashboard_data')
os.makedirs(OUT, exist_ok=True)

cfg = joblib.load(os.path.join(MODELS, 'model_config.pkl'))
FEATURES = cfg['features']

MODEL_FILES = {                       # UI display name -> file
    'Random Forest':       'final_rf.pkl',
    'Logistic Regression': 'logreg.pkl',
    'Decision Tree':       'decision_tree.pkl',
}

# ===== 1. Panel (map + trends) =====
master = pd.read_csv(os.path.join(PROCESSED, 'master_dataset_2010_2023.csv'))
def to_tier(p):
    if pd.isna(p): return np.nan
    return 'Low' if p < 5 else ('Medium' if p < 15 else 'High')
master['risk_tier'] = master['pou'].apply(to_tier)
keep = ['country_iso','country_name','year','region','income_group',
        'pou','des_adequacy','cereal_import_dep','food_prod_var',
        'gdp_per_capita','gdp_growth','inflation_cpi','pop_growth','risk_tier']
master[keep].to_csv(os.path.join(OUT, 'panel.csv'), index=False)
print(f"[1] panel.csv  {master.shape[0]} rows")

# ===== 2. 2024 predictions — model ၃ ခုလုံး (long format) =====
demo = pd.read_csv(os.path.join(PROCESSED, 'features_2023_demo.csv'))
all_preds = []
for mname, fn in MODEL_FILES.items():
    pipe  = joblib.load(os.path.join(MODELS, fn))
    proba = pipe.predict_proba(demo[FEATURES])
    classes = list(pipe.named_steps['clf'].classes_)
    d = demo[['country_iso','country_name','region','income_group','pou']].copy()
    d['model']          = mname
    d['pred_next_tier'] = pipe.predict(demo[FEATURES])
    for i, c in enumerate(classes):
        d[f'proba_{c}'] = proba[:, i].round(4)
    d['pred_confidence'] = proba.max(axis=1).round(4)
    all_preds.append(d)
    print(f"[2] {mname:20s} High={ (d['pred_next_tier']=='High').sum():3d}")
pd.concat(all_preds).to_csv(os.path.join(OUT, 'predictions_2024.csv'), index=False)

# ===== 3. SHAP (Random Forest only — TreeExplainer) =====
rf_pipe = joblib.load(os.path.join(MODELS, 'final_rf.pkl'))
imputer, rf = rf_pipe.named_steps['imputer'], rf_pipe.named_steps['clf']
classes = list(rf.classes_)
X_demo  = pd.DataFrame(imputer.transform(demo[FEATURES]), columns=FEATURES)
explainer = shap.TreeExplainer(rf)
sv = explainer.shap_values(X_demo)
hp = classes.index('High')
rows = []
for i in range(len(demo)):
    one = sv[hp][i] if isinstance(sv, list) else sv[i, :, hp]
    for f, val in zip(FEATURES, one):
        rows.append([demo.iloc[i]['country_iso'], f, round(float(val), 5),
                     round(float(X_demo.iloc[i][f]), 3)])
pd.DataFrame(rows, columns=['country_iso','feature','shap_high','feat_value']) \
  .to_csv(os.path.join(OUT, 'shap_high.csv'), index=False)
base = explainer.expected_value[hp] if hasattr(explainer.expected_value, '__len__') else explainer.expected_value
pd.DataFrame([{'base_value_high': float(base)}]).to_csv(os.path.join(OUT, 'shap_base.csv'), index=False)
print(f"[3] shap_high.csv  base={float(base):.3f}")

# ===== 4. Latest features (what-if tool defaults) =====
demo.to_csv(os.path.join(OUT, 'latest_features_2023.csv'), index=False)
print(f"[4] latest_features_2023.csv  {demo.shape[0]} countries")

# ===== 5. Model comparison =====
mc = os.path.join(PROCESSED, 'model_comparison.csv')
if os.path.exists(mc):
    pd.read_csv(mc).to_csv(os.path.join(OUT, 'model_comparison.csv'), index=False)
    print("[5] model_comparison.csv copied")

print("\n✅ Dashboard data ready:", OUT)
