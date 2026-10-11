# make_report.py
# Build output/results.html: tabs in a vertical column on the LEFT; table on the right.
# Palette: #2B2D42 navy, #6F4D3E brown, #D9C6B2 tan, #F5F0E1 cream.

import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"

RUNS = [
    ("window5",  "window 5+5",     "window · 5 tokens left / 5 right"),
    ("window10", "window 10+10",   "window · 10 tokens left / 10 right"),
    ("sentence", "same sentence",  "sentence · same-sentence co-occurrence"),
    ("pooled",   "pooled +忠贤",    "window 5+5 · 魏忠贤 and short form 忠贤 pooled"),
    ("min3",     "short corpus ≥3", "window 5+5 · restricted to ≥3-token sentences"),
]
COLUMNS = ["collocate", "obs_local", "exp_local", "ratio_local", "obs_global",
           "log_dice", "log_likelihood", "adjusted_p_value", "p_value"]
HEADERS = {
    "collocate": "Collocate", "obs_local": "O", "exp_local": "E",
    "ratio_local": "O/E", "obs_global": "Global", "log_dice": "logDice",
    "log_likelihood": "log-likelihood", "adjusted_p_value": "Adj. p",
    "p_value": "p",
}

data = {}
for name, label, desc in RUNS:
    df = pd.read_csv(OUT / f"collocates_{name}.csv")
    df = df.sort_values("log_dice", ascending=False)[COLUMNS]
    data[label] = {"desc": desc, "rows": df.to_dict(orient="records")}

payload = json.dumps(data, ensure_ascii=False)

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Collocates of 魏忠贤 · Mingshi</title>
<style>
 :root{
   --navy:#2B2D42; --brown:#6F4D3E; --tan:#D9C6B2; --cream:#F5F0E1;
   --paper:#FCFAF4; --line:#E5DCCD; --muted:#8b8173;
   --grad:linear-gradient(100deg,#2B2D42,#6F4D3E);
 }
 *{box-sizing:border-box}
 body{margin:0;color:#2B2D42;
      background:linear-gradient(165deg,#F8F4EA,#F1EADB 60%,#F6F1E4);
      font-family:"Segoe UI",system-ui,-apple-system,"Microsoft YaHei",sans-serif;
      min-height:100vh;font-size:15px}
 .wrap{max-width:1160px;margin:0 auto;padding:40px 24px 84px}
 header{text-align:center;margin-bottom:8px}
 h1{font-size:1.66rem;font-weight:600;margin:0;color:#2B2D42}
 h1 .red{color:#6F4D3E} h1 .blue{color:#2B2D42}
 h1::after{content:"";display:block;width:74px;height:3px;border-radius:2px;
           margin:14px auto 0;background:var(--grad)}
 .sub{color:#8b8173;font-size:.84rem;line-height:1.9;margin:15px 0 0}
 .sub b{color:#6F4D3E;font-weight:600}
 .layout{display:flex;gap:26px;align-items:flex-start;margin-top:30px}
 .side{flex:0 0 188px;position:sticky;top:22px}
 .side-title{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;
             color:#a49885;font-weight:600;margin:0 0 10px 4px}
 .tabs{display:flex;flex-direction:column;gap:9px}
 .tab{border:1px solid var(--line);background:var(--cream);color:#2B2D42;
      padding:10px 14px;border-radius:9px;cursor:pointer;font-size:.85rem;
      font-weight:600;text-align:left;transition:.16s}
 .tab:hover{background:#EFE7D6}
 .tab.active{background:var(--grad);color:#F5F0E1;border-color:transparent;
             box-shadow:0 6px 16px rgba(43,45,66,.28)}
 .main{flex:1;min-width:0}
 .rundesc{color:#6F4D3E;font-size:.82rem;margin:2px 0 14px}
 .card{background:var(--paper);border:1px solid var(--line);border-radius:12px;
       overflow:hidden;box-shadow:0 8px 22px rgba(70,60,45,.07)}
 .bar{height:4px;background:var(--grad)}
 table{border-collapse:collapse;width:100%;font-size:.86rem}
 thead{background:var(--grad)}
 thead th{background:transparent;color:#F5F0E1;font-weight:600;padding:11px 14px;
          text-align:right;white-space:nowrap;cursor:pointer;user-select:none}
 thead th:first-child{text-align:left}
 thead th:hover{color:#EAD9C0}
 thead th.sorted::after{content:" \\2582"}
 thead th.sorted.asc::after{content:" \\2580"}
 thead th.rank{cursor:default;color:#C9BFB0}
 tbody td{padding:9px 14px;border-bottom:1px solid #F0E9DB;text-align:right;
          white-space:nowrap;font-variant-numeric:tabular-nums;color:#4a473f}
 tbody td.rank{text-align:left;color:#b8ad9c}
 tbody td.coll{text-align:left;font-weight:600;color:#2B2D42}
 tbody tr:nth-child(even){background:#F7F2E7}
 tbody tr:hover{background:#EFE6D4}
 td.dice{color:#2B2D42;font-weight:600}
 td.ll{color:#6F4D3E;font-weight:600}
 .hint{color:#a49885;font-size:.77rem;margin-top:14px}
 @media(max-width:760px){
   .layout{flex-direction:column}
   .side{flex:none;width:100%;position:static}
   .tabs{flex-direction:row;flex-wrap:wrap}
 }
</style></head><body>
<div class="wrap">
<header>
 <h1>Collocates of <span class="red">魏忠贤</span> in the <span class="blue">Mingshi</span> 明史</h1>
 <p class="sub"><b>Corpus</b> 明史 (History of the Ming) &nbsp;·&nbsp; <b>Target</b> 魏忠贤 &nbsp;·&nbsp;
  <b>Test</b> Fisher's exact, FDR (Benjamini–Hochberg) &nbsp;·&nbsp;
  <b>Measures</b> log-likelihood &amp; logDice</p>
</header>
<div class="layout">
 <aside class="side">
   <div class="side-title">Runs</div>
   <div class="tabs" id="tabs"></div>
 </aside>
 <main class="main">
   <div class="rundesc" id="rundesc"></div>
   <div class="card"><div class="bar"></div>
    <table><thead><tr id="head"></tr></thead><tbody id="body"></tbody></table></div>
   <p class="hint">Click a column header to sort · click a Run on the left to switch</p>
 </main>
</div>
</div>
<script>
const DATA = __DATA__;
const COLS = __COLS__;
const HEAD = __HEAD__;
let cur = Object.keys(DATA)[0];
let sort = {col:"log_dice", asc:false};

function fmt(col, v){
  if(col==="collocate") return v;
  if(col==="p_value"||col==="adjusted_p_value")
     return (v===0)?"<0.0001":Number(v).toExponential(2);
  if(col==="log_dice") return Number(v).toFixed(3);
  if(col==="log_likelihood"||col==="ratio_local") return Number(v).toFixed(2);
  if(col==="obs_local"||col==="obs_global") return String(v);
  return Number(v).toFixed(3);
}
function cls(c){ return c==="log_dice"?"dice":(c==="log_likelihood"?"ll":(c==="collocate"?"coll":"")); }

function render(){
  let rows = DATA[cur].rows.slice();
  rows.sort((a,b)=> sort.col==="collocate"
     ? (sort.asc?a.collocate.localeCompare(b.collocate):b.collocate.localeCompare(a.collocate))
     : (sort.asc? a[sort.col]-b[sort.col] : b[sort.col]-a[sort.col]));
  document.getElementById("rundesc").textContent =
     DATA[cur].desc + " · " + rows.length + " collocates";
  document.getElementById("head").innerHTML =
    '<th class="rank">#</th>' + COLS.map(c =>
    `<th data-col="${c}" class="${c===sort.col?'sorted':''} ${c===sort.col&&sort.asc?'asc':''}">${HEAD[c]}</th>`).join("");
  document.querySelectorAll("#head th[data-col]").forEach(th=>th.onclick=()=>{
    const c = th.dataset.col;
    if(c===sort.col) sort.asc=!sort.asc; else {sort.col=c; sort.asc=false;}
    render();
  });
  document.getElementById("body").innerHTML = rows.map((r,i)=>
    `<tr><td class="rank">${i+1}</td>` +
    COLS.map(c=>`<td class="${cls(c)}">${fmt(c,r[c])}</td>`).join("") + "</tr>").join("");
}

const tabs = document.getElementById("tabs");
Object.keys(DATA).forEach(label=>{
  const b = document.createElement("div");
  b.className = "tab"+((label===cur)?" active":"");
  b.textContent = label;
  b.onclick = ()=>{ cur=label; document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active")); b.classList.add("active"); render(); };
  tabs.appendChild(b);
});
render();
</script></body></html>
"""

html = (HTML.replace("__DATA__", payload)
            .replace("__COLS__", json.dumps(COLUMNS))
            .replace("__HEAD__", json.dumps(HEADERS, ensure_ascii=False)))
(OUT / "results.html").write_text(html, encoding="utf-8")
print("wrote output/results.html")
