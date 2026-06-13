"""matplotlib 한글 폰트 공용 헬퍼 — 판다스/matplotlib 차트 한글 깨짐(□) 해결.
사용: from kfont import set_korean_font; set_korean_font() (차트 생성 전 1회)."""
import os, matplotlib as mpl
from matplotlib import font_manager as fm
_CANDIDATES = [
    "/home/click/.local/share/fonts/malgun.ttf",
    "/mnt/c/Windows/Fonts/malgun.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]
def set_korean_font():
    for fp in _CANDIDATES:
        if os.path.exists(fp):
            try:
                fm.fontManager.addfont(fp)
                mpl.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name()
                mpl.rcParams["axes.unicode_minus"] = False   # 마이너스(−) 깨짐 방지
                return fp
            except Exception:
                continue
    mpl.rcParams["axes.unicode_minus"] = False
    return None
