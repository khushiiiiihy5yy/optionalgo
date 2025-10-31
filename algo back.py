# enhanced_option_simulator.py
"""
Enhanced Educational Simulation of Low-Liquidity Option Manipulation
--------------------------------------------------------------------

⚠️ Educational purpose only. This simulates how a manipulative algorithm
in an illiquid option market can influence naive traders' execution prices.

Author: [Your Name]
Repo: https://github.com/[your-username]/option-simulation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------------------------------------
# PAGE CONFIG & STYLING
# -----------------------------------------------------------
st.set_page_config(
    page_title="Option Manipulation Simulator (Educational)",
    layout="wide",
    page_icon="💹",
)

# CSS custom style for a better UI
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #1f1c2c, #928DAB);
        color: #fff;
    }
    .stApp {
        background: linear-gradient(135deg, #1f1c2c, #928DAB);
    }
    h1, h2, h3 {
        color: #F0F0F0;
    }
    .stButton>button {
        color: white;
        background-color: #4a148c;
        border-radius: 10px;
        height: 45px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #6a1b9a;
        border-color: #fff;
    }
    .sidebar .sidebar-content {
        background-color: #2c2c54;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------
st.sidebar.header("⚙️ Simulation Settings")

fair_price = st.sidebar.slider("Fair Price of Option", 10, 100, 40)
passive_bid = st.sidebar.slider("Algo Bid (Initial)", 10, 50, 20)
passive_ask = st.sidebar.slider("Algo Ask (Initial)", 60, 150, 100)
threshold_pct = st.sidebar.slider("Sell Trigger (% above fair)", 5, 100, 20)
num_humans = st.sidebar.slider("Number of Human Traders", 1, 5, 2)
steps = st.sidebar.slider("Simulation Steps", 10, 100, 30)
animation_speed = st.sidebar.slider("Animation Speed (ms per step)", 100, 2000, 500)
random_seed = st.sidebar.number_input("Random Seed", 0, 999, 42)
st.sidebar.markdown("---")
run_sim = st.sidebar.button("▶️ Run Simulation")

# -----------------------------------------------------------
# SIMULATION LOGIC
# -----------------------------------------------------------
def simulate_market(fair_price, passive_bid, passive_ask, threshold_pct, num_humans, steps, seed=42):
    np.random.seed(seed)
    data = []

    current_bid = passive_bid
    current_ask = passive_ask
    human_positions = [0] * num_humans
    human_cash = [10000.0] * num_humans
    algo_inventory = 0
    algo_cash = 0
    threshold_price = fair_price * (1 + threshold_pct / 100)

    for t in range(steps):
        event = f"Step {t}: Bid={current_bid:.2f}, Ask={current_ask:.2f}"
        # Human attempts to buy occasionally
        for i in range(num_humans):
            if np.random.rand() < 0.15:  # chance to place order
                order_price = current_bid + np.random.randint(1, 5)
                if order_price < threshold_price:
                    current_bid = order_price + 1
                    algo_inventory += 5
                    algo_cash -= current_bid * 5
                    event = f"Human {i+1} placed BUY @ {order_price}, Algo stepped to {current_bid}"
                else:
                    # Algo sells to human
                    sell_price = threshold_price
                    human_positions[i] += 5
                    human_cash[i] -= sell_price * 5
                    algo_inventory -= 5
                    algo_cash += sell_price * 5
                    current_bid, current_ask = passive_bid, passive_ask
                    event = f"Human {i+1} filled by Algo @ {sell_price:.2f}"

        # Random drift
        current_ask += np.random.uniform(-1, 2)
        current_bid = max(passive_bid, current_bid + np.random.uniform(-1, 1))
        current_ask = max(current_bid + 1, current_ask)

        data.append({
            "Time": t,
            "Bid": current_bid,
            "Ask": current_ask,
            "Mid": (current_bid + current_ask) / 2,
            "Event": event
        })

    df = pd.DataFrame(data)
    human_summary = pd.DataFrame({
        "Human": [f"Trader {i+1}" for i in range(num_humans)],
        "Position": human_positions,
        "Cash": human_cash,
        "MarkToFair": [p * fair_price for p in human_positions],
        "UnrealizedPnL": [p * fair_price - (10000 - cash) for p, cash in zip(human_positions, human_cash)]
    })

    algo_summary = {
        "Algo Inventory": algo_inventory,
        "Algo Cash": algo_cash,
        "Threshold Price": threshold_price
    }

    return df, human_summary, algo_summary

# -----------------------------------------------------------
# RUN SIMULATION
# -----------------------------------------------------------
if run_sim:
    df, human_summary, algo_summary = simulate_market(
        fair_price, passive_bid, passive_ask, threshold_pct, num_humans, steps, seed=random_seed
    )

    # -------------------------------------------------------
    # CHART
    # -------------------------------------------------------
    st.title("💹 Option Market Manipulation (Educational Simulation)")
    st.caption("Simulation of algorithmic quote manipulation in an illiquid option market.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Bid"], mode="lines+markers", name="Bid", line=dict(color="cyan")))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Ask"], mode="lines+markers", name="Ask", line=dict(color="magenta")))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Mid"], mode="lines", name="Mid", line=dict(color="yellow")))
    fig.add_hline(y=fair_price, line_dash="dot", annotation_text="Fair Price", annotation_position="bottom left")
    fig.add_hline(y=algo_summary["Threshold Price"], line_dash="dash", line_color="red", annotation_text="Threshold", annotation_position="top left")
    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Time Step",
        yaxis_title="Price",
        title="Simulated Market Quotes"
    )
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------
    # TABLES
    # -------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🧾 Market Events")
        st.dataframe(df[["Time", "Event"]].tail(15), height=350)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Simulation Log", csv, "simulation_log.csv", "text/csv")

    with col2:
        st.subheader("👨‍💻 Human Traders Summary")
        st.dataframe(human_summary.style.format({"Cash": "{:.2f}", "MarkToFair": "{:.2f}", "UnrealizedPnL": "{:.2f}"}))
        st.metric("Algo Inventory", algo_summary["Algo Inventory"])
        st.metric("Algo Cash", f"{algo_summary['Algo Cash']:.2f}")
        st.metric("Threshold Price", f"{algo_summary['Threshold Price']:.2f}")

    st.markdown("---")
    st.caption("Educational Visualization — Simulates market imbalance caused by algorithmic trading in non-liquid options.")
else:
    st.markdown("## 👇 Configure simulation in the sidebar and click **▶️ Run Simulation**")
    st.info("This app visually demonstrates how a manipulative algorithm can distort pricing in an illiquid option environment.")
