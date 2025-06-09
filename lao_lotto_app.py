import streamlit as st, pandas as pd, math, random
from collections import Counter, defaultdict
from itertools import combinations

# ───────────────── CONFIG ─────────────────
st.set_page_config(page_title="LoasLottoAI", page_icon="🇱🇦", layout="centered")
st.title("🎯 LoasLottoAI")

MIN_DRAW        = 30        # ข้อมูลย้อนหลังขั้นต่ำ
WINDOW_DIGIT    = 60        # หน้าต่างคำนวณตัวเด่น
PAIR_TOP_MARK   = 40        # Top-k 4-Markov
PAIR_KEEP       = 10        # เจาะคู่ 10 ชุด
TRIPLE_KEEP     = 10        # เจาะสามตัว 10 ชุด
ALPHA_GRID      = [0.80,0.85,0.90,0.93,0.96]
SPECIAL_DIGITS  = ['4','5','6','2']  # เลขพิเศษผสมทุกชุด

# ───────────────── INPUT ─────────────────
raw = st.text_area(
    "📥 วางผลหวยลาว 4 หลัก (บรรทัดละ 1 งวด)", height=220,
    placeholder="เช่น 9767\n5319\n1961 …"
)
draws = [l.strip() for l in raw.splitlines() if l.strip().isdigit() and len(l.strip())==4]
st.write(f"📊 โหลดแล้ว **{len(draws)}** งวด")
if len(draws) < MIN_DRAW:
    st.info(f"⚠️ ต้องมีข้อมูลอย่างน้อย {MIN_DRAW} งวด")
    st.stop()
st.dataframe(pd.DataFrame(draws, columns=["เลข 4 หลัก"]), use_container_width=True)

# ───────────────── HELPER ─────────────────
def ewma_digit(hist, alpha, top_k=1):
    sc = Counter()
    for i, num in enumerate(reversed(hist)):
        w = alpha ** i
        for d in num:
            sc[d] += w
    return [d for d, _ in sc.most_common(top_k)]

def build_markov4(hist):
    M = defaultdict(Counter)
    for p, c in zip(hist[:-1], hist[1:]):
        M[p][c] += 1
    return M

def unordered2(a, b):
    return "".join(sorted(a + b))

def unordered3(t):
    return "".join(sorted(t))

# ───────────────── α CV ─────────────────
def quick_hit_pairs(hist, alpha, n_eval=50):
    if len(hist) < MIN_DRAW + 5:
        return 0
    hits = tot = 0
    for i in range(MIN_DRAW, len(hist)):
        pairs = two_combo(hist[:i], alpha)
        matched = False
        for x in range(4):
            for y in range(x + 1, 4):
                if unordered2(hist[i][x], hist[i][y]) in pairs:
                    hits += 1
                    matched = True
                    break
            if matched:
                break
        tot += 1
        if tot == n_eval:
            break
    return hits / tot if tot else 0

def choose_alpha(hist):
    best, score = ALPHA_GRID[0], -1
    for a in ALPHA_GRID:
        s = quick_hit_pairs(hist, a)
        if s > score:
            best, score = a, s
    return best

# ───────────────── CORE FUNCTIONS ─────────────────
def hot_digit(hist, alpha):
    freq = Counter("".join(hist[-WINDOW_DIGIT:]))
    trend = Counter("".join(hist[-5:])) - Counter("".join(hist[-WINDOW_DIGIT:-5]))
    score = {d: 0.6 * freq[d] + 0.4 * trend[d] + 0.2 for d in "0123456789"}
    return max(score, key=score.get)

def two_combo(hist, alpha):
    M = build_markov4(hist)
    mark_pred = [p for p, _ in M[hist[-1]].most_common(PAIR_TOP_MARK)]
    base_pairs = [unordered2(x, y) for m in mark_pred for x, y in combinations(m, 2)]
    # momentum pairs (occurrence ≥3 in 20 งวด)
    recent = hist[-20:]
    cnt = Counter(unordered2(d[i], d[j]) for d in recent for i in range(4) for j in range(i+1, 4))
    mom = [p for p, c in cnt.items() if c >= 3]
    # special pairs from SPECIAL_DIGITS
    special_pairs = [unordered2(a, b) for a, b in combinations(SPECIAL_DIGITS, 2)]
    # missing digits from last 5 draws
    recent5 = hist[-5:]
    missing = [d for d in '0123456789' if all(d not in draw for draw in recent5)]
    missing_pairs = [unordered2(a, b) for a, b in combinations(missing, 2)]
    combos = list(dict.fromkeys(base_pairs + mom + special_pairs + missing_pairs))[:PAIR_KEEP]
    return combos

def three_combo(hist, alpha):
    pool = list(dict.fromkeys(
        ewma_digit(hist, alpha, top_k=5)
        + list(hist[-1])
        + [hot_digit(hist, alpha)]
        + SPECIAL_DIGITS
    ))[:15]
    # include missing digits
    recent5 = hist[-5:]
    missing = [d for d in '0123456789' if all(d not in draw for draw in recent5)]
    pool += missing
    pool = list(dict.fromkeys(pool))[:15]
    cnt = Counter("".join(hist[-30:]))
    score = lambda t: math.prod(cnt[d] + 1 for d in t)
    triples = sorted({unordered3(c) for c in combinations(pool, 3)}, key=score, reverse=True)
    return triples[:TRIPLE_KEEP]

# ───────────────── CALC & DISPLAY ─────────────────
a = choose_alpha(draws)
main_digit = hot_digit(draws, a)
combo_two = two_combo(draws, a)
combo_three = three_combo(draws, a)
# สร้างสี่ตัว: หลักพันคงเดิม + ตัวเด่นจากชุดสามตัวแรก
thousands = draws[-1][0]
four_digit = thousands + combo_three[0]

# แสดงผล
st.markdown(
    f"<h2 style='color:red;text-align:center'>รูด 19 ประตู: {main_digit}</h2>", unsafe_allow_html=True
)
c1, c2 = st.columns(2)
with c1:
    st.subheader("เจาะสองตัว (10 ชุด ไม่สนตำแหน่ง)")
    st.markdown("  ".join(combo_two), unsafe_allow_html=True)
with c2:
    st.subheader("เจาะสามตัว (10 ชุด ไม่สนตำแหน่ง)")
    st.markdown(
        "<br>".join(
            "  ".join(combo_three[i:i+5]) for i in range(0, len(combo_three), 5)
        ),
        unsafe_allow_html=True,
    )
st.subheader("เจาะสี่ตัว (1 ชุด)")
st.markdown(
    f"<div style='font-size:28px;color:red;text-align:center'>{four_digit}</div>",
    unsafe_allow_html=True
)
st.caption("© 2025 LoasLottoAI – Adaptive EWMA & 4-Markov")
