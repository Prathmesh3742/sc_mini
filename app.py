import streamlit as st
import pandas as pd
import time
from fuzzy_controller import evaluate_intersection, compute_effectiveness
from visualization import draw_intersection
import matplotlib.pyplot as plt

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Smart Traffic Control", layout="wide", page_icon="🚦")
st.title("🚦 Fuzzy Logic Smart Traffic Controller")
st.markdown("Interactive 4-Way Junction Simulator with Emergency Override and Live Priority Metrics.")

# ==========================================
# SIDEBAR: 12 Interactive Inputs
# ==========================================
st.sidebar.header("🎛️ Intersection Controls")
st.sidebar.markdown("Adjust the real-time traffic volume and wait times to see how the Fuzzy Engine reacts.")

# State dictionary to hold all 4 lanes
lanes_data = {"North": {}, "South": {}, "East": {}, "West": {}}

# Programmatically generate sliders for all 4 lanes
for lane in lanes_data.keys():
    st.sidebar.subheader(f"{lane} Lane")
    density_val = st.sidebar.slider(f"{lane} Density", 0, 100, 50, key=f"{lane}_d", help="Number of cars in the queue.")
    wait_val = st.sidebar.slider(f"{lane} Waiting Time (s)", 0, 120, 30, key=f"{lane}_w", help="Seconds the first car has been waiting.")
    emerg_val = st.sidebar.checkbox(f"{lane} Emergency Vehicle", key=f"{lane}_e", help="Forces maximum priority override.")
    
    # Store user selections into the central dict
    lanes_data[lane] = {
        'density': density_val,
        'wait': wait_val,
        'emergency': 1 if emerg_val else 0
    }
    st.sidebar.markdown("---")

# ==========================================
# FUZZY INFERENCE LOGIC (Live Calculation)
# ==========================================
# Triggers instantly on any slider change
winner, duration, results = evaluate_intersection(lanes_data)

# ==========================================
# MAIN DASHBOARD LAYOUT
# ==========================================
col1, col2 = st.columns([1.5, 1])

# Left Column: Visualization & Animation
with col1:
    st.subheader("Live Intersection Visualization")
    
    # Placeholder for live animation frame
    viz_placeholder = st.empty()
    
    # Draw initial static frame
    fig = draw_intersection(winner, duration, lanes_data)
    viz_placeholder.pyplot(fig)
    plt.close(fig)
    
    # Animation Trigger
    if st.button(f"Animate Green Light ({winner})", help="Watch the logic process vehicles in real-time"):
        sim_lanes = dict(lanes_data) # Shallow copy data to mutate visually
        total_time = int(duration)
        
        # We simulate cars clearing the intersection at roughly 1 density unit per second
        density_drain_rate = sim_lanes[winner]['density'] / max(total_time, 1)
        
        for t in range(total_time, -1, -1):
            # Drain density visually
            if sim_lanes[winner]['density'] > 0:
                sim_lanes[winner]['density'] -= density_drain_rate
                
            sim_fig = draw_intersection(winner, t, sim_lanes)
            viz_placeholder.pyplot(sim_fig)
            plt.close(sim_fig)
            # Sleep slightly for animation effect
            time.sleep(0.05)
            
        st.success(f"{winner} lane cleared successfully!")

# Right Column: Metrics & Charts
with col2:
    st.subheader("Current Priority Scores")
    
    # Bar Chart Rendering
    priorities = {l: results[l]['priority'] for l in results}
    df_p = pd.DataFrame(priorities.values(), index=priorities.keys(), columns=['Priority Score'])
    st.bar_chart(df_p, color="#ff4b4b")
    
    st.markdown(f"**Winner:** `{winner}` is granted `{duration:.1f}s` of Green.")
    
    if any(l['emergency'] == 1 for l in lanes_data.values()):
        st.warning("⚠️ **Emergency Override Active!** Tie-breaking & Priority weights heavily altered.")
        
    # Fixed vs Fuzzy Comparison
    st.subheader("Performance Comparison (Instant)")
    st.markdown("Comparing current state vs a 30s Static cycle:")
    
    fixed_winner = 'North'
    fixed_green = 30
    
    fixed_eff = compute_effectiveness(results, fixed_winner, fixed_green)
    fuzzy_eff = compute_effectiveness(results, winner, duration)
    
    comp_df = pd.DataFrame([
        {"System": "Static Signal", "Winner": fixed_winner, "Green": 30.0, "Queue Clearance Efficiency": int(fixed_eff)},
        {"System": "Fuzzy Logic", "Winner": winner, "Green": round(duration, 1), "Queue Clearance Efficiency": int(fuzzy_eff)}
    ])
    
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    
    st.caption("*Queue Clearance Efficiency = Vehicles Cleared × (Wait Time + Emergency Weight)*")
    st.caption("*Higher efficiency indicates smarter routing of the heaviest delays.*")
