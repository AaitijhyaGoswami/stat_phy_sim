import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
from math import comb

st.set_page_config(layout="wide")
st.title("Galton Board — Central Limit Theorem")

st.markdown("""
Balls fall through pegs and randomly deflect left or right.  
The final bin distribution converges to a **Gaussian**.
""")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Controls")
    N_LAYERS = st.slider("Peg Rows", 6, 20, 12)
    BALLS = st.slider("Balls per Drop", 1, 50, 10)
    bias = st.slider("Right Probability", 0.0, 1.0, 0.5)
    speed = st.slider("Animation Speed", 0.01, 0.2, 0.05)

    if st.button("Reset"):
        st.session_state.init = False
        st.rerun()

# ---------------- Init ----------------
if "init" not in st.session_state:
    st.session_state.init = False

if not st.session_state.init:
    st.session_state.bins = np.zeros(N_LAYERS + 1, dtype=int)
    st.session_state.paths = []
    st.session_state.init = True

# ---------------- Peg Geometry ----------------
peg_x, peg_y = [], []
for row in range(N_LAYERS):
    for col in range(row + 1):
        peg_x.append(col - row / 2)
        peg_y.append(-row)

# ---------------- Layout ----------------
col_anim, col_hist = st.columns([1.5, 1])
anim_ph = col_anim.empty()
hist_ph = col_hist.empty()

run = st.toggle("Drop Balls")

# ---------------- Theory ----------------
def theoretical(n, p):
    k = np.arange(n+1)
    probs = np.array([comb(n, i)*(p**i)*((1-p)**(n-i)) for i in k])
    return k, probs / probs.max()

# ---------------- Simulation ----------------
if run:
    for _ in range(BALLS):
        x = 0
        y = 0
        path_x = [x]
        path_y = [y]

        for layer in range(N_LAYERS):
            if np.random.rand() < bias:
                x += 0.5
            else:
                x -= 0.5
            y -= 1
            path_x.append(x)
            path_y.append(y)

        st.session_state.paths.append((path_x, path_y))
        bin_idx = int(round(x + N_LAYERS/2))
        st.session_state.bins[bin_idx] += 1

        # ----- Animate -----
        fig = go.Figure()

        # pegs
        fig.add_trace(go.Scatter(
            x=peg_x, y=peg_y,
            mode="markers",
            marker=dict(size=10, color="black"),
            name="Pegs"
        ))

        # balls
        for px, py in st.session_state.paths[-20:]:
            fig.add_trace(go.Scatter(
                x=px, y=py,
                mode="lines+markers",
                line=dict(color="red"),
                marker=dict(size=6),
                showlegend=False
            ))

        fig.update_layout(
            xaxis=dict(range=[-N_LAYERS/1.5, N_LAYERS/1.5], showgrid=False, zeroline=False),
            yaxis=dict(range=[-N_LAYERS-2, 1], showgrid=False, zeroline=False),
            height=500,
            title="Galton Board"
        )

        anim_ph.plotly_chart(fig, use_container_width=True)

        # ----- Histogram + theory -----
        k = np.arange(len(st.session_state.bins))
        df = {"Bin": k, "Count": st.session_state.bins}

        k_t, th = theoretical(N_LAYERS, bias)
        th = th * max(st.session_state.bins.max(), 1)

        fig2 = go.Figure()
        fig2.add_bar(x=k, y=st.session_state.bins, name="Observed")
        fig2.add_scatter(x=k_t, y=th, mode="lines", name="Theory", line=dict(color="red"))

        hist_ph.plotly_chart(fig2, use_container_width=True)

        time.sleep(speed)
