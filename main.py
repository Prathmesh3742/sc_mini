import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import pandas as pd
import os

# Create output directories for plots if needed
os.makedirs("plots", exist_ok=True)

# ==========================================
# 1. Define Universe of Discourse & Variables
# ==========================================
# Inputs
density = ctrl.Antecedent(np.arange(0, 101, 1), 'density')
waiting_time = ctrl.Antecedent(np.arange(0, 121, 1), 'waiting_time')
emergency = ctrl.Antecedent(np.arange(0, 2, 1), 'emergency') # 0 or 1

# Outputs
priority = ctrl.Consequent(np.arange(0, 101, 1), 'priority')
green_duration = ctrl.Consequent(np.arange(10, 91, 1), 'green_duration')

# ==========================================
# 2. Design Membership Functions
# ==========================================
# Vehicle Density
density['low'] = fuzz.trapmf(density.universe, [0, 0, 15, 30])
density['medium'] = fuzz.trapmf(density.universe, [20, 35, 55, 70])
density['high'] = fuzz.trapmf(density.universe, [60, 75, 100, 100])

# Waiting Time
waiting_time['short'] = fuzz.trapmf(waiting_time.universe, [0, 0, 20, 40])
waiting_time['moderate'] = fuzz.trapmf(waiting_time.universe, [30, 45, 65, 80])
waiting_time['long'] = fuzz.trapmf(waiting_time.universe, [70, 85, 120, 120])

# Emergency Vehicle
emergency['no'] = fuzz.trimf(emergency.universe, [0, 0, 0.5])
emergency['yes'] = fuzz.trimf(emergency.universe, [0.5, 1, 1])

# Priority
priority['low'] = fuzz.trapmf(priority.universe, [0, 0, 20, 40])
priority['medium'] = fuzz.trapmf(priority.universe, [30, 45, 55, 70])
priority['high'] = fuzz.trapmf(priority.universe, [60, 75, 85, 90])
priority['very_high'] = fuzz.trapmf(priority.universe, [85, 90, 100, 100])

# Green Duration
green_duration['short'] = fuzz.trapmf(green_duration.universe, [10, 10, 20, 30])
green_duration['medium'] = fuzz.trapmf(green_duration.universe, [25, 35, 45, 60])
green_duration['long'] = fuzz.trapmf(green_duration.universe, [50, 65, 90, 90])

# ==========================================
# 3. Plot Membership Functions
# ==========================================
def plot_mfs():
    fig, (ax0, ax1, ax2, ax3, ax4) = plt.subplots(nrows=5, figsize=(8, 15))
    
    ax0.plot(density.universe, fuzz.trapmf(density.universe, [0, 0, 15, 30]), 'b', linewidth=1.5, label='Low')
    ax0.plot(density.universe, fuzz.trapmf(density.universe, [20, 35, 55, 70]), 'g', linewidth=1.5, label='Medium')
    ax0.plot(density.universe, fuzz.trapmf(density.universe, [60, 75, 100, 100]), 'r', linewidth=1.5, label='High')
    ax0.set_title('Vehicle Density')
    ax0.legend()

    ax1.plot(waiting_time.universe, fuzz.trapmf(waiting_time.universe, [0, 0, 20, 40]), 'b', linewidth=1.5, label='Short')
    ax1.plot(waiting_time.universe, fuzz.trapmf(waiting_time.universe, [30, 45, 65, 80]), 'g', linewidth=1.5, label='Moderate')
    ax1.plot(waiting_time.universe, fuzz.trapmf(waiting_time.universe, [70, 85, 120, 120]), 'r', linewidth=1.5, label='Long')
    ax1.set_title('Waiting Time')
    ax1.legend()

    ax2.plot(emergency.universe, fuzz.trimf(emergency.universe, [0, 0, 0.5]), 'b', linewidth=1.5, label='No')
    ax2.plot(emergency.universe, fuzz.trimf(emergency.universe, [0.5, 1, 1]), 'r', linewidth=1.5, label='Yes')
    ax2.set_title('Emergency')
    ax2.set_xticks([0, 1])
    ax2.legend()
    
    ax3.plot(priority.universe, fuzz.trapmf(priority.universe, [0, 0, 20, 40]), 'b', linewidth=1.5, label='Low')
    ax3.plot(priority.universe, fuzz.trapmf(priority.universe, [30, 45, 55, 70]), 'g', linewidth=1.5, label='Medium')
    ax3.plot(priority.universe, fuzz.trapmf(priority.universe, [60, 75, 85, 90]), 'r', linewidth=1.5, label='High')
    ax3.plot(priority.universe, fuzz.trapmf(priority.universe, [85, 90, 100, 100]), 'purple', linewidth=1.5, label='Very High')
    ax3.set_title('Priority')
    ax3.legend()

    ax4.plot(green_duration.universe, fuzz.trapmf(green_duration.universe, [10, 10, 20, 30]), 'b', linewidth=1.5, label='Short')
    ax4.plot(green_duration.universe, fuzz.trapmf(green_duration.universe, [25, 35, 45, 60]), 'g', linewidth=1.5, label='Medium')
    ax4.plot(green_duration.universe, fuzz.trapmf(green_duration.universe, [50, 65, 90, 90]), 'r', linewidth=1.5, label='Long')
    ax4.set_title('Green Duration')
    ax4.legend()

    plt.tight_layout()
    plt.savefig('plots/membership_functions.png')
    plt.close()

plot_mfs()

# ==========================================
# 4. Construct Fuzzy Rule Base
# ==========================================
rule1 = ctrl.Rule(emergency['yes'], [priority['very_high'], green_duration['long']])
rule2 = ctrl.Rule(density['high'] & waiting_time['long'] & emergency['no'], [priority['high'], green_duration['long']])
rule3 = ctrl.Rule(density['high'] & waiting_time['moderate'] & emergency['no'], [priority['high'], green_duration['medium']])
rule4 = ctrl.Rule(density['high'] & waiting_time['short'] & emergency['no'], [priority['medium'], green_duration['medium']])

rule5 = ctrl.Rule(density['medium'] & waiting_time['long'] & emergency['no'], [priority['medium'], green_duration['long']])
rule6 = ctrl.Rule(density['medium'] & waiting_time['moderate'] & emergency['no'], [priority['medium'], green_duration['medium']])
rule7 = ctrl.Rule(density['medium'] & waiting_time['short'] & emergency['no'], [priority['low'], green_duration['short']])

rule8 = ctrl.Rule(density['low'] & waiting_time['long'] & emergency['no'], [priority['medium'], green_duration['medium']])
rule9 = ctrl.Rule(density['low'] & waiting_time['moderate'] & emergency['no'], [priority['low'], green_duration['medium']])
rule10 = ctrl.Rule(density['low'] & waiting_time['short'] & emergency['no'], [priority['low'], green_duration['short']])

traffic_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10])
traffic_sim = ctrl.ControlSystemSimulation(traffic_ctrl)

# ==========================================
# 5. Inference Process Definition
# ==========================================
def evaluate_lane(d, w, e):
    traffic_sim.input['density'] = d
    traffic_sim.input['waiting_time'] = w
    traffic_sim.input['emergency'] = e
    traffic_sim.compute()
    return traffic_sim.output['priority'], traffic_sim.output['green_duration']

# ==========================================
# 6. Surface Plot Visualization
# ==========================================
def plot_surface():
    x, y = np.meshgrid(np.linspace(0, 100, 30), np.linspace(0, 120, 30))
    z = np.zeros_like(x)

    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            # evaluate without emergency
            _, z[i, j] = evaluate_lane(x[i, j], y[i, j], 0)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap='viridis', linewidth=0.4, antialiased=True)
    ax.set_xlabel('Vehicle Density')
    ax.set_ylabel('Waiting Time')
    ax.set_zlabel('Green Duration (s)')
    ax.set_title('Surface Plot: Density & Waiting Time -> Green Duration')
    plt.savefig('plots/surface_plot.png')
    plt.close()

plot_surface()

# ==========================================
# 7. Multi-Lane Decision Logic & Scenarios
# ==========================================
def simulate_intersection(scenario_name, lanes_data):
    print(f"--- Scenario: {scenario_name} ---")
    results = {}
    winner_lane = None
    max_priority = -1
    assigned_green = 0
    max_wait = -1
    
    for lane, data in lanes_data.items():
        p, g = evaluate_lane(data['density'], data['wait'], data['emergency'])
        results[lane] = {'priority': p, 'computed_green': g, 'data': data}
        print(f"  {lane} -> Input(D:{data['density']}, W:{data['wait']}, E:{data['emergency']}) => Priority: {p:.2f}, Computed Green: {g:.2f}s")
        
        # Tie-breaking logic: higher wait time wins if priorities are roughly equal
        if p > max_priority + 0.01:
            max_priority = p
            winner_lane = lane
            assigned_green = g
            max_wait = data['wait']
        elif abs(p - max_priority) <= 0.01 and data['wait'] > max_wait:
            max_priority = p
            winner_lane = lane
            assigned_green = g
            max_wait = data['wait']
            
    print(f"  [RESULT] {winner_lane} gets priority with Green Duration = {assigned_green:.2f}s. Others remain red.\n")
    return winner_lane, assigned_green, results

scenarios = [
    {
        "name": "Case 1: North Heavy Traffic",
        "lanes": {
            "North": {"density": 85, "wait": 90, "emergency": 0},
            "South": {"density": 45, "wait": 50, "emergency": 0},
            "East": {"density": 10, "wait": 10, "emergency": 0},
            "West": {"density": 5, "wait": 5, "emergency": 0}
        }
    },
    {
        "name": "Case 2: West Emergency",
        "lanes": {
            "North": {"density": 85, "wait": 90, "emergency": 0},
            "South": {"density": 45, "wait": 50, "emergency": 0},
            "East": {"density": 10, "wait": 10, "emergency": 0},
            "West": {"density": 5, "wait": 5, "emergency": 1}
        }
    },
    {
        "name": "Case 3: All Lanes Balanced",
        "lanes": {
            "North": {"density": 50, "wait": 50, "emergency": 0},
            "South": {"density": 50, "wait": 52, "emergency": 0},
            "East": {"density": 48, "wait": 50, "emergency": 0},
            "West": {"density": 51, "wait": 50, "emergency": 0}
        }
    },
    {
        "name": "Case 4: Long Wait despite Low Density",
        "lanes": {
            "North": {"density": 15, "wait": 110, "emergency": 0},
            "South": {"density": 30, "wait": 20, "emergency": 0},
            "East": {"density": 40, "wait": 30, "emergency": 0},
            "West": {"density": 35, "wait": 25, "emergency": 0}
        }
    },
    {
        "name": "Case 5: High Density vs High Density with Emergency",
        "lanes": {
            "North": {"density": 95, "wait": 100, "emergency": 0},
            "South": {"density": 90, "wait": 110, "emergency": 1},
            "East": {"density": 50, "wait": 40, "emergency": 0},
            "West": {"density": 50, "wait": 40, "emergency": 0}
        }
    },
    {
        "name": "Case 6: Very Low Traffic",
        "lanes": {
            "North": {"density": 5, "wait": 5, "emergency": 0},
            "South": {"density": 10, "wait": 5, "emergency": 0},
            "East": {"density": 5, "wait": 10, "emergency": 0},
            "West": {"density": 5, "wait": 5, "emergency": 0}
        }
    }
]

scenario_results = []
for s in scenarios:
    w, g, r = simulate_intersection(s['name'], s['lanes'])
    scenario_results.append({'Scenario': s['name'], 'Winner': w, 'Green_Duration': g, 'Details': r})

# ==========================================
# 8. Performance Comparison (Fixed vs Fuzzy)
# ==========================================
# Assumption for Delay calculation:
# Fixed System: everyone gets 30s. If a lane needs more (density is high), the cars have to wait multiple cycles.
# For simplicity, let's track "Unserved Density Impact": Green time handles ~1 unit of density per second.
# Wait time for other lanes = assigned green to the winner.

comparison_data = []

# Fixed signal round-robin: N -> S -> E -> W, 30s each
fixed_green = 30

for i, s in enumerate(scenario_results):
    details = s['Details']
    winner = s['Winner']
    fuzzy_green = s['Green_Duration']
    
    # Better System Penalty Metric: Total System Remaining Vehicle-Seconds of Wait
    # Every missing second of green for a waiting car increases penalty.
    # Green light clears ~1 unit of density per second.
    def compute_system_penalty(lanes_details, win_lane, green_time):
        penalty = 0
        for lname, d_opts in lanes_details.items():
            d = d_opts['data']['density']
            w = d_opts['data']['wait']
            if lname == win_lane:
                rem_d = max(0, d - green_time) # cars left waiting
                penalty += rem_d * (w + green_time)
            else:
                penalty += d * (w + green_time) # all cars keep waiting
        return penalty
        
    fixed_winner = 'North'
    fixed_penalty = compute_system_penalty(details, fixed_winner, fixed_green)
    fuzzy_penalty = compute_system_penalty(details, winner, fuzzy_green)
            
    comparison_data.append({
        'Scenario': s['Scenario'].split(':')[0],
        'Fixed_Winner': fixed_winner,
        'Fixed_Green': 30,
        'Fixed_System_Penalty': round(fixed_penalty, 2),
        'Fuzzy_Winner': winner,
        'Fuzzy_Green': round(fuzzy_green, 2),
        'Fuzzy_System_Penalty': round(fuzzy_penalty, 2)
    })

df_comparison = pd.DataFrame(comparison_data)
print("=== Performance Comparison ===")
print(df_comparison.to_markdown(index=False))

# Visualization of Priority Comparison Chart (Case 1)
def plot_priority_comparison(details, scenario_name, index):
    lanes = list(details.keys())
    priorities = [details[l]['priority'] for l in lanes]
    
    plt.figure(figsize=(8, 5))
    plt.bar(lanes, priorities, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    plt.xlabel('Lanes')
    plt.ylabel('Priority Score')
    plt.title(f'Priority Scores - {scenario_name}')
    plt.ylim(0, 100)
    
    plt.savefig(f'plots/priority_comparison_{index}.png')
    plt.close()

# Plot priorities for all scenarios
for i, s in enumerate(scenario_results):
    plot_priority_comparison(s['Details'], s['Scenario'], i+1)

print("\nSimulation complete. All plots saved to 'plots/' directory.")
