import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from math import comb, sqrt, pi, exp

st.set_page_config(layout="wide")
st.title("Galton Board — Central Limit Theorem")

st.markdown("""
Each row is a Bernoulli trial.  
Each ball makes a left/right choice at every peg.  
The accumulation of many trials converges to a **Gaussian**.
""")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Controls")
    N_LAYERS = st.slider("Number of Peg Rows", 10, 60, 30)
    N_BALLS = st.slider("Balls per Batch", 10, 300, 100)
    bias = st.slider("Right Step Probability p", 0.0, 1.0, 0.5)
    speed = st.slider("Animation Speed", 0.01, 0.15, 0.04)

    if st.button("Reset"):
        st.session_state.init = False
        st.rerun()

# ---------------- Init ----------------
if "init" not in st.session_state:
    st.session_state.init = False

def reset():
    st.session_state.active = []
    st.session_state.bins = np.zeros(N_LAYERS + 1, dtype=int)
    st.session_state.init = True

if not st.session_state.init:
    reset()

# ---------------- Layout ----------------
col_board, col_hist = st.columns([1.4, 1])
board_ph = col_board.empty()
hist_ph = col_hist.empty()

run = st.toggle("Drop Balls")

# ---------------- Theory ----------------
def binomial_curve(n, p):
    k = np.arange(n+1)
    probs = np.array([comb(n, i)*(p**i)*((1-p)**(n-i)) for i in k])
    return k, probs / probs.max()

# ---------------- Simulation ----------------
if run:
    for _ in range(N_BALLS):
        pos = N_LAYERS // 2
        path = [pos]

        for _ in range(N_LAYERS):
            pos += 1 if np.random.rand() < bias else -1
            path.append(pos)

        st.session_state.active.append(path)
        st.session_state.bins[path[-1]] += 1

        # ----- Draw board -----
        board = np.zeros((N_LAYERS+2, 2*N_LAYERS+1, 3))

        # pegs
        for r in range(N_LAYERS):
            for c in range(N_LAYERS-r, N_LAYERS+r+1, 2):
                board[r, c] = [0.7, 0.7, 0.7]

        # balls
        for pth in st.session_state.active[-200:]:
            for y, x in enumerate(pth):
                board[y, x] = [1, 0.3, 0.3]

        board_ph.image(np.kron(board, np.ones((6,6,1))), clamp=True)

        # ----- Histogram + theory -----
        xs = np.arange(len(st.session_state.bins))
        df = pd.DataFrame({"Bin": xs, "Count": st.session_state.bins})

        k, theo = binomial_curve(N_LAYERS, bias)
        theo = theo * df["Count"].max()

        df_theo = pd.DataFrame({
            "Bin": k + xs.mean() - k.mean(),
            "Count": theo
        })

        bars = alt.Chart(df).mark_bar(color="#6699cc").encode(
            x="Bin:O", y="Count"
        )

        line = alt.Chart(df_theo).mark_line(color="red").encode(
            x="Bin:O", y="Count"
        )

        hist_ph.altair_chart(
            (bars + line).properties(title="Final Bin Distribution"),
            use_container_width=True
        )

        time.sleep(speed)
