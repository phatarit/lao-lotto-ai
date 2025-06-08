# Lao-AI v4.1 – Analysis-only  (ไม่แสดงผลทำนาย)
import streamlit as st, pandas as pd
from collections import Counter, defaultdict
from itertools import combinations
import random

# ───────── CONFIG ─────────
MIN_DRAW   = 10               # ข้อมูลขั้นต่ำ 10 งวด
ALPHA_EWMA = 0.87             # ค่าถ่วงสำหรับสถิติ EWMA

st.set_page_config(page_title='หวยลาว – วิเคราะห์ย้อนหลัง', page_icon='🇱🇦')
st.title('📊 Lao-Lottery Retrospective Analyzer (No Prediction)')

# ───────── INPUT ─────────
raw = st.text_area('วางผลหวยลาว 4 หลัก (1 บรรทัด/งวด)', height=200,
                   placeholder='เช่น 9767\n5319\n1961 …')

draws = [l.strip() for l in raw.splitlines()
         if l.strip().isdigit() and len(l.strip()) == 4]

st.write(f'📥 คุณใส่ข้อมูล **{len(draws)}** งวด')

if len(draws) < MIN_DRAW:
    st.info(f'กรุณาใส่ข้อมูลอย่างน้อย {MIN_DRAW} งวดเพื่อดูสถิติย้อนหลัง')
    st.stop()

st.dataframe(pd.DataFrame(draws, columns=['เลข 4 หลัก']),
             use_container_width=True)

# ────────── สถิติเบื้องต้น ──────────
last_1 = draws[-1]
last_2 = draws[-2] if len(draws) >= 2 else ''
last_3 = draws[-3] if len(draws) >= 3 else ''

flow  = [d for d in last_1 if d in last_2]  # เลขไหล
cross
