"""simple_route_planner.py
A minimal route planner that doesn't rely on external libraries.
This script generates a climbing route based on manually identified holds from the image.
"""

import os
import json
import random

def generate_predefined_route():
    """Generate a climbing route using manually identified holds from the image"""
    # Manually identified holds from the climbing wall image
    holds = [
        # Bottom blue holds
        {"id": 0, "x": 275, "y": 1050, "color": "blue"},
        {"id": 1, "x": 450, "y": 1050, "color": "blue"}, 
        
        # Middle green holds (from bottom to top)
        {"id": 2, "x": 400, "y": 900, "color": "green"},
        {"id": 3, "x": 500, "y": 850, "color": "green"},
        {"id": 4, "x": 425, "y": 750, "color": "green"},
        {"id": 5, "x": 475, "y": 650, "color": "green"},
        {"id": 6, "x": 375, "y": 600, "color": "green"},
        {"id": 7, "x": 450, "y": 500, "color": "green"},
        
        # Yellow holds (middle part)
        {"id": 8, "x": 540, "y": 450, "color": "yellow"},
        
        # Orange holds
        {"id": 9, "x": 475, "y": 350, "color": "orange"},
        
        # Red square at top
        {"id": 10, "x": 400, "y": 200, "color": "red"}
    ]
    
    # Define a logical route from bottom to top
    # We'll use the green sequence in the middle as the main path
    route_ids = [1, 2, 3, 4, 5, 6, 7, 8, 10]
    
    # Convert to route steps
    steps = []
    for idx, hold_id in enumerate(route_ids):
        hold = next(h for h in holds if h["id"] == hold_id)
        steps.append({
            "step": idx + 1,
            "x": hold["x"],
            "y": hold["y"],
            "color": hold["color"],
            "instruction": f"Step {idx+1}: move to {hold['color']} hold at (x={hold['x']}, y={hold['y']})"
        })
    
    return steps

def create_text_visualization(steps, width=80, height=40):
    """Create a simple text visualization of the route"""
    # Create a blank canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Place the holds and numbers
    for step in steps:
        # Scale coordinates to fit text canvas
        x = int(step["x"] * (width-1) / 800)
        y = int(step["y"] * (height-1) / 1200)
        
        # Ensure within bounds
        x = min(max(x, 0), width-1)
        y = min(max(y, 0), height-1)
        
        # Place the step number
        step_num = str(step["step"])
        if len(step_num) == 1:
            canvas[y][x] = step_num
        else:
            # For multi-digit numbers, just use #
            canvas[y][x] = '#'
    
    # Connect the holds with lines (very simple approach)
    for i in range(len(steps)-1):
        start_x = int(steps[i]["x"] * (width-1) / 800)
        start_y = int(steps[i]["y"] * (height-1) / 1200)
        end_x = int(steps[i+1]["x"] * (width-1) / 800)
        end_y = int(steps[i+1]["y"] * (height-1) / 1200)
        
        # Draw simple line
        steps_x = abs(end_x - start_x)
        steps_y = abs(end_y - start_y)
        steps_total = max(steps_x, steps_y)
        
        if steps_total > 0:
            for step in range(1, steps_total):
                x = start_x + int((end_x - start_x) * step / steps_total)
                y = start_y + int((end_y - start_y) * step / steps_total)
                
                # Don't overwrite hold numbers
                if canvas[y][x] == ' ':
                    canvas[y][x] = '·'
    
    # Convert to string
    visualization = ""
    for row in canvas:
        visualization += ''.join(row) + '\n'
    
    return visualization

if __name__ == "__main__":
    import sys
    
    # Get the output filename
    output_file = "route.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    # Generate route with predefined holds
    steps = generate_predefined_route()
    
    # Save to JSON
    with open(output_file, "w") as f:
        json.dump(steps, f, indent=2)
    
    print(f"Route with {len(steps)} moves saved to {output_file}")
    
    # Create and display text visualization
    vis = create_text_visualization(steps)
    print("\nRoute Visualization:")
    print(vis)
    
    # Print detailed instructions
    print("\nClimbing Route Instructions:")
    for step in steps:
        print(step["instruction"]) 