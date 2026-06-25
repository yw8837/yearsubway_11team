# -*- coding: utf-8 -*-
"""⑤ 솔루션 노트북 — 혼잡 점수화 → folium 지도 + 자원배치 권고."""
import nbformat as nbf
nb = nbf.v4.new_notebook(); cells = []
M = lambda t: cells.append(nbf.v4.new_markdown_cell(t))
C = lambda t: cells.append(nbf.v4.new_code_cell(t))

M("""# ⑤ 솔루션 — 혼잡 지도 & 자원배치 권고
**11team · 서울 지하철 혼잡도 분석**

분석 결과(④)를 **운영팀이 바로 쓸 수 있는 형태**로 전환한다.
> 거창한 개발이 아니라, 데이터로 뒷받침된 **현실적·실현가능한 권고**.
1. 혼잡 핫스팟 **점수화** → 2. **folium 지도**(공간) + 3. **자원배치 권고**(우선순위)""")

C("""import pandas as pd, numpy as np, re, folium
SUBWAY_DIR = r"C:/Users/최용우/Downloads/drive-download-20260625T013956Z-3-001/dataset"
def read_csv_auto(p, **k):
    for e in ['utf-8-sig','cp949','euc-kr','utf-8']:
        try: return pd.read_csv(p, encoding=e, **k)
        except UnicodeDecodeError: continue
metro = read_csv_auto(f"{SUBWAY_DIR}/Seoul_subway_data_20210705.csv")
loc   = read_csv_auto(f"{SUBWAY_DIR}/subway_location_data.csv")
on_cols  = [c for c in metro.columns if '승차인원' in c]
off_cols = [c for c in metro.columns if '하차인원' in c]
slots    = [c.replace(' 승차인원','') for c in on_cols]
jun = metro[metro['사용월']==202106].copy()

def keyf(x): return re.sub(r'역$','', re.sub(r'\\(.*?\\)','', str(x))).strip()
def get_gu(a):
    p=str(a).split(); return p[1] if p and p[0].startswith('서울') else None
loc['key']=loc['지하철역'].apply(keyf); loc['자치구']=loc['주소'].apply(get_gu)
loc_xy = loc.drop_duplicates('key').set_index('key')
st = jun.groupby('지하철역')[on_cols+off_cols].sum().reset_index()
st['key']=st['지하철역'].apply(keyf)
st['자치구']=st['key'].map(loc_xy['자치구'])
st.loc[st['지하철역']=='서울역','자치구']='중구'
seoul = st[st['자치구'].notna()].copy()
print("서울 분석역:", len(seoul))""")

M("""## 1. 혼잡 핫스팟 점수화
- **총혼잡** = 하루 승차+하차 인원 (규모)
- **피크시간/피크혼잡** = 가장 붐비는 시간대와 그 인원 (집중도)
- **유형** = 아침 승차비율로 업무지구/베드타운/혼합 분류 (대응 방식이 다름)""")
C("""seoul['총혼잡'] = seoul[on_cols].sum(axis=1) + seoul[off_cols].sum(axis=1)
slot_tot = pd.DataFrame({slots[i]: seoul[on_cols[i]].values + seoul[off_cols[i]].values
                         for i in range(len(slots))}, index=seoul.index)
seoul['피크시간'] = slot_tot.idxmax(axis=1)
seoul['피크혼잡'] = slot_tot.max(axis=1)
am_on  = [c for c in on_cols  if c.startswith(('07시','08시'))]
am_off = [c for c in off_cols if c.startswith(('07시','08시'))]
ratio = seoul[am_on].sum(axis=1) / (seoul[am_on].sum(axis=1) + seoul[am_off].sum(axis=1))
seoul['유형'] = np.where(ratio < 0.4, '업무지구', np.where(ratio > 0.6, '베드타운', '혼합'))
seoul['위도'] = seoul['key'].map(loc_xy['x좌표']); seoul['경도'] = seoul['key'].map(loc_xy['y좌표'])
print(seoul['유형'].value_counts().to_string())
seoul.nlargest(5,'총혼잡')[['지하철역','유형','피크시간','피크혼잡']].to_string(index=False)""")

M("""## 2. folium 혼잡 지도
- **마커 크기** = 총혼잡(규모) · **색** = 역 유형 · **클릭 팝업** = 피크시간·혼잡 인원
- 밝은 CartoDB 타일로 가독성 확보 (Wilke: 데이터가 주인공)""")
C("""mapdf = seoul.dropna(subset=['위도','경도']).copy()
COL = {'업무지구':'#E63946', '베드타운':'#457B9D', '혼합':'#7B2CBF'}
mx = mapdf['총혼잡'].max()
m = folium.Map(location=[37.55,126.98], zoom_start=11, tiles='CartoDB positron')
for _, r in mapdf.iterrows():
    folium.CircleMarker(
        [r['위도'], r['경도']], radius=float(np.sqrt(r['총혼잡']/mx)*16 + 2),
        color=COL[r['유형']], fill=True, fill_color=COL[r['유형']], fill_opacity=0.55, weight=1,
        popup=folium.Popup(f"<b>{r['지하철역']}</b><br>유형: {r['유형']}<br>피크: {r['피크시간']}<br>"
                           f"피크 혼잡: {r['피크혼잡']:,.0f}명<br>총혼잡: {r['총혼잡']:,.0f}명", max_width=230)
    ).add_to(m)
legend = ('<div style="position:fixed; bottom:28px; left:28px; z-index:9999; background:white; '
          'padding:10px 14px; border-radius:8px; box-shadow:0 1px 5px rgba(0,0,0,.25); '
          'font-family:Malgun Gothic,sans-serif; font-size:13px; line-height:1.6;">'
          '<b>역 유형</b><br>'
          '<span style="color:#E63946">●</span> 업무지구(아침 하차)<br>'
          '<span style="color:#457B9D">●</span> 베드타운(아침 승차)<br>'
          '<span style="color:#7B2CBF">●</span> 혼합 허브<br>'
          '<span style="color:#888">● 크기 = 혼잡 규모</span></div>')
m.get_root().html.add_child(folium.Element(legend))
import os
_out = "outputs" if os.path.isdir("outputs") else "../outputs"
m.save(f"{_out}/혼잡지도.html")
print(f"지도 저장: {_out}/혼잡지도.html | 마커 {len(mapdf)}개")
m""")

M("""## 3. 자원배치 권고 (현실적·실현가능)
피크혼잡 상위 역을 **유형별**로 정리 → 운영팀 자원 우선 투입 대상.""")
C("""hot = seoul.nlargest(12,'피크혼잡')[['지하철역','자치구','유형','피크시간','피크혼잡']].copy()
hot['피크혼잡'] = hot['피크혼잡'].round(0).astype(int)
print("=== 혼잡 핫스팟 Top 12 (피크 기준) ===")
print(hot.to_string(index=False))""")
M("""### 운영 권고 (So What)
| 유형 | 대상 역(예) | 피크 | 권고 |
|---|---|---|---|
| **업무지구** | 가산디지털단지·여의도·삼성·서울역 | **18–19시 퇴근** | 저녁 피크 **증차·안전인력**, 승강장 하행 혼잡 관리 |
| **베드타운** | 신림·서울대입구·사당 | **08–09시 출근** | 아침 피크 인력, 상행 승강장·게이트 집중 |
| **혼합 허브** | 강남·잠실·홍대입구 | **종일(특히 18–19시)** | 상시 관리 + 양방향 안내, 환승 동선 분산 |

> 한정된 자원은 **피크혼잡 Top + 유형별 시간대**에 우선 배치 — '감'이 아닌 데이터 우선순위.""")

M("""---
## ✅ 솔루션 요약
- 혼잡 점수화 → **folium 지도**(공간 분포) + **권고 리스트**(우선순위)를 같은 근거로 통합
- 운영팀은 *"어느 역·어느 시간에 자원을 먼저"*를 데이터로 판단 가능
### ▶ 다음 (⑥ 보고서·발표)
SCQA + heartcount 원칙으로 발표자료(장표) + 보고서 제작""")

nb.cells = cells; nb.metadata = {"language_info": {"name":"python"}}
nbf.write(nb, "notebooks/05_솔루션.ipynb")
print("written: notebooks/05_솔루션.ipynb")
