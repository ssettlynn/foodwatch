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
/* inline line-icon set (Feather-style, stroke-based) */
const FICON={
 wheat:'<path d="M12 22V8"/><path d="M12 8C12 5.2 10 3 7 3c0 3 2.2 5 5 5z"/><path d="M12 8c0-2.8 2-5 5-5 0 3-2.2 5-5 5z"/><path d="M12 14c0-2.8-2-5-5-5 0 3 2.2 5 5 5z"/><path d="M12 14c0-2.8 2-5 5-5 0 3-2.2 5-5 5z"/>',
 map:'<polygon points="1 6 8 3 16 6 23 3 23 18 16 21 8 18 1 21 1 6"/><line x1="8" y1="3" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="21"/>',
 globe:'<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
 trend:'<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
 sliders:'<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
 search:'<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
 download:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
 play:'<polygon points="6 3 20 12 6 21 6 3"/>',
 pause:'<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>',
 reset:'<polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>',
 check:'<polyline points="20 6 9 17 4 12"/>',
 clock:'<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
 calendar:'<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
 book:'<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>'};
const icn=(n,s=18)=>`<svg class="ic" width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${FICON[n]}</svg>`;
const LAYOUT={paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
 font:{family:'Inter,sans-serif',color:'#13202E',size:12},margin:{l:52,r:14,t:14,b:42}};
const ISOs=(typeof FW!=='undefined')?Object.keys(FW.META):[];
const name2iso={};ISOs.forEach(i=>name2iso[FW.META[i].n]=i);

function fwNav(active,solid){
 const items=[['index.html','Home'],['explore.html','World & Patterns'],['country.html','Country Story'],
  ['forecast.html','Forecast'],['modellab.html','Model Lab'],['lab.html','What-If Lab'],['learn.html','Learn']];
 document.write(`<div id="progress"></div><nav class="${solid?'solid':''}"><div class="bar">
  <a class="logo" href="index.html">${icn('wheat',20)} FoodWatch</a>
  <button class="navtoggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button>
  <ul>`+
  items.map(([h,t])=>`<li><a href="${h}" class="${h===active?'active':''}">${t}</a></li>`).join('')+
  `</ul></div></nav>`);}

function fwFooter(){document.write(`<footer><div class="wrap"><div class="cols">
 <div><h4>${icn('wheat',16)} FoodWatch</h4><p style="font-size:.82rem;color:#8FB4D6;margin-bottom:.5rem">An Explainable Early-Warning System for National Food-Security Risk</p>
 <p style="font-size:.9rem;line-height:1.7">An academic data-mining project predicting national food-security
 risk from socioeconomic signals — FAOSTAT + World Bank open data (2010–2023), machine learning,
 SHAP explainability. Runs entirely in your browser.</p></div>
 <div><h4>Explore</h4><a href="explore.html">World &amp; Patterns</a><a href="country.html">Country Story</a>
  <a href="forecast.html">Forecast 2024–2028</a><a href="lab.html">What-If Lab</a></div>
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
