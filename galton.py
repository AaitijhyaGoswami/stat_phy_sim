import streamlit as st
import numpy as np
import plotly.graph_objects as go

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
    N_BINS = st.slider("Histogram Bin Density", 20, 300, 120)
    SCALE = st.slider("Bar Spacing Scale", 0.05, 1.0, 0.25)
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

    positions = np.array(positions)

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

    # draw last 200 paths for clarity
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

    # ---------------- Dense Histogram + Gaussian ----------------
    scaled_pos = positions * SCALE

    hist_y, hist_x = np.histogram(scaled_pos, bins=N_BINS)
    hist_centers = (hist_x[:-1] + hist_x[1:]) / 2

    mu = np.mean(scaled_pos)
    sigma = np.std(scaled_pos)

    x_cont = np.linspace(hist_centers.min(), hist_centers.max(), 400)
    gauss = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-(x_cont-mu)**2/(2*sigma**2))
    gauss = gauss / gauss.max() * hist_y.max()

    fig_hist = go.Figure()
    fig_hist.add_bar(x=hist_centers, y=hist_y, name="Observed", opacity=0.7)
    fig_hist.add_scatter(x=x_cont, y=gauss, mode="lines",
                         name="Gaussian Fit", line=dict(color="red", width=3))

    fig_hist.update_layout(
        title="Final Bin Distribution (Smoothed)",
        xaxis_title="Final Position (scaled)",
        yaxis_title="Count",
        height=400
    )

    st.plotly_chart(fig_hist, use_container_width=True)
