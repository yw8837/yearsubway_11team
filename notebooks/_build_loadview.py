# -*- coding: utf-8 -*-
"""② 로드뷰 노트북(.ipynb) 생성 스크립트."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []
M = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
C = lambda t: cells.append(nbf.v4.new_code_cell(t))

M("""# ② 데이터 로드 & 구조 확인 — Load & View
**11team · 서울 지하철 혼잡도 분석**

분석에 쓸 데이터를 불러오고 구조(크기·컬럼·샘플)를 확인한다.
본격 정제·분석은 다음 단계(③ EDA)에서 진행한다.""")

M("""## 사용 데이터
| 데이터 | 내용 | 출처 |
|---|---|---|
| 지하철 승하차 | 호선·역별 시간대별 승하차 (2015–2021) | 서울 열린데이터광장 |
| 역 위치좌표 | 지하철역 위·경도 | Kakao Local API |
| 주야간 인구 | 자치구별 주간인구지수 (2020) | 공공데이터포털(통계청) |
| 직업유형별 취업인구 | 자치구별 직업군 취업인구 (2020) | 서울 열린데이터광장 |
| (기상) | 서울 월별 기온·강수 | 기상청 — *월별 재다운로드 후 추가* |""")

C("""import pandas as pd, numpy as np

pd.set_option('display.max_columns', 60)

SUBWAY_DIR = r"C:/Users/최용우/Downloads/drive-download-20260625T013956Z-3-001/dataset"
EXT_DIR    = r"C:/Users/최용우/claude/yearsubway_11team/external_data"

def read_csv_auto(path, **kw):
    \"\"\"인코딩 자동 감지 CSV 로더 (cp949/utf-8 혼용 대응).\"\"\"
    for enc in ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']:
        try:
            return pd.read_csv(path, encoding=enc, **kw)
        except UnicodeDecodeError:
            continue
    raise RuntimeError('인코딩 감지 실패: ' + path)""")

M("## 1. 지하철 승하차 인원 (메인 데이터)")
C("""metro = read_csv_auto(f"{SUBWAY_DIR}/Seoul_subway_data_20210705.csv")
print("shape:", metro.shape)
metro.head()""")
C("""print("기간 :", metro['사용월'].min(), "~", metro['사용월'].max())
print("호선 :", metro['호선명'].nunique(), "개 / 역 :", metro['지하철역'].nunique(), "개")
print("결측 :", int(metro.isna().sum().sum()), "건")""")

M("## 2. 역 위치좌표 (지도 시각화용)")
C("""subway_loc = read_csv_auto(f"{SUBWAY_DIR}/subway_location_data.csv")
print("shape:", subway_loc.shape)
subway_loc.head()""")

M("""## 3. 주야간 인구 — 외부데이터 ①
**주간인구지수** = 주간인구 / 상주인구 × 100.
100 초과 → 낮에 사람이 모이는 **업무지구**, 100 미만 → **주거지(베드타운)**.
원본은 연령·성별로 쪼개져 있어 **자치구 합계** 행만 추출한다.""")
C("""daynight_raw = pd.read_excel(
    f"{EXT_DIR}/서울특별시_자치구별 연령별 주간 야간 인구_20201231.xlsx", header=1)
daynight_raw['행정구역별'] = daynight_raw['행정구역별'].ffill()

# 성별=계 & 연령별=합계 & 서울특별시 전체 제외 → 자치구별 1행
daynight = daynight_raw[
    (daynight_raw['성별'] == '계') &
    (daynight_raw['연령별'] == '합계') &
    (daynight_raw['행정구역별'] != '서울특별시')].copy()
daynight['자치구'] = daynight['행정구역별'].str.replace('\\u3000', '', regex=False).str.strip()
daynight = daynight[['자치구', '상주인구', '주간 인구', '주간 인구 지수']].reset_index(drop=True)

print("자치구 수:", len(daynight))
daynight.sort_values('주간 인구 지수', ascending=False).head(8)""")

M("## 4. 직업유형별 취업인구 — 외부데이터 ②")
C("""job_raw = read_csv_auto(f"{EXT_DIR}/직업유형별+취업인구(구별)_20260625143926.csv")
print("shape:", job_raw.shape)
job_raw.head(4)""")

M("""## 5. 기상 — 외부데이터 ③ *(월별 재다운로드 후 추가 예정)*
처음 받은 파일이 1개월치(30일)만 들어와, **자료구분 '월'**로 다시 받아 합칠 예정.
Join 키 = `연-월` (지하철 사용월과 매칭).""")

M("""---
## ✅ 로드 요약
- **지하철 승하차** (45,338 × 52) · **역 좌표** (579) — 메인
- **주야간 인구** (자치구 25) · **직업 취업인구** — 외부 Join용 (키: 자치구)
- **기상** — 월별 재다운로드 후 추가

### ▶ 다음 단계 (③ EDA)
시간대 패턴·호선·역 혼잡 분석 + **자치구 주간인구지수 Join**으로 방향성(업무지구 vs 베드타운) 검증.""")

nb.cells = cells
nb.metadata = {"language_info": {"name": "python"}}
nbf.write(nb, "notebooks/02_데이터_로드.ipynb")
print("notebook written: notebooks/02_데이터_로드.ipynb")
