# 🌾 FoodWatch — Predicting Hunger Before It Happens

> An interactive web platform that predicts national food-security risk **one year ahead**,
> built on 100% open data from the UN FAO and the World Bank.

**Live site:** `https://<your-username>.github.io/foodwatch/` *(enable GitHub Pages — see below)*

![status](https://img.shields.io/badge/status-active-1A9E77)
![data](https://img.shields.io/badge/data-FAOSTAT%20%2B%20World%20Bank-0F5FA8)
![models](https://img.shields.io/badge/models-LogReg%20·%20DT%20·%20RF-E6A817)
![license](https://img.shields.io/badge/license-MIT-blue)

---

## What it does

- 🗺️ **World & Patterns** — an animated choropleth of 14 years of undernourishment (2010–2023),
  plus the four big patterns that explain global hunger
- 📖 **Country Story** — auto-written country summaries, trends vs. regional averages,
  year-by-year risk history
- 🔮 **Forecast 2024** — next-year risk-tier predictions from three switchable models,
  with per-country confidence and CSV export
- 🧪 **What-If Lab** — a live Logistic Regression running **entirely in the browser**:
  drag sliders to change a country's economy and watch its predicted risk respond
- 🧠 **Explainability** — SHAP-based "why the model thinks so" for every forecast

No backend. No API keys. The entire site is static HTML/CSS/JS — the trained model's
parameters are exported to JSON and evaluated client-side.

## The data

| Source | What we use | Link |
|---|---|---|
| **FAOSTAT** — Suite of Food Security Indicators | Prevalence of undernourishment (SDG 2.1.1), dietary energy supply adequacy, cereal import dependency, food supply variability | [fao.org/faostat](https://www.fao.org/faostat/en/#data/FS) |
| **World Bank** — WDI | GDP per capita, GDP growth, inflation (CPI), population growth | [data.worldbank.org](https://data.worldbank.org) |

**Panel:** 168 countries × 14 years (2010–2023) → 2,160 country-year training pairs.
**Target:** next-year risk tier from FAO severity bands — Low (<5%), Medium (5–15%), High (≥15%).

## The models

| Model | Macro-F1 (test 2020–2022) | Notes |
|---|---|---|
| Persistence baseline | 0.957 | "same tier as last year" |
| **Logistic Regression** | **0.963** | powers the in-browser What-If Lab |
| Decision Tree | 0.954 | interpretable middle |
| **Random Forest** | **0.962** | default forecast model + SHAP |

Key result: on unseen shock years (COVID aftermath + 2022 price shock),
**no high-risk country was ever misclassified as low-risk** — the worst possible
error for an early-warning system never occurred in testing.

Leakage prevention: chronological train/test split (2010–2019 vs 2020–2022),
GroupKFold by country for tuning, all preprocessing inside sklearn Pipelines.

## Run locally

```bash
git clone https://github.com/<your-username>/foodwatch.git
cd foodwatch
python3 -m http.server 8000
# open http://localhost:8000
```

Or simply double-click `index.html` — the site has zero dependencies beyond a browser.

## Deploy on GitHub Pages

1. Push this repo to GitHub
2. **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save**
3. Your site goes live at `https://<your-username>.github.io/foodwatch/`

## Project structure

```
foodwatch/
├── index.html            # Home — hero, stats, entry points
├── explore.html          # World map + the four big patterns
├── country.html          # Country stories + 2024 outlook
├── forecast.html         # 3-model forecast center
├── lab.html              # In-browser what-if simulator
├── learn.html            # Methodology, sources, videos, FAQ
├── style.css             # Shared design system
├── fw.js                 # Shared JS (nav, constants, reveal animations)
├── foodwatch_data.js     # All data + exported model parameters (generated)
├── plotly.min.js         # Charting library (vendored for offline use)
├── assets/               # Hand-crafted SVG artwork + project figures
├── app.py                # Optional: Streamlit dashboard variant
└── prepare_dashboard_data.py  # Regenerates data from the ML pipeline
```

## Methodology (short version)

KDD pipeline: FAOSTAT + World Bank CSV → ISO3 standardisation & merge →
country-wise interpolation (gap ≤ 2 yr, flagged) → feature engineering
(YoY hunger momentum, COVID flag, **lag target** `shift(-1)`) → EDA (14 charts) →
3 classifiers with GroupKFold tuning → chronological hold-out evaluation →
SHAP explainability → this site.

Built as an academic Data Mining course project, 2026.

## License

MIT — see [LICENSE](LICENSE). Data © FAO / World Bank under their open-data terms.
