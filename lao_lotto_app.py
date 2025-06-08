# ─── Lao-AI v4.0 ───  (Streamlit ≥ 1.32  •  pandas)
import streamlit as st, pandas as pd
from collections import Counter, defaultdict
from itertools import combinations, islice
import random, math

# ───────── CONFIG ─────────
ALPHA_EWMA   = 0.87       # ถ่วงน้ำหนักเลขเด่น
PAIR_TOP_N   = 12         # ดึง top-N จากแต่ละตำแหน่งก่อน cross-mix
PAIRS_KEEP   = 20         # ชุดสองตัวที่แอปแสดง
TRIPLE_KEEP  = 20         # ชุดสามตัว
QUAD_KEEP    = 20         # ชุดสี่ตัว (ไม่เปิดตำแหน่ง)
MIN_DRAW     = 10         # ข้อมูลย้อนหลังขั้นต่ำ

st.set_page_config(page_title='หวยลาว AI v4.0', page_icon='🇱🇦', layout='centered')
st.title('🎯 Lao-AI v4 – EWMA + 2-Pos Markov + Unordered Combos')

# ───────── INPUT ─────────
raw = st.text_area('📥 วางผล 4-หลัก (หนึ่งบรรทัด/งวด)', height=180)
draws = [l.strip() for l in raw.splitlines() if l.strip().isdigit() and len(l.strip()) == 4]

st.write(f'📊 โหลดแล้ว **{len(draws)}** งวด')

if len(draws) < MIN_DRAW:
    st.info(f'ต้องการอย่างน้อย {MIN_DRAW} งวด')
    st.stop()

st.dataframe(pd.DataFrame(draws, columns=['เลข 4 หลัก']), use_container_width=True)

# ───────── HELPER ─────────
def ewma_digit(hist, alpha=ALPHA_EWMA, top_k=1):
    sc = Counter()
    for i, num in enumerate(reversed(hist)):
        w = alpha ** i
        for d in num:
            sc[d] += w
    return [d for d, _ in sc.most_common(top_k)]

def build_pos_markov(hist):
    pos1, pos2 = defaultdict(Counter), defaultdict(Counter)   # 2 ตำแหน่ง (พัน+ร้อย) & (สิบ+หน่วย)
    for p, c in zip(hist[:-1], hist[1:]):
        pos1[p[:2]][c[:2]] += 1
        pos2[p[2:]][c[2:]] += 1
    return pos1, pos2

def two_combo_markov(hist, keep=PAIRS_KEEP, n_each=PAIR_TOP_N):
    p1, p2 = build_pos_markov(hist)
    last1, last2 = hist[-1][:2], hist[-1][2:]
    cand1 = [x for x, _ in p1[last1].most_common(n_each)]
    cand2 = [x for x, _ in p2[last2].most_common(n_each)]

    combos = {"".join(sorted(a + b)) for a in cand1 for b in cand2}
    # เติม hot-digit ให้ครบถ้าไม่ถึง keep
    hot = ewma_digit(hist, top_k=3)
    for a, b in combinations(hot, 2):
        combos.add("".join(sorted(a + b)))
        if len(combos) >= keep:
            break
    return list(islice(combos, keep))

def unordered_multiset(nums, k_keep):
    combos = sorted(nums, key=lambda x: (len(set(x)), x))  # just sort for consistency
    return combos[:k_keep]

def three_combo(hist, keep=TRIPLE_KEEP):
    pool = list(dict.fromkeys(ewma_digit(hist, top_k=5) + list(hist[-1])))[:8]
    triples = {"".join(sorted(c)) for c in combinations(pool, 3)}
    return unordered_multiset(triples, keep)

def four_combo(hist, keep=QUAD_KEEP):
    pool = list(dict.fromkeys(ewma_digit(hist, top_k=6) + list(hist[-1])))[:10]
    quads = {"".join(sorted(c)) for c in combinations(pool, 4)}
    return unordered_multiset(quads, keep)

# ───────── CALCULATE ─────────
hot_digit     = ewma_digit(draws)[0]
pair20        = two_combo_markov(draws)
triple20      = three_combo(draws)
quad20        = four_combo(draws)

focus_pairs   = pair20[:5]
focus_triple  = triple20[0]

# ───────── DISPLAY ─────────
st.markdown(f"<h2 style='color:red;text-align:center'>เลขเด่น: {hot_digit}</h2>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader('สองตัว (20 ชุด • ไม่สนตำแหน่ง)')
    st.markdown('<br>'.join('  '.join(pair20[i:i+10]) for i in range(0, len(pair20), 10)),
                unsafe_allow_html=True)

with c2:
    st.subheader('สามตัว (20 ชุด • เต็ง-โต๊ด)')
    st.markdown('<br>'.join('  '.join(triple20[i:i+10]) for i in range(0, len(triple20), 10)),
                unsafe_allow_html=True)

st.subheader('สี่ตัว (20 ชุด • ไม่สนตำแหน่ง)')
st.markdown('<br>'.join('  '.join(quad20[i:i+10]) for i in range(0, len(quad20), 10)),
            unsafe_allow_html=True)

st.subheader('🚩 ชุดเน้น')
st.markdown(f"**สองตัว:** {', '.join(focus_pairs)}\n\n**สามตัว:** {focus_triple}")

# ───────── (OPTIONAL) QUICK HIT-RATE TEST ─────────
def hit2(pred, act): return "".join(sorted(act[2:])) in pred or "".join(sorted(act[:2])) in pred
def hit3(pred, act): return "".join(sorted(act)) in pred
def walk(hist, fn, hit, start=MIN_DRAW):
    h=t=0
    for i in range(start, len(hist)):
        if hit(fn(hist[:i]), hist[i]): h+=1
        t+=1
    return h/t if t else 0
if len(draws) >= 40:
    st.caption(f"Hit-ย้อนหลัง (20 ชุด): สองตัว≈{walk(draws, two_combo_markov, hit2)*100:.1f}% | "
               f"สามตัว≈{walk(draws, three_combo, hit3)*100:.1f}%")

st.caption('© 2025 Lao-AI v4.0 – EWMA & Two-Pos Markov')
