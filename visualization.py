import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_intersection(winner_lane, green_duration, lanes_data):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Draw roads
    road_width = 30
    center_c = 50
    half_w = road_width / 2

    # NS Road
    ax.add_patch(patches.Rectangle((center_c - half_w, 0), road_width, 100, color='#333333'))
    # EW Road
    ax.add_patch(patches.Rectangle((0, center_c - half_w), 100, road_width, color='#333333'))
    
    # Dashed lines
    ax.plot([50, 50], [0, 100], color='white', linestyle='--', dashes=(5, 5), zorder=2)
    ax.plot([0, 100], [50, 50], color='white', linestyle='--', dashes=(5, 5), zorder=2)
    
    # Highlight Center Box
    ax.add_patch(patches.Rectangle((center_c - half_w, center_c - half_w), road_width, road_width, color='#444444', zorder=1))

    # Determine colors
    colors = {
        'North': 'red', 'South': 'red', 'East': 'red', 'West': 'red'
    }
    if winner_lane:
        colors[winner_lane] = '#00FF00' # Bright Green

    # Draw Traffic Lights & Labels
    lights_pos = {
        'North': (40, 70, 'North'),
        'South': (60, 30, 'South'),
        'East': (70, 60, 'East'),
        'West': (30, 40, 'West')
    }

    for lane, (x, y, label) in lights_pos.items():
        # Traffic light housing
        ax.add_patch(patches.Circle((x, y), 3, color='black', zorder=3))
        # Light bulb
        ax.add_patch(patches.Circle((x, y), 2, color=colors[lane], zorder=4))
        
        # Label
        text_y = y + 5 if lane in ['North', 'East'] else y - 8
        ax.text(x, text_y, label, color='white', fontsize=12, ha='center', fontweight='bold',
               bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))
               
    # Draw Countdown Timer if there is a winner
    if winner_lane:
        ax.text(50, 50, f"{int(green_duration)}s", color='white', fontsize=18, 
                ha='center', va='center', fontweight='bold', zorder=5)

    # Draw vehicle density dots
    dot_positions = {
        'North': [(45, 80 + i*4) for i in range(5)],
        'South': [(55, 20 - i*4) for i in range(5)],
        'East':  [(80 + i*4, 45) for i in range(5)],
        'West':  [(20 - i*4, 55) for i in range(5)],
    }
    
    for lane, pts in dot_positions.items():
        density = lanes_data[lane]['density']
        cars_to_draw = int((density / 100.0) * 5) # Scale 0-100 to 0-5 dots
        for i in range(cars_to_draw):
            px, py = pts[i]
            # Emergency vehicles get blue/red flash indicator
            is_emergency = lanes_data[lane]['emergency'] == 1 and i == 0
            car_color = '#00CCFF' if is_emergency else '#FFDD00'
            ax.add_patch(patches.Circle((px, py), 1.5, color=car_color, zorder=3))

    fig.tight_layout()
    return fig
