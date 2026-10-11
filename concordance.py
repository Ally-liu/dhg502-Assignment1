# concordance.py
# Build output/kwic.html: collocate tabs in a vertical column on the LEFT; the
# matching passages on the right. Nodes: 魏忠贤 and the short form 忠贤.
# Palette: #2B2D42 navy, #6F4D3E brown, #D9C6B2 tan, #F5F0E1 cream.

import csv
import json
from pathlib import Path

from qhchina.analytics.collocations import kwic

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"

NODES = ["魏忠贤", "忠贤"]
COLLOCATES = ["杨涟", "矫旨", "传旨", "其党", "生祠", "建祠",
              "逆案", "乱政", "削籍", "客氏"]
HORIZON = 10
MAX_PER_WORD = 40

sents = [line.split(" ") for line in
         (BASE / "sentences.txt").read_text(encoding="utf-8").splitlines()]

juan_by_line = {}
with (BASE / "sentence_index.csv").open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        juan_by_line[int(row["line"])] = row["juan_heading"]

df = kwic(sents, target=NODES, horizon=HORIZON)

data = {}
for word in COLLOCATES:
    hits = []
    for _, r in df.iterrows():
        toks = list(r["left_tokens"]) + list(r["right_tokens"])
        if word in toks:
            line = int(r["doc_index"]) + 1
            hits.append({"left": r["left"].strip(), "node": str(r["node"]),
                         "right": r["right"].strip(),
                         "juan": juan_by_line.get(line, "?")})
    data[word] = hits
    print(f"  {word}: {len(hits)} passages")

payload = json.dumps(data, ensure_ascii=False)

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KWIC · 魏忠贤 &amp; collocates · Mingshi</title>
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
 h1{font-size:1.52rem;font-weight:600;margin:0;color:#2B2D42}
 h1 .red{color:#6F4D3E} h1 .blue{color:#2B2D42}
 h1::after{content:"";display:block;width:74px;height:3px;border-radius:2px;
           margin:14px auto 0;background:var(--grad)}
 .sub{color:#8b8173;font-size:.84rem;margin:15px 0 0}
 .layout{display:flex;gap:26px;align-items:flex-start;margin-top:30px}
 .side{flex:0 0 188px;position:sticky;top:22px}
 .side-title{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;
             color:#a49885;font-weight:600;margin:0 0 10px 4px}
 .tabs{display:flex;flex-direction:column;gap:9px}
 .tab{border:1px solid var(--line);background:var(--cream);color:#2B2D42;
      padding:9px 13px;border-radius:9px;cursor:pointer;font-size:.85rem;
      font-weight:600;text-align:left;transition:.16s;display:flex;
      justify-content:space-between;gap:8px}
 .tab:hover{background:#EFE7D6}
 .tab.active{background:var(--grad);color:#F5F0E1;border-color:transparent;
             box-shadow:0 6px 16px rgba(43,45,66,.28)}
 .tab .c{color:#6F4D3E;font-weight:400}
 .tab.active .c{color:#E3D5BE}
 .main{flex:1;min-width:0}
 .card{background:var(--paper);border:1px solid var(--line);border-radius:12px;
       overflow:hidden;box-shadow:0 8px 22px rgba(70,60,45,.07)}
 .bar{height:4px;background:var(--grad)}
 .ph{padding:6px 18px 22px}
 .ptitle{text-align:left;color:#2B2D42;font-weight:600;font-size:1.02rem;
         padding:14px 0 8px;border-bottom:1px solid #EFE7D6;margin-bottom:12px}
 .ptitle .n{color:#a49885;font-size:.8rem;font-weight:400}
 .hits{text-align:center}
 .hit{display:inline-block;text-align:left;max-width:100%;margin:7px 0;padding:10px 15px;
      background:#FBF8F0;border:1px solid #EDE4D3;border-left:3px solid #C8B79B;
      border-radius:9px;font-family:ui-monospace,Consolas,"Courier New",monospace;
      font-size:.86rem;line-height:1.9;color:#4a473f;transition:.15s}
 .hit:hover{border-left-color:#6F4D3E;background:#F7F1E4}
 .l{color:#5c584e} .r{color:#5c584e}
 .node{color:#F5F0E1;background:#6F4D3E;font-weight:600;padding:1px 6px;border-radius:4px}
 .juan{color:#6F4D3E;font-size:.76rem;background:#EADFCB;border-radius:5px;
       padding:1px 8px;margin-left:8px;white-space:nowrap}
 .legend{color:#a49885;font-size:.77rem;margin-top:14px}
 .legend .node{background:none;color:#6F4D3E;padding:0}
 .legend .juan{background:none;color:#6F4D3E;margin:0}
 .empty{color:#a49885;text-align:center;padding:26px}
 @media(max-width:760px){
   .layout{flex-direction:column}
   .side{flex:none;width:100%;position:static}
   .tabs{flex-direction:row;flex-wrap:wrap}
 }
</style></head><body>
<div class="wrap">
<header>
 <h1>Passages linking <span class="red">魏忠贤 / 忠贤</span> with its collocates</h1>
 <p class="sub">Keywords-in-context (±10 tokens) · Corpus 明史 · citations by 卷 (juan)</p>
</header>
<div class="layout">
 <aside class="side">
   <div class="side-title">Collocates</div>
   <div class="tabs" id="tabs"></div>
 </aside>
 <main class="main">
  <div class="card"><div class="bar"></div>
   <div class="ph">
    <div class="ptitle" id="ptitle"></div>
    <div class="hits" id="hits"></div>
   </div>
  </div>
  <p class="legend"><span class="node">brown</span> = node · <span class="juan">tan</span> = 卷 · click a collocate on the left</p>
 </main>
</div>
</div>
<script>
const DATA = __DATA__;
let cur = Object.keys(DATA)[0];
function esc(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function render(){
  const hits = DATA[cur];
  document.getElementById("ptitle").innerHTML =
     esc(cur) + ` <span class="n">(${hits.length} passages)</span>`;
  const box = document.getElementById("hits");
  if(!hits.length){ box.innerHTML = '<div class="empty">no co-occurring passage within horizon 10</div>'; return; }
  box.innerHTML = hits.slice(0,40).map(h =>
     `<div class="hit"><span class="l">${esc(h.left)}</span> `+
     `<span class="node">${esc(h.node)}</span> `+
     `<span class="r">${esc(h.right)}</span> `+
     `<span class="juan">${esc(h.juan)}</span></div>`).join("");
}
const tabs = document.getElementById("tabs");
Object.keys(DATA).forEach(w=>{
  const b = document.createElement("div");
  b.className = "tab"+((w===cur)?" active":"");
  b.innerHTML = esc(w)+' <span class="c">'+DATA[w].length+'</span>';
  b.onclick = ()=>{ cur=w; document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active")); b.classList.add("active"); render(); };
  tabs.appendChild(b);
});
render();
</script></body></html>
"""

(OUT / "kwic.html").write_text(HTML.replace("__DATA__", payload), encoding="utf-8")
print("wrote output/kwic.html")
