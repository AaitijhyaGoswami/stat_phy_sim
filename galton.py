import streamlit as st
import numpy as np
import plotly.graph_objects as go
from math import comb

st.set_page_config(layout="wide")
st.title("Galton Board — Central Limit Theorem")

st.markdown("""
Balls pass through rows of pegs and randomly deflect left or right.  
After many trials, the final bin distribution converges to a **Gaussian**.
""")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Controls")
    N_LAYERS = st.slider("Peg Rows", 6, 30, 15)
    N_BALLS = st.slider("Number of Balls", 100, 20000, 5000, step=500)
    bias = st.slider("Right Step Probability", 0.0, 1.0, 0.5)
    run = st.button("Run Simulation")

# ---------------- Simulation ----------------
if run:
    positions = []
    paths = []

    for _ in range(N_BALLS):
        x = 0
        y = 0
        path_x = [x]
        path_y = [y]

        for _ in range(N_LAYERS):
            if np.random.rand() < bias:
                x += 1
            else:
                x -= 1
            y -= 1
            path_x.append(x)
            path_y.append(y)

        positions.append(x)
        paths.append((path_x, path_y))

    # bins
    bins = np.zeros(N_LAYERS+1)
    for p in positions:
        idx = int(round(p + N_LAYERS/2))
        if 0 <= idx < len(bins):
            bins[idx] += 1

    # ---------------- Peg Geometry ----------------
    peg_x, peg_y = [], []
    for row in range(N_LAYERS):
        for col in range(row + 1):
            peg_x.append(col - row/2)
            peg_y.append(-row)

    # ---------------- Board Plot ----------------
    fig_board = go.Figure()

    fig_board.add_trace(go.Scatter(
        x=peg_x, y=peg_y,
        mode="markers",
        marker=dict(size=8, color="black"),
        name="Pegs"
    ))

    # draw only last 200 paths for clarity
    for px, py in paths[-200:]:
        fig_board.add_trace(go.Scatter(
            x=px, y=py,
            mode="lines",
            line=dict(color="red"),
            showlegend=False
        ))

    fig_board.update_layout(
        title="Galton Board with Ball Trajectories",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        height=500
    )

    st.plotly_chart(fig_board, use_container_width=True)

    # ---------------- Histogram + Theory ----------------
    k = np.arange(len(bins))
    theo = np.array([comb(N_LAYERS, i)*(bias**i)*((1-bias)**(N_LAYERS-i)) for i in k])
    theo = theo / theo.max() * max(bins)

    fig_hist = go.Figure()
    fig_hist.add_bar(x=k, y=bins, name="Observed")
    fig_hist.add_scatter(x=k, y=theo, mode="lines",
                         name="Binomial / Gaussian",
                         line=dict(color="red"))

    fig_hist.update_layout(
        title="Final Bin Distribution",
        xaxis_title="Bin",
        yaxis_title="Count",
        height=400
    )

    st.plotly_chart(fig_hist, use_container_width=True)
