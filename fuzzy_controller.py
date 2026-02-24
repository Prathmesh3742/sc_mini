import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def create_fuzzy_system():
    # Inputs
    density = ctrl.Antecedent(np.arange(0, 101, 1), 'density')
    waiting_time = ctrl.Antecedent(np.arange(0, 121, 1), 'waiting_time')
    emergency = ctrl.Antecedent(np.arange(0, 2, 1), 'emergency') # 0 or 1

    # Outputs
    priority = ctrl.Consequent(np.arange(0, 101, 1), 'priority')
    green_duration = ctrl.Consequent(np.arange(10, 91, 1), 'green_duration')

    # Membership Functions
    density['low'] = fuzz.trapmf(density.universe, [0, 0, 15, 30])
    density['medium'] = fuzz.trapmf(density.universe, [20, 35, 55, 70])
    density['high'] = fuzz.trapmf(density.universe, [60, 75, 100, 100])

    waiting_time['short'] = fuzz.trapmf(waiting_time.universe, [0, 0, 20, 40])
    waiting_time['moderate'] = fuzz.trapmf(waiting_time.universe, [30, 45, 65, 80])
    waiting_time['long'] = fuzz.trapmf(waiting_time.universe, [70, 85, 120, 120])

    emergency['no'] = fuzz.trimf(emergency.universe, [0, 0, 0.5])
    emergency['yes'] = fuzz.trimf(emergency.universe, [0.5, 1, 1])

    priority['low'] = fuzz.trapmf(priority.universe, [0, 0, 20, 40])
    priority['medium'] = fuzz.trapmf(priority.universe, [30, 45, 55, 70])
    priority['high'] = fuzz.trapmf(priority.universe, [60, 75, 85, 90])
    priority['very_high'] = fuzz.trapmf(priority.universe, [85, 90, 100, 100])

    green_duration['short'] = fuzz.trapmf(green_duration.universe, [10, 10, 20, 30])
    green_duration['medium'] = fuzz.trapmf(green_duration.universe, [25, 35, 45, 60])
    green_duration['long'] = fuzz.trapmf(green_duration.universe, [50, 65, 90, 90])

    # Rules
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
    return ctrl.ControlSystemSimulation(traffic_ctrl)

# Singleton instance
traffic_sim = create_fuzzy_system()

def evaluate_lane(d, w, e):
    traffic_sim.input['density'] = d
    traffic_sim.input['waiting_time'] = w
    traffic_sim.input['emergency'] = e
    traffic_sim.compute()
    return traffic_sim.output['priority'], traffic_sim.output['green_duration']

def evaluate_intersection(lanes_data):
    results = {}
    winner_lane = None
    max_priority = -1
    assigned_green = 0
    max_wait = -1
    
    for lane, data in lanes_data.items():
        p, g = evaluate_lane(data['density'], data['wait'], data['emergency'])
        results[lane] = {'priority': p, 'computed_green': g, 'data': data}
        
        # Tie-breaking logic: higher wait time wins
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
            
    return winner_lane, assigned_green, results

def compute_effectiveness(lanes_details, win_lane, green_time):
    d = lanes_details[win_lane]['data']['density']
    w = lanes_details[win_lane]['data']['wait']
    e = lanes_details[win_lane]['data']['emergency']
    
    cleared_cars = min(d, green_time)
    EMERGENCY_WEIGHT = 1000
    effective_wait = w + (EMERGENCY_WEIGHT if e else 0)
    
    return cleared_cars * effective_wait
