import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def create_fuzzy_system():
    """
    Initializes the Mamdani Fuzzy Inference System for traffic control.
    Defines the Universes of Discourse (inputs/outputs), Membership Functions,
    and the Fuzzy Rule Base.
    
    Returns:
        ctrl.ControlSystemSimulation: The compiled executable fuzzy simulation environment.
    """
    # ==========================================
    # 1. Define Universes of Discourse
    # ==========================================
    # Inputs
    density = ctrl.Antecedent(np.arange(0, 101, 1), 'density')
    waiting_time = ctrl.Antecedent(np.arange(0, 121, 1), 'waiting_time')
    emergency = ctrl.Antecedent(np.arange(0, 2, 1), 'emergency') # Boolean: 0 (No) or 1 (Yes)

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

    # ==========================================
    # 3. Construct Fuzzy Rule Base (10 Rules)
    # ==========================================
    # Emergency Override
    rule1 = ctrl.Rule(emergency['yes'], [priority['very_high'], green_duration['long']])
    
    # High Density Scenarios
    rule2 = ctrl.Rule(density['high'] & waiting_time['long'] & emergency['no'], [priority['high'], green_duration['long']])
    rule3 = ctrl.Rule(density['high'] & waiting_time['moderate'] & emergency['no'], [priority['high'], green_duration['medium']])
    rule4 = ctrl.Rule(density['high'] & waiting_time['short'] & emergency['no'], [priority['medium'], green_duration['medium']])

    # Medium Density Scenarios
    rule5 = ctrl.Rule(density['medium'] & waiting_time['long'] & emergency['no'], [priority['medium'], green_duration['long']])
    rule6 = ctrl.Rule(density['medium'] & waiting_time['moderate'] & emergency['no'], [priority['medium'], green_duration['medium']])
    rule7 = ctrl.Rule(density['medium'] & waiting_time['short'] & emergency['no'], [priority['low'], green_duration['short']])

    # Low Density Scenarios
    rule8 = ctrl.Rule(density['low'] & waiting_time['long'] & emergency['no'], [priority['medium'], green_duration['medium']])
    rule9 = ctrl.Rule(density['low'] & waiting_time['moderate'] & emergency['no'], [priority['low'], green_duration['medium']])
    rule10 = ctrl.Rule(density['low'] & waiting_time['short'] & emergency['no'], [priority['low'], green_duration['short']])

    # Compile the Control System
    traffic_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10])
    return ctrl.ControlSystemSimulation(traffic_ctrl)

# Singleton instance
traffic_sim = create_fuzzy_system()

def evaluate_lane(veh_density, wait_time, is_emergency):
    """
    Passes crisp input variables into the Fuzzy Inference Engine to calculate outputs.
    
    Args:
        veh_density (int): The volume of cars in the lane (0-100).
        wait_time (int): Seconds the lane has been waiting at red (0-120).
        is_emergency (int): 1 if emergency vehicle is present, 0 otherwise.
        
    Returns:
        tuple: (calculated_priority_score, calculated_green_duration)
    """
    traffic_sim.input['density'] = veh_density
    traffic_sim.input['waiting_time'] = wait_time
    traffic_sim.input['emergency'] = is_emergency
    
    traffic_sim.compute()
    return traffic_sim.output['priority'], traffic_sim.output['green_duration']

def evaluate_intersection(lanes_data):
    """
    Evaluates all 4 lanes simultaneously and determines the absolute winner.
    Implements intelligent tie-breaking: If priorities are equal, the lane 
    with the longest wait time wins.
    
    Args:
        lanes_data (dict): Dictionary containing the state of all 4 lanes.
        
    Returns:
        tuple: (winning_lane_name, assigned_green_duration_in_seconds, full_results_dict)
    """
    results_dictionary = {}
    winner_lane = None
    max_priority = -1
    assigned_green = 0
    max_wait_time = -1
    
    # Iterate through North, South, East, West
    for lane_name, lane_state in lanes_data.items():
        # Extrapolate outputs via Fuzzy Engine
        calculated_priority, calculated_green = evaluate_lane(
            lane_state['density'], 
            lane_state['wait'], 
            lane_state['emergency']
        )
        
        # Store for dashboard charts
        results_dictionary[lane_name] = {
            'priority': calculated_priority, 
            'computed_green': calculated_green, 
            'data': lane_state
        }
        
        # 1. Standard win condition: highest priority strictly beats previous max
        if calculated_priority > max_priority + 0.01:
            max_priority = calculated_priority
            winner_lane = lane_name
            assigned_green = calculated_green
            max_wait_time = lane_state['wait']
            
        # 2. Tie-breaking condition: equal priorities, but this lane has waited longer
        elif abs(calculated_priority - max_priority) <= 0.01 and lane_state['wait'] > max_wait_time:
            max_priority = calculated_priority
            winner_lane = lane_name
            assigned_green = calculated_green
            max_wait_time = lane_state['wait']
            
    return winner_lane, assigned_green, results_dictionary

def compute_effectiveness(all_lanes_outcomes, winning_lane, green_duration_granted):
    """
    Calculates the 'Queue Clearance Efficiency' metric which proves why the
    Fuzzy system logically outperforms a static Round-Robin system.
    
    Formula: Cleared Vehicles * (Wait Time + Emergency Weight)
    
    Args:
        all_lanes_outcomes (dict): The output dictionary from evaluate_intersection.
        winning_lane (str): The name of the lane selected to go green.
        green_duration_granted (float): The amount of green time awarded.
        
    Returns:
        float: The calculated effectiveness score.
    """
    # Extract crisp data of the lane that was granted the green light
    lane_density = all_lanes_outcomes[winning_lane]['data']['density']
    lane_wait_time = all_lanes_outcomes[winning_lane]['data']['wait']
    has_emergency = all_lanes_outcomes[winning_lane]['data']['emergency']
    
    # Assume a throughput of 1 vehicle per second of green light
    cleared_cars = min(lane_density, green_duration_granted)
    
    # Give extreme mathematical weight to processing an emergency vehicle
    EMERGENCY_WEIGHT_MULTIPLIER = 1000
    effective_delay_relieved = lane_wait_time + (EMERGENCY_WEIGHT_MULTIPLIER if has_emergency else 0)
    
    return cleared_cars * effective_delay_relieved
