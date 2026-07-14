/* FoodWatch — shared JS (constants, nav, footer, reveal). Load AFTER foodwatch_data.js */
const TC={Low:'#1A9E77',Medium:'#E6A817',High:'#D64550'};
const TIERS=['Low','Medium','High'];
const MEAN={Low:'food access broadly secure',Medium:'vulnerable — early-action zone',High:'serious hunger — urgent attention'};
const LBL={pou:'Hunger level (%)',des_adequacy:'Food supply adequacy (%)',
 cereal_import_dep:'Cereal import dependence (%)',food_prod_var:'Food supply stability',
 gdp_per_capita:'Income per person (US$)',gdp_growth:'Economic growth (%)',
 inflation_cpi:'Inflation (%)',pop_growth:'Population growth (%)',
 pou_change:'Hunger trend vs last year (pp)',covid_flag:'Pandemic year'};
const PLOTCFG={displayModeBar:false,responsive:true};
const LAYOUT={paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
 font:{family:'Inter,sans-serif',color:'#13202E',size:12},margin:{l:52,r:14,t:14,b:42}};
const ISOs=(typeof FW!=='undefined')?Object.keys(FW.META):[];
const name2iso={};ISOs.forEach(i=>name2iso[FW.META[i].n]=i);

function fwNav(active,solid){
 const items=[['index.html','Home'],['explore.html','World & Patterns'],['country.html','Country Story'],
  ['forecast.html','Forecast'],['modellab.html','Model Lab'],['lab.html','What-If Lab'],['learn.html','Learn']];
 document.write(`<div id="progress"></div><nav class="${solid?'solid':''}"><div class="bar">
  <a class="logo" href="index.html">🌾 FoodWatch</a>
  <button class="navtoggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button>
  <ul>`+
  items.map(([h,t])=>`<li><a href="${h}" class="${h===active?'active':''}">${t}</a></li>`).join('')+
  `</ul></div></nav>`);}

function fwFooter(){document.write(`<footer><div class="wrap"><div class="cols">
 <div><h4>🌾 FoodWatch</h4><p style="font-size:.82rem;color:#8FB4D6;margin-bottom:.5rem">An Explainable Early-Warning System for National Food-Security Risk</p>
 <p style="font-size:.9rem;line-height:1.7">An academic data-mining project predicting national food-security
 risk from socioeconomic signals — FAOSTAT + World Bank open data (2010–2023), machine learning,
 SHAP explainability. Runs entirely in your browser.</p></div>
 <div><h4>Explore</h4><a href="explore.html">World &amp; Patterns</a><a href="country.html">Country Story</a>
  <a href="forecast.html">Forecast 2024</a><a href="lab.html">What-If Lab</a></div>
 <div><h4>Data</h4><a href="https://www.fao.org/faostat/en/#data/FS" target="_blank">FAOSTAT</a>
  <a href="https://data.worldbank.org" target="_blank">World Bank</a>
  <a href="https://sdgs.un.org/goals/goal2" target="_blank">UN SDG 2</a></div>
 <div><h4>Agencies</h4><a href="https://www.fao.org" target="_blank">FAO</a>
  <a href="https://www.wfp.org" target="_blank">WFP</a>
  <a href="https://www.un.org/en" target="_blank">United Nations</a></div></div>
 <div class="fine">Academic project — Data Mining course, 2026 · Open data · LogReg, Decision Tree, Random Forest · SHAP</div>
 </div></footer>`);}

addEventListener('DOMContentLoaded',()=>{
 const nav=document.querySelector('nav'),bar=document.getElementById('progress');
 const toggle=document.getElementById('navToggle');
 if(toggle) toggle.addEventListener('click',()=>nav.classList.toggle('open'));
 nav?.querySelectorAll('ul a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')));
 addEventListener('scroll',()=>{
  if(nav&&!nav.classList.contains('solid'))nav.classList.toggle('scrolled',scrollY>40);
  if(bar)bar.style.width=(scrollY/Math.max(1,document.body.scrollHeight-innerHeight)*100)+'%';
 },{passive:true});
 const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');
  e.target.querySelectorAll?.('.num[data-count]').forEach(n=>{if(n.dataset.done)return;n.dataset.done=1;
   const end=+n.dataset.count,t0=performance.now();
   const tick=t=>{const p=Math.min((t-t0)/1500,1);
    n.textContent=Math.round(end*(1-Math.pow(1-p,3))).toLocaleString();
    if(p<1)requestAnimationFrame(tick)};requestAnimationFrame(tick);});}}),{threshold:.18});
 document.querySelectorAll('.rv,.stat').forEach(el=>io.observe(el));
});
