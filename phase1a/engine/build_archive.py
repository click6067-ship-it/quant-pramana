#!/usr/bin/env python3
"""PRAMANA 통합 아카이브 빌더 — 흩어진 DR폴더+로컬 문서를 한 곳에 dedup·분류·인덱스.
원본은 절대 안 건드림(복사만). 결과: quant-pramana/PRAMANA_ARCHIVE/ + 00_START_HERE.md 지도."""
import os, shutil, glob
ROOT="/home/click/ghq/github.com/click6067-ship-it/quant-pramana"
DR="/mnt/c/Users/click/Desktop/DR"
ARC=os.path.join(ROOT,"PRAMANA_ARCHIVE")

cats={
 "01_research_arc":      sorted(glob.glob(f"{ROOT}/pramana_research/*.md")+glob.glob(f"{ROOT}/pramana_research/*.pdf")),
 "02_empirical_results": sorted(glob.glob(f"{ROOT}/phase1a/reports/*.md")),
 "03_design_and_locks":  sorted(glob.glob(f"{ROOT}/integrated/*.md")+glob.glob(f"{ROOT}/integrated/*.docx")),
 "04_v4_redesign":       sorted(glob.glob(f"{ROOT}/PRAMANA_V4/*.docx")),
 "06_registry":          sorted(glob.glob(f"{ROOT}/phase1a/registry/*.csv")),
}
# 로컬 전체 basename 집합 (DR dedup용)
local_names={os.path.basename(p) for ps in cats.values() for p in ps}
# DR 폴더에서 로컬에 없는 고유본만 (PDF·docx·고유 md)
dr_unique=[p for p in sorted(glob.glob(f"{DR}/*")) if os.path.isfile(p) and os.path.basename(p) not in local_names]
cats["05_desktop_DR_unique"]=dr_unique

# 빌드 (idempotent)
if os.path.exists(ARC): shutil.rmtree(ARC)
os.makedirs(ARC)
counts={}
for cat,files in cats.items():
    dst=os.path.join(ARC,cat); os.makedirs(dst,exist_ok=True); n=0
    for f in files:
        try: shutil.copy2(f,os.path.join(dst,os.path.basename(f))); n+=1
        except Exception as e: print("skip",f,e)
    counts[cat]=n
# 마스터 다이제스트를 루트에 (가지고 다니는 한 파일)
master=f"{ROOT}/PRAMANA_V4/PRAMANA_MASTER_DOSSIER.docx"
if os.path.exists(master): shutil.copy2(master,os.path.join(ARC,"PRAMANA_MASTER_DOSSIER.docx"))

# 00_START_HERE.md 지도
def listing(cat):
    dst=os.path.join(ARC,cat);
    return "\n".join(f"  - {f}" for f in sorted(os.listdir(dst))) if os.path.isdir(dst) else ""
idx=f"""# PRAMANA — 통합 아카이브 (START HERE)

> 흩어져 있던 **DR 폴더(Desktop) + 로컬 문서(integrated·pramana_research·reports)** 를 한 곳에 dedup·분류한 정본 아카이브.
> 원본은 그대로 보존됨(여긴 복사본). 시점·네이밍 제각각이던 걸 카테고리로 묶음.

## ⭐ 먼저 읽을 것 — 딱 한 파일
**`PRAMANA_MASTER_DOSSIER.docx`** (이 폴더 루트) — 전체(목표·연구아크 DR1~4·실증결과 전부·아키텍처·Codex리뷰·v1–v3→V4·현재상태)를 한 파일로. **이거 하나면 PRAMANA 전체 파악.** 100+ 원본을 다 읽을 필요 없음.

그 다음(원하면): `04_v4_redesign/` 의 v1–v3 사후분석 · V4 설계도.

## 폴더 지도
| 폴더 | 개수 | 내용 |
|---|---|---|
| (루트) PRAMANA_MASTER_DOSSIER.docx | 1 | ⭐ 전체 한 파일 요약 |
| 01_research_arc/ | {counts.get('01_research_arc',0)} | DR-1~4 적대 락 시퀀스(primary+Claude audit)·Phase1A 설계·control sheet |
| 02_empirical_results/ | {counts.get('02_empirical_results',0)} | B0~V3 실험 결과 정본(무엇이 죽고 살았나) |
| 03_design_and_locks/ | {counts.get('03_design_and_locks',0)} | 8레이어 설계·V3 락·기술보고서·Codex handoff |
| 04_v4_redesign/ | {counts.get('04_v4_redesign',0)} | v1-v3 사후분석·V4 설계도·마스터 다이제스트(신규) |
| 05_desktop_DR_unique/ | {counts.get('05_desktop_DR_unique',0)} | Desktop DR 폴더 고유본(ChatGPT 원본 PDF·Stage0A locks·퀀트딥리서치 charter) |
| 06_registry/ | {counts.get('06_registry',0)} | 마일스톤·B0 런 기록 CSV |

## 핵심 한 줄
단순/선형 팩터는 전멸(정직한 no-edge), 풀북은 SPY를 위험조정으로 못 이김 → **V4 = SPY/QQQ 코어 + 검증된 공격 위성(core-satellite)** 로 재설계 중. 상세는 마스터 다이제스트.

## 01_research_arc/
{listing('01_research_arc')}

## 02_empirical_results/
{listing('02_empirical_results')}

## 03_design_and_locks/
{listing('03_design_and_locks')}

## 05_desktop_DR_unique/
{listing('05_desktop_DR_unique')}

---
*생성: phase1a/engine/build_archive.py · 원본 보존(복사본 아카이브) · 재실행시 갱신*
"""
open(os.path.join(ARC,"00_START_HERE.md"),"w").write(idx)
total=sum(counts.values())+1
print(f"✅ PRAMANA_ARCHIVE/ 생성 — 총 {total}개 파일 (dedup 후)")
for c,n in counts.items(): print(f"   {c}: {n}")
print(f"   05_desktop_DR_unique 고유본: {[os.path.basename(p) for p in dr_unique]}")
du=os.popen(f"du -sh {ARC}").read().split()[0]
print(f"   용량 {du} · 지도: PRAMANA_ARCHIVE/00_START_HERE.md")
