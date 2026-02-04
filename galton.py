import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from math import comb

st.set_page_config(layout="wide")
st.title("Galton Board — Central Limit Theorem")

st.markdown("""
Each ball passes through rows of pegs, randomly deflecting left or right.  
After many trials, the final bin distribution converges to a **Gaussian**.
""")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Controls")
    N_LAYERS = st.slider("Peg Rows", 6, 30, 12)
    N_BALLS = st.slider("Number of Balls", 10, 5000, 500)
    bias = st.slider("Right Step Probability", 0.0, 1.0, 0.5)

    run = st.button("Run Simulation")

# ---------------- Simulation ----------------
if run:
    positions = []
    for _ in range(N_BALLS):
        pos = 0
        for _ in range(N_LAYERS):
            pos += 1 if np.random.rand() < bias else -1
        positions.append(pos)

    bins = np.zeros(N_LAYERS+1)
    for p in positions:
        idx = int(round(p + N_LAYERS/2))
        if 0 <= idx < len(bins):
            bins[idx] += 1

    # ---------------- Plot ----------------
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(range(len(bins)), bins, alpha=0.7, label="Observed")

    k = np.arange(N_LAYERS+1)
    theo = np.array([comb(N_LAYERS, i)*(bias**i)*((1-bias)**(N_LAYERS-i)) for i in k])
    theo = theo / theo.max() * max(bins)
    ax.plot(k, theo, 'r-', lw=2, label="Binomial / Gaussian")

    ax.set_title("Final Bin Distribution")
    ax.set_xlabel("Bin")
    ax.set_ylabel("Count")
    ax.legend()

    st.pyplot(fig)
