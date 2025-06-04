import streamlit as st
import pandas as pd
from collections import Counter
import random

st.set_page_config(page_title="หวยลาว AI", layout="centered")
st.title("🇱🇦 วิเคราะห์หวยลาวด้วย AI")
st.caption("ระบบวิเคราะห์หวยลาว 4 หลัก พร้อมทำนายเลขเด่น สองตัว สามตัว สี่ตัว")

if "lao_lotto" not in st.session_state:
    st.session_state.lao_lotto = []

# 🧾 ช่องวางข้อมูลย้อนหลัง
st.subheader("📥 วางข้อมูลย้อนหลังแบบชุด")
bulk_input = st.text_area("วางผลหวย เช่น 1234\n4567\n7890", height=120)
if st.button("📌 เพิ่มจากข้อความ"):
    added = 0
    for line in bulk_input.strip().split("\n"):
        num = line.strip()
        if num.isdigit() and len(num) == 4:
            st.session_state.lao_lotto.append(num)
            added += 1
    st.success(f"✅ เพิ่มแล้ว {added} รายการ")

# ✏️ กรอกข้อมูลทีละงวด
st.subheader("➕ เพิ่มข้อมูล 1 งวด (4 หลัก)")
cols = st.columns(4)
d1 = cols[0].text_input("หลักพัน", max_chars=1)
d2 = cols[1].text_input("หลักร้อย", max_chars=1)
d3 = cols[2].text_input("หลักสิบ", max_chars=1)
d4 = cols[3].text_input("หลักหน่วย", max_chars=1)

if st.button("➕ เพิ่มข้อมูล 1 งวด"):
    if all([d.isdigit() for d in [d1, d2, d3, d4]]):
        st.session_state.lao_lotto.append(d1 + d2 + d3 + d4)
        st.success("✅ เพิ่มข้อมูลแล้ว")
    else:
        st.warning("⚠️ กรุณากรอกเลขให้ครบทุกหลัก")

if st.button("🗑️ ลบรายการล่าสุด"):
    if st.session_state.lao_lotto:
        st.session_state.lao_lotto.pop()
        st.success("🧹 ลบรายการล่าสุดแล้ว")

# 📊 วิเคราะห์
if st.session_state.lao_lotto:
    df = pd.DataFrame(st.session_state.lao_lotto, columns=["เลข 4 หลัก"])
    st.dataframe(df)

    last_1 = st.session_state.lao_lotto[-1]
    last_2 = st.session_state.lao_lotto[-2] if len(st.session_state.lao_lotto) >= 2 else ""
    last_3 = st.session_state.lao_lotto[-3] if len(st.session_state.lao_lotto) >= 3 else ""

    flow = [d for d in last_1 if d in last_2]
    cross = [d for d in last_1 if d in last_3]
    recent_10 = st.session_state.lao_lotto[-10:]
    all_digits = "".join(recent_10)
    freq_all = Counter(all_digits).most_common()
    most_freq = freq_all[0][0] if freq_all else "-"
    missing = [d for d in "0123456789" if d not in "".join(st.session_state.lao_lotto[-5:])]
    random_digit = str(random.choice("0123456789"))

    st.subheader("📊 วิเคราะห์ข้อมูลย้อนหลัง")
    st.markdown(f"**1. เลขไหล:** {' '.join(flow) if flow else 'ไม่มี'}")
    st.markdown(f"**2. เลขข้ามงวด:** {' '.join(cross) if cross else 'ไม่มี'}")
    st.markdown(f"**3. เลขซ้ำบ่อย (10 งวด):** {freq_all}")
    st.markdown(f"**4. เลขหายนาน (5 งวด):** {', '.join(missing)}")
    st.markdown(f"**5. เลขสุ่ม:** {random_digit}")

    # 🔮 ทำนาย
    st.subheader("🔮 ทำนายงวดถัดไป")
    digit = most_freq
    pairs = [f"{digit}{(int(digit)+i)%10}" for i in range(1, 5)]
    lead_pair = random.choice(pairs)
    triple = [f"{lead_pair[0]}{lead_pair[1]}{i}" for i in range(10)]
    triple_random = f"{random.randint(0,9)}{digit}{random.randint(0,9)}"
    quad = f"{random.randint(1,9)}{digit}{random.randint(0,9)}{random.randint(0,9)}"

    st.markdown(f"<h2 style='color:red;'>เลขเด่น: {digit}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:red;'>เลขสองตัวแนะนำ: {', '.join(pairs)}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:red;'>เลขลากสามตัว: {' '.join(triple)}</h4>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:red;'>เลขเสียวสามตัว: {triple_random}</h4>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:red;'>เลขโชคสี่ตัว: {quad}</h4>", unsafe_allow_html=True)

else:
    st.info("กรุณากรอกข้อมูลหวยลาวอย่างน้อย 1 งวด")
