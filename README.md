<div align="center">

# 🌾 FoodWatch

### An Explainable Early-Warning System for National Food-Security Risk

Predicting where national hunger is heading — from open UN & World Bank data, with machine learning you can actually understand.

[![Live Demo](https://img.shields.io/badge/▶_Live_Demo-GitHub_Pages-1A9E77?style=for-the-badge)](https://YOUR_USERNAME.github.io/foodwatch/)

![status](https://img.shields.io/badge/status-active-1A9E77)
![data](https://img.shields.io/badge/data-FAOSTAT_+_World_Bank-0F5FA8)
![models](https://img.shields.io/badge/models-LogReg_·_Tree_·_RF-E6A817)
![explainability](https://img.shields.io/badge/explainability-SHAP_+_Apriori-CC79A7)
![license](https://img.shields.io/badge/license-MIT-blue)

</div>

---

## Overview

**FoodWatch** turns open socioeconomic data into a forward-looking signal: it predicts each country's
food-security **risk tier** (Low / Medium / High) one and five years ahead, explains *why* with SHAP,
and surfaces hidden condition-patterns with association-rule mining — all in an interactive, zero-backend web app.

> Built as an academic **Data Mining** course project (2026). 100% open data. The entire site is static
> HTML/CSS/JS — the trained model's parameters are exported to JSON and evaluated **in the browser**.

## ✨ Features

| Page | What it does |
|---|---|
| 🗺️ **World & Patterns** | Animated choropleth of 14 years of undernourishment + the four big patterns behind global hunger |
| 📖 **Country Story** | Auto-written country summaries, trend-vs-region charts, and a 2024–2028 outlook timeline |
| 🔮 **Forecast** | Next-year risk-tier predictions from three switchable models, per-country confidence, CSV export |
| 🧪 **Model Lab** | Accuracy by horizon, overfitting diagnosis, SHAP feature importance, and mined association rules |
| 🎛️ **What-If Lab** | A live model in the browser — drag sliders to change a country's economy and watch its risk respond |
| 📚 **Learn** | Methodology, official sources, UN/FAO videos, and an honest FAQ |

## 📊 Results

Models are evaluated on a **chronological hold-out test set** (data never seen during training).

| Model | Macro-F1 (1-yr) | Macro-F1 (5-yr) |
|---|:---:|:---:|
| Persistence baseline | 0.957 | 0.834 |
| Logistic Regression | 0.934 | 0.811 |
| Decision Tree | 0.927 | 0.765 |
| **Random Forest** | **0.958** | **0.831** |

**Headline finding:** across every model and both horizons, **no high-risk country was ever misclassified
as low-risk** — the worst possible error for an early-warning system never occurred on the test data.

**Leakage prevention:** chronological train/validation/test split · GroupKFold by country for tuning ·
all preprocessing inside scikit-learn Pipelines (fit on train only).

## 🗂️ Data

| Source | Indicators used |
|---|---|
| **[FAOSTAT](https://www.fao.org/faostat/en/#data/FS)** — Suite of Food Security Indicators | Prevalence of undernourishment (SDG 2.1.1), dietary energy supply adequacy, cereal import dependency, food supply variability |
| **[World Bank WDI](https://data.worldbank.org)** | GDP per capita, GDP growth, inflation (CPI), population growth |

**Panel:** 182 countries × 14 years (2010–2023) · **Target tiers:** Low (<5%), Medium (5–15%), High (≥15%) — FAO severity bands. No API keys — official bulk CSV downloads only.

## 🚀 Run locally

```bash
git clone https://github.com/YOUR_USERNAME/foodwatch.git
cd foodwatch
python3 -m http.server 8000
# then open http://localhost:8000
```

Or just double-click `index.html` — the site has zero dependencies beyond a browser.

## 🌐 Deploy (free, on GitHub Pages)

1. Push this repo to GitHub.
2. **Settings → Pages → Source: _Deploy from a branch_ → `main` / `(root)` → Save.**
3. Live in ~2 minutes at `https://YOUR_USERNAME.github.io/foodwatch/`.

## 🧱 Tech stack

`Python` · `pandas` · `scikit-learn` · `SHAP` · `mlxtend` (Apriori) · `Plotly.js` · vanilla `HTML/CSS/JS` · GitHub Pages

## 📁 Project structure

```
foodwatch/
├── index.html           # Home
├── explore.html         # World map + patterns
├── country.html         # Country stories + 2024–2028 outlook
├── forecast.html        # Multi-model forecast center
├── modellab.html        # Metrics, overfitting, SHAP, association rules
├── lab.html             # In-browser what-if simulator
├── learn.html           # Methodology, sources, FAQ
├── style.css            # Shared design system
├── fw.js                # Shared JS (nav, constants, animations)
├── foodwatch_data.js    # Data + exported model parameters (generated)
├── plotly.min.js        # Charting library (vendored, offline)
├── assets/              # Hand-crafted SVG artwork + figures
└── notebooks/           # KDD pipeline (01 collect → 07 SHAP)
```

## 🔬 Methodology

**KDD pipeline:** FAOSTAT + World Bank CSV → ISO3 standardisation & merge → country-wise interpolation
(gap ≤ 2 yr, flagged) → feature engineering (hunger momentum, COVID flag, **lag targets** `shift(-1)` &
`shift(-5)`) → EDA (14 charts) + **Apriori** association mining → 3 classifiers × 2 horizons with a
documented tuning journey → chronological test evaluation (overfitting, threshold tuning, bootstrap CI) →
**SHAP** explainability → this site.

## 📄 License

[MIT](LICENSE) · Data © FAO / World Bank under their respective open-data terms.

<div align="center">
<sub>Academic Data Mining project · 2026 · Open data · Built to be understood, not just accurate.</sub>
</div>
