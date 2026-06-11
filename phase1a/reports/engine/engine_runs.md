# Engine Runs (named configs)

config registry 재실행(동결 재현).

| name | n | IC | IC-IR | net_ls | net_cw | turnover | verdict | kills |
|---|---|---|---|---|---|---|---|---|
| B2_value | 125 | +0.0015 | +0.011 | -0.0177 | -0.0153 | 1.16 | DEAD | net≤0;IC-IR<0.2 |
| B3_quality | 122 | +0.0207 | +0.220 | +0.0441 | -0.0125 | 0.99 | SURVIVE |  |
| B4_momentum | 113 | +0.0140 | +0.098 | +0.0763 | +0.0056 | 3.01 | DEAD | IC-IR<0.2 |
| B5_lowvol | 119 | +0.0226 | +0.117 | -0.0511 | -0.0541 | 1.42 | DEAD | net≤0;IC-IR<0.2;소형집중 |
| broad_quality_quarantine | 122 | +0.0207 | +0.220 | +0.0441 | -0.0125 | 0.99 | FAIL | long-only active≤0(vs CW) |
| phase1b_blend | 113 | +0.0256 | +0.200 | +0.0270 | -0.0244 | 2.38 | FAIL | net active vs CW≤0;2016-20에만 집중;sector중립화후 net≤0;long-only vs CW 음수 |
| broad_event | 111 | +0.0061 | +0.083 | +0.0293 | -0.0061 | 2.67 | FAIL | net active vs CW≤0;2x cost net≤0;long-only vs CW 음수;sector중립화후 net≤0 |
| sm_quality | 122 | +0.0145 | +0.157 | +0.0256 | +0.0066 | 1.37 | FAIL | IC-IR<0.20;2021-26 사망;최저유동성에만 존재 |
| sm_event | 110 | +0.0102 | +0.164 | +0.0400 | +0.0185 | 3.21 | FAIL | IC-IR<0.20;turnover>300%&net약 |
| sm_blend | 125 | +0.0415 | +0.335 | +0.0357 | +0.0220 | 3.04 | FAIL | 최저유동성에만 존재 |
