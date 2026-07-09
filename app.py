"""
app.py — FoodWatch Dashboard  (v3 — aligned with landing page, plain language)
==============================================================================
Design language = landing.html (navy→blue→teal, amber accents, serif headings).
Every chart has a one-line "What this shows" caption in plain English.
No raw column names anywhere — human labels only.

Run:  python3 -m streamlit run app.py
"""
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import joblib

st.set_page_config(page_title="FoodWatch Dashboard", page_icon="🌾",
                   layout="wide", initial_sidebar_state="collapsed")

HERE   = os.path.dirname(os.path.abspath(__file__))
DATA   = os.path.join(HERE, "dashboard_data")
MODELS = os.path.join(HERE, "models")
ASSETS = os.path.join(HERE, "assets")

TIER_COLORS = {"Low": "#1A9E77", "Medium": "#E6A817", "High": "#D64550"}
TIER_ORDER  = ["Low", "Medium", "High"]
BLUE, NAVY, TEAL, AMBER = "#0F5FA8", "#082A47", "#1A9E77", "#E6A817"

# ---- Plain-language labels (no raw column names shown to users) ----
LABEL = {
    'pou':               'Hunger level (% of people undernourished)',
    'des_adequacy':      'Food supply adequacy (%)',
    'cereal_import_dep': 'Cereal import dependence (%)',
    'food_prod_var':     'Food supply stability',
    'gdp_per_capita':    'Income per person (US$)',
    'gdp_growth':        'Economic growth (%)',
    'inflation_cpi':     'Inflation (%)',
    'pop_growth':        'Population growth (%)',
    'pou_change':        'Hunger trend — change vs last year',
    'covid_flag':        'Pandemic year',
}
FEATURES = list(LABEL.keys())
MODEL_FILES = {'Random Forest': 'final_rf.pkl',
               'Logistic Regression': 'logreg.pkl',
               'Decision Tree': 'decision_tree.pkl'}
TIER_MEANING = {"Low": "food access broadly secure",
                "Medium": "vulnerable — early action zone",
                "High": "serious hunger — urgent attention"}

# ────────────────── THEME (matches landing.html) ──────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');
.stApp {{ background:#F7F9FB; color:#13202E; font-family:'Inter',sans-serif; }}
h1,h2,h3 {{ font-family:'Source Serif 4',serif; color:#0B3D6E; }}
.hero {{ background:linear-gradient(120deg,{NAVY},{BLUE} 58%,{TEAL});
  margin:-4rem -4rem 1.4rem; padding:2.6rem 4rem 2.2rem; color:#fff; }}
.hero h1 {{ color:#fff; margin:0; font-size:2rem; }}
.hero p  {{ color:#D9E8F5; margin:.4rem 0 0; }}
.hero a  {{ color:{AMBER}; font-weight:700; text-decoration:none; }}
.card {{ background:#fff; border:1px solid #E3EAF1; border-radius:16px;
  padding:1.25rem 1.4rem; box-shadow:0 2px 10px rgba(16,42,67,.06); }}
.kpi-num {{ font-size:2.1rem; font-weight:700; font-family:'Source Serif 4'; }}
.kpi-lab {{ color:#5B6B7C; font-size:.8rem; text-transform:uppercase; letter-spacing:.6px; }}
.badge {{ padding:.22rem .75rem; border-radius:999px; font-weight:700; font-size:.85rem; color:white; }}
.explain {{ background:#EEF5FB; border-left:4px solid {BLUE}; border-radius:0 10px 10px 0;
  padding:.7rem 1rem; color:#2A4A66; font-size:.92rem; margin:.4rem 0 1.2rem; }}
.stTabs [data-baseweb="tab"] {{ font-weight:600; }}
#MainMenu, footer {{ visibility:hidden; }}
</style>
<div class="hero">
  <h1>🌾 FoodWatch Dashboard</h1>
  <p>Live maps, country stories and next-year forecasts — in plain language.
     &nbsp;·&nbsp; <a href="landing.html">← Back to the FoodWatch site</a></p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load(name): return pd.read_csv(os.path.join(DATA, name))
@st.cache_resource
def load_model(fn): return joblib.load(os.path.join(MODELS, fn))

panel  = load("panel.csv")
preds  = load("predictions_2024.csv")
latest = load("latest_features_2023.csv")

def explain(text):
    st.markdown(f"<div class='explain'>💡 <b>What this shows:</b> {text}</div>", unsafe_allow_html=True)

tabs = st.tabs(["🗺️ World Today", "📊 The Big Patterns", "🌏 Country Story", "🔮 2024 Forecast", "🧪 What-If Lab"])

# ══════════════════ TAB 1 — WORLD TODAY ══════════════════
with tabs[0]:
    c1, c2 = st.columns([1.1, 2.2])
    with c1:
        year = st.slider("Choose a year", 2010, 2023, 2023)
        d = panel[panel['year'] == year]
        prev = panel[panel['year'] == year-1] if year > 2010 else d
        hi, hip = int((d['risk_tier']=='High').sum()), int((prev['risk_tier']=='High').sum())
        arrow = "🔺" if hi > hip else ("🔻" if hi < hip else "▪️")
        st.markdown(f"<div class='card' style='margin-bottom:.7rem'>"
                    f"<div class='kpi-num' style='color:{TIER_COLORS['High']}'>{hi}</div>"
                    f"<div class='kpi-lab'>countries in serious hunger</div>"
                    f"<div style='color:#5B6B7C;font-size:.85rem'>{arrow} {abs(hi-hip)} vs {year-1}</div></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='card' style='margin-bottom:.7rem'>"
                    f"<div class='kpi-num'>{d['pou'].mean():.1f}%</div>"
                    f"<div class='kpi-lab'>average hunger level worldwide</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>"
                    f"<div class='kpi-num' style='color:{TEAL}'>{int((d['risk_tier']=='Low').sum())}</div>"
                    f"<div class='kpi-lab'>countries food-secure</div></div>", unsafe_allow_html=True)
    with c2:
        dm = d.dropna(subset=['risk_tier'])
        fig = px.choropleth(dm, locations="country_iso", color="risk_tier",
                            color_discrete_map=TIER_COLORS, category_orders={"risk_tier": TIER_ORDER},
                            hover_name="country_name",
                            hover_data={"pou": ":.1f", "country_iso": False},
                            labels={"pou": "Hunger level %", "risk_tier": "Risk"})
        fig.update_geos(showframe=False, projection_type="natural earth", landcolor="#EDF1F5",
                        bgcolor="rgba(0,0,0,0)")
        fig.update_layout(margin=dict(l=0, r=0, t=4, b=0), height=440, paper_bgcolor="rgba(0,0,0,0)",
                          legend=dict(orientation="h", y=-.04, title=""))
        st.plotly_chart(fig, use_container_width=True)
    explain(f"Each country is coloured by its hunger tier in {year}: "
            f"<b style='color:{TEAL}'>green = secure (under 5%)</b>, "
            f"<b style='color:{AMBER}'>amber = vulnerable (5–15%)</b>, "
            f"<b style='color:{TIER_COLORS['High']}'>red = serious (over 15%)</b>. Drag the slider to watch 14 years of change.")

# ══════════════════ TAB 2 — BIG PATTERNS (descriptive, easy) ══════════════════
with tabs[1]:
    st.markdown("### Four patterns that explain global hunger")

    p1, p2 = st.columns(2)
    with p1:
        g = panel.groupby('year')['pou'].mean().reset_index()
        f1 = px.area(g, x='year', y='pou', color_discrete_sequence=[BLUE],
                     labels={'pou': 'average hunger level (%)', 'year': ''})
        for xv, lab in [(2020, "COVID-19"), (2022, "Price shock")]:
            f1.add_vline(x=xv, line_dash="dash", line_color=TIER_COLORS['High'])
            f1.add_annotation(x=xv, y=g['pou'].max(), text=lab, showarrow=False,
                              font=dict(color=TIER_COLORS['High'], size=11))
        f1.update_layout(height=300, margin=dict(l=0,r=0,t=24,b=0), paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(0,0,0,0)", title="① The world was winning — then 2020 happened")
        st.plotly_chart(f1, use_container_width=True)
        explain("Hunger fell steadily for a decade, then COVID-19 and the 2022 price shock erased half that progress.")

        inc = panel[panel['year']==2023].groupby('income_group')['pou'].median().reindex(
            ['High income','Upper middle income','Lower middle income','Low income']).reset_index()
        inc.columns = ['Income group', 'Median hunger %']
        f3 = px.bar(inc, x='Income group', y='Median hunger %', color='Median hunger %',
                    color_continuous_scale=['#BFE3D6', TEAL, AMBER, TIER_COLORS['High']])
        f3.add_hline(y=15, line_dash="dash", line_color=TIER_COLORS['High'],
                     annotation_text="serious-hunger line")
        f3.update_layout(height=300, margin=dict(l=0,r=0,t=24,b=0), coloraxis_showscale=False,
                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                         title="③ Hunger follows income — structurally")
        st.plotly_chart(f3, use_container_width=True)
        explain("In the poorest countries the <b>typical</b> country sits above the serious-hunger line — hunger isn't random, it's structural.")

    with p2:
        regs = panel.groupby(['region','year'])['pou'].mean().reset_index()
        f2 = px.line(regs, x='year', y='pou', color='region',
                     labels={'pou': 'average hunger level (%)', 'year': '', 'region': ''},
                     color_discrete_sequence=[TIER_COLORS['High'], AMBER, BLUE, TEAL, '#CC79A7', '#8B93A7', '#444'])
        f2.update_layout(height=300, margin=dict(l=0,r=0,t=24,b=0), paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(0,0,0,0)", title="② Where hunger lives",
                         legend=dict(font=dict(size=9)))
        st.plotly_chart(f2, use_container_width=True)
        explain("Sub-Saharan Africa carries the highest burden — and is the only region back near its 2010 level after the shocks.")

        d23 = panel[panel['year']==2023].dropna(subset=['gdp_per_capita','pou','risk_tier'])
        f4 = px.scatter(d23, x='gdp_per_capita', y='pou', color='risk_tier', log_x=True,
                        color_discrete_map=TIER_COLORS, hover_name='country_name',
                        labels={'gdp_per_capita': 'income per person (US$, log scale)',
                                'pou': 'hunger level (%)', 'risk_tier': ''})
        f4.update_layout(height=300, margin=dict(l=0,r=0,t=24,b=0), paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(0,0,0,0)", title="④ Money matters — until it doesn't")
        st.plotly_chart(f4, use_container_width=True)
        explain("Rising income cuts hunger fast in poor countries, then the effect flattens — one reason we use models that can learn curved relationships.")

# ══════════════════ TAB 3 — COUNTRY STORY ══════════════════
with tabs[2]:
    names = sorted(panel['country_name'].dropna().unique())
    country = st.selectbox("Pick a country", names, index=names.index("Myanmar") if "Myanmar" in names else 0)
    cdf = panel[panel['country_name'] == country].sort_values('year')
    lastrow = cdf.iloc[-1]; tier = lastrow['risk_tier']
    reg = cdf['region'].iloc[0]

    # auto-written plain-language summary
    first, last = cdf['pou'].iloc[0], cdf['pou'].iloc[-1]
    direction = "improved" if last < first else "worsened"
    peak_y = int(cdf.loc[cdf['pou'].idxmax(), 'year'])
    st.markdown(f"### {country} <span class='badge' style='background:{TIER_COLORS.get(tier,'#888')}'>"
                f"{tier} — {TIER_MEANING.get(tier,'')}</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='explain'>📖 <b>{country}'s story:</b> hunger has <b>{direction}</b> since 2010 "
                f"({first:.1f}% → {last:.1f}%). Its hardest year in this period was <b>{peak_y}</b>. "
                f"It belongs to the {reg} region ({lastrow['income_group']}).</div>", unsafe_allow_html=True)

    metric_lab = st.selectbox("What do you want to see?", [LABEL[k] for k in
                              ['pou','gdp_per_capita','inflation_cpi','gdp_growth','des_adequacy','cereal_import_dep']])
    metric = [k for k, v in LABEL.items() if v == metric_lab][0]
    reg_avg = panel[panel['region'] == reg].groupby('year')[metric].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cdf['year'], y=cdf[metric], name=country, mode="lines+markers",
                             line=dict(color=BLUE, width=3)))
    fig.add_trace(go.Scatter(x=reg_avg.index, y=reg_avg.values, name=f"{reg} average",
                             line=dict(color="#9AA8B5", width=2, dash="dot")))
    for xv in (2020, 2022):
        fig.add_vline(x=xv, line_dash="dash", line_color=TIER_COLORS['High'], opacity=.45)
    fig.update_layout(height=360, margin=dict(l=0,r=0,t=12,b=0), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="white", yaxis_title=metric_lab, legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, use_container_width=True)
    explain(f"The solid line is {country}; the dotted line is the average of its region — so you can see "
            f"whether it is doing better or worse than its neighbours. Red dashes mark COVID (2020) and the price shock (2022).")

    strip = " ".join(f"<span class='badge' style='background:{TIER_COLORS.get(t,'#888')};font-size:.72rem'>{int(y)}</span>"
                     for y, t in zip(cdf['year'], cdf['risk_tier']) if pd.notna(t))
    st.markdown("**Hunger tier, year by year** &nbsp;" + strip, unsafe_allow_html=True)

# ══════════════════ TAB 4 — 2024 FORECAST ══════════════════
with tabs[3]:
    st.markdown("### Where is hunger heading in 2024?")
    mcol, scol = st.columns([1, 1.6])
    model_name = mcol.selectbox("Choose a model", list(MODEL_FILES),
                                help="Three different learning methods. They agree on 96% of countries — "
                                     "disagreements mark borderline cases.")
    q = scol.text_input("Search a country", placeholder="e.g. Kenya, Haiti, Myanmar ...")

    mp = preds[preds['model'] == model_name].copy()
    if q:
        hits = mp[mp['country_name'].str.contains(q, case=False, na=False)]
        for _, r in hits.head(4).iterrows():
            c = TIER_COLORS[r['pred_next_tier']]
            st.markdown(f"<div class='card' style='margin-bottom:.5rem'>"
                        f"<b>{r['country_name']}</b> → 2024: "
                        f"<span class='badge' style='background:{c}'>{r['pred_next_tier']}</span> "
                        f"<span style='color:#5B6B7C'>({TIER_MEANING[r['pred_next_tier']]}) · "
                        f"the model is {r['pred_confidence']*100:.0f}% sure · hunger today {r['pou']:.1f}%</span></div>",
                        unsafe_allow_html=True)

    a, b = st.columns([1, 1.6])
    with a:
        cnt = mp['pred_next_tier'].value_counts().reindex(TIER_ORDER).fillna(0)
        pie = go.Figure(go.Pie(labels=cnt.index, values=cnt.values, hole=.58,
                               marker=dict(colors=[TIER_COLORS[t] for t in cnt.index])))
        pie.update_layout(height=270, margin=dict(l=0,r=0,t=6,b=0), paper_bgcolor="rgba(0,0,0,0)",
                          annotations=[dict(text=f"<b>{int(cnt.sum())}</b><br>countries", showarrow=False)])
        st.plotly_chart(pie, use_container_width=True)
        explain(f"{model_name} expects <b>{int(cnt['High'])} countries</b> in serious hunger next year.")
    with b:
        show = mp.sort_values('proba_High', ascending=False)[
            ['country_name','pou','pred_next_tier','pred_confidence']].copy()
        show['pred_confidence'] = (show['pred_confidence']*100).round(0).astype(int).astype(str) + '%'
        show.columns = ['Country', 'Hunger today (%)', 'Predicted 2024', 'How sure?']
        st.dataframe(show, use_container_width=True, height=310, hide_index=True)
        st.download_button("⬇️ Download the full forecast (CSV)", show.to_csv(index=False), "forecast_2024.csv")

# ══════════════════ TAB 5 — WHAT-IF LAB ══════════════════
with tabs[4]:
    st.markdown("### 🧪 What-If Lab — change the story yourself")
    st.markdown("<div class='explain'>Pick a country, move the sliders, and watch its 2024 outlook change. "
                "Try it: give a struggling country strong economic growth and lower inflation — "
                "does its risk fall?</div>", unsafe_allow_html=True)

    wnames = sorted(latest['country_name'].unique())
    wc, wm = st.columns([1.4, 1])
    wcountry = wc.selectbox("Start from this country's real 2023 situation", wnames,
                            index=wnames.index("Kenya") if "Kenya" in wnames else 0)
    wmodel_name = wm.selectbox("Model", list(MODEL_FILES), key="wmodel")
    base = latest[latest['country_name'] == wcountry].iloc[0]

    s1, s2, s3 = st.columns(3)
    sliders = [('pou', 0.0, 80.0, s1), ('des_adequacy', 60.0, 170.0, s1), ('cereal_import_dep', -100.0, 100.0, s1),
               ('gdp_per_capita', 200.0, 60000.0, s2), ('gdp_growth', -20.0, 20.0, s2), ('inflation_cpi', -5.0, 100.0, s2),
               ('pop_growth', -3.0, 6.0, s3), ('food_prod_var', 0.0, 200.0, s3), ('pou_change', -5.0, 5.0, s3)]
    vals = {}
    for f, lo, hi, col in sliders:
        dv = float(base[f]) if pd.notna(base[f]) else (lo + hi) / 2
        vals[f] = col.slider(LABEL[f], lo, hi, min(max(dv, lo), hi))
    vals['covid_flag'] = 0

    wmodel = load_model(MODEL_FILES[wmodel_name])
    row = pd.DataFrame([vals])[FEATURES]
    wpred  = wmodel.predict(row)[0]
    wproba = wmodel.predict_proba(row)[0]
    wclasses = list(wmodel.named_steps['clf'].classes_)

    r1, r2 = st.columns([1, 2])
    real = preds[(preds['model'] == wmodel_name) & (preds['country_name'] == wcountry)]
    real_tier = real['pred_next_tier'].iloc[0] if len(real) else "?"
    changed = "— same as the real forecast" if wpred == real_tier else \
              f"— changed from the real forecast (<b>{real_tier}</b>) by your adjustments!"
    r1.markdown(f"<div class='card'><div class='kpi-lab'>Your scenario says 2024 =</div>"
                f"<div class='kpi-num' style='color:{TIER_COLORS[wpred]}'>{wpred}</div>"
                f"<div style='color:#5B6B7C;font-size:.85rem'>{TIER_MEANING[wpred]}<br>"
                f"{max(wproba)*100:.0f}% sure {changed}</div></div>", unsafe_allow_html=True)
    pr = pd.DataFrame({'tier': wclasses, 'p': wproba}).set_index('tier').reindex(TIER_ORDER).reset_index()
    pb = go.Figure(go.Bar(x=pr['p'], y=pr['tier'], orientation='h',
                          marker_color=[TIER_COLORS[t] for t in pr['tier']],
                          text=[f"{v*100:.0f}%" for v in pr['p']], textposition="outside"))
    pb.update_layout(height=190, margin=dict(l=0,r=30,t=8,b=0), xaxis=dict(range=[0,1.15], showgrid=False),
                     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    r2.plotly_chart(pb, use_container_width=True)
    st.caption("⚠️ Educational scenario tool — real forecasts use verified data, not manual inputs.")
