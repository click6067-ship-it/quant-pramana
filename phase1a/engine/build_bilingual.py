#!/usr/bin/env python3
"""KO + EN 빌드 → 단일 토글 대시보드(EN/KO 버튼 in-page). self-contained.
cd phase1a && .venv/bin/python -u engine/build_bilingual.py"""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
PY = os.path.join(ROOT, ".venv", "bin", "python")
MAIN = os.path.join(HERE, "build_journey_dashboard.py")
KO = os.path.join(REPO, "pramana_journey_dashboard.html")
EN = os.path.join(REPO, "pramana_journey_dashboard_en.html")

# 1) build both languages
for lang in ("ko", "en"):
    env = {**os.environ, "PRAMANA_LANG": lang}
    r = subprocess.run([PY, MAIN], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"build {lang} FAILED:\n{r.stderr[-1500:]}")
    print(f"  built {lang}: {r.stdout.strip().splitlines()[0] if r.stdout else ''}")

ko_html = open(KO, encoding="utf-8").read()
en_html = open(EN, encoding="utf-8").read()
head = re.search(r"<head>(.*?)</head>", ko_html, re.S).group(1)
ko_body = re.search(r"<body[^>]*>(.*)</body>", ko_html, re.S).group(1)
en_body = re.search(r"<body[^>]*>(.*)</body>", en_html, re.S).group(1)

toggle_css = """<style>
#langtoggle{position:fixed;top:13px;right:16px;z-index:60;display:flex;gap:2px;background:rgb(255 255 255 / .06);border:1px solid rgb(255 255 255 / .14);border-radius:999px;padding:3px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-shadow:0 8px 24px rgb(0 0 0 / .28)}
#langtoggle button{border:0;background:transparent;color:#9fb0c3;font:600 12px 'Inter',sans-serif;padding:5px 14px;border-radius:999px;cursor:pointer;transition:all .18s}
#langtoggle button.on{background:rgb(125 211 252 / .18);color:#7dd3fc}
#langtoggle button:not(.on):hover{color:#eaf0f7}
</style>"""

toggle_ui = ('<div id="langtoggle"><button data-l="ko" onclick="setLang(\'ko\')">한국어</button>'
             '<button data-l="en" onclick="setLang(\'en\')">EN</button></div>')

js = """<script>
function setLang(l){
  document.getElementById('L-ko').style.display = l==='en' ? 'none':'';
  document.getElementById('L-en').style.display = l==='en' ? '':'none';
  document.documentElement.lang = l;
  try{localStorage.setItem('pramana_lang', l)}catch(e){}
  var bs=document.querySelectorAll('#langtoggle button');
  for(var i=0;i<bs.length;i++){bs[i].classList.toggle('on', bs[i].dataset.l===l);}
}
(function(){
  var p=new URLSearchParams(location.search).get('lang'), s=null;
  try{s=localStorage.getItem('pramana_lang')}catch(e){}
  setLang((p==='en'||p==='ko')?p:(s||'ko'));
})();
</script>"""

out = (f"<!doctype html><html lang=\"ko\"><head>{head}{toggle_css}</head>"
       f"<body class=\"noise\">{toggle_ui}"
       f"<div id=\"L-ko\">{ko_body}</div>"
       f"<div id=\"L-en\" style=\"display:none\">{en_body}</div>"
       f"{js}</body></html>")

open(KO, "w", encoding="utf-8").write(out)
os.remove(EN)  # single toggle file is the deliverable
print(f"✅ bilingual toggle → {KO} ({len(out)//1024} KB) · removed separate EN file")
