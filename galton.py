import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from math import comb, sqrt, pi, exp

st.set_page_config(layout="wide")
st.title("Galton Board — Central Limit Theorem")

st.markdown("""
Each ball undergoes left/right decisions at pegs.  
As the number of layers increases, the final distribution  
converges to a **Gaussian**.
""")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Controls")
    N_LAYERS = st.slider("Peg Layers", 10, 50, 25)
    N_COLS = st.slider("Columns (Width)", 10, 80, 40)
    BALLS = st.slider("Balls per Burst", 10, 500, 100)
    bias = st.slider("Right Step Probability", 0.0, 1.0, 0.5)
    speed = st.slider("Animation Speed", 0.005, 0.1, 0.03)

    if st.button("Reset"):
        st.session_state.initialized = False
        st.rerun()

if "initialized" not in st.session_state:
    st.session_state.initialized = False

def reset():
    st.session_state.paths = []
    st.session_state.bins = np.zeros(N_LAYERS+1, dtype=int)
    st.session_state.initialized = True

if not st.session_state.initialized:
    reset()

# ---------------- Layout ----------------
col_board, col_hist = st.columns([1.2, 1])
board_ph = col_board.empty()
hist_ph = col_hist.empty()

run = st.toggle("Drop Balls")

# ---------------- Helper ----------------
def theoretical_curve(n, p):
    xs = np.arange(n+1)
    probs = np.array([comb(n, k)*(p**k)*((1-p)**(n-k)) for k in xs])
    return xs, probs / probs.max()

# ---------------- Simulation ----------------
if run:
    for _ in range(BALLS):
        x = N_COLS // 2
        y = 0
        path = [(x, y)]

        for layer in range(N_LAYERS):
            if np.random.rand() < bias:
                x += 1
            else:
                x -= 1
            y += 1
            path.append((x, y))

        st.session_state.paths.append(path)

        final_bin = x - (N_COLS // 2)
        idx = final_bin + N_LAYERS // 2
        if 0 <= idx < len(st.session_state.bins):
            st.session_state.bins[idx] += 1

        # ----- Draw board -----
        H = N_LAYERS + 2
        W = N_COLS + 4
        fig = np.zeros((H, W, 3))

        # draw pegs
        for row in range(1, N_LAYERS):
            for col in range(N_COLS//2 - row, N_COLS//2 + row, 2):
                if 0 <= col < W:
                    fig[row, col] = [0.8, 0.8, 0.8]

        # draw last 200 paths
        for pth in st.session_state.paths[-200:]:
            for (px, py) in pth:
                if 0 <= py < H and 0 <= px < W:
                    fig[py, px] = [1, 0.3, 0.3]

        board_ph.image(fig, clamp=True)

        # ----- Histogram + theory -----
        xs = np.arange(len(st.session_state.bins))
        df = pd.DataFrame({"Bin": xs, "Count": st.session_state.bins})

        theo_x, theo = theoretical_curve(N_LAYERS, bias)
        theo = theo * df["Count"].max()

        df_theo = pd.DataFrame({"Bin": theo_x + xs.mean() - theo_x.mean(), "Count": theo})

        bars = alt.Chart(df).mark_bar(color="#6699cc").encode(
            x="Bin:O", y="Count"
        )

        line = alt.Chart(df_theo).mark_line(color="red").encode(
            x="Bin:O", y="Count"
        )

        hist_ph.altair_chart((bars + line).properties(title="Final Bin Distribution"), use_container_width=True)

        time.sleep(speed)
