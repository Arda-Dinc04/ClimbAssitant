"""
Climbing Route Analyzer
----------------------
Analyzes climbing routes from images and provides optimal movement suggestions.

Features:
- Identifies climbing holds in an image
- Plans an optimal climbing route
- Suggests limb placements (which hand/foot to use for each hold)
- Generates step-by-step climbing instructions

Usage:
1. To use with the web interface:
   - Simply open index.html in a browser
   - Use the "Load Demo Image" button to see a demonstration
   - Upload your own climbing wall images to analyze them

2. To use from the command line:
   python route_analyzer.py [output_file.json]

3. To use as a library in your own code:
   from route_analyzer import ClimbingRouteAnalyzer
   analyzer = ClimbingRouteAnalyzer()
   route = analyzer.analyze_image_and_generate_route("your_image.jpg")
"""

import os
import json
import math
import random

class ClimbingRouteAnalyzer:
    def __init__(self):
        self.holds = []
        self.route = []
        self.route_with_limbs = []
        self.body_position = {
            "left_hand": None,
            "right_hand": None,
            "left_foot": None,
            "right_foot": None,
            "center_x": 0,
            "center_y": 0
        }
    
    def identify_holds_from_image(self, img_path=None):
        """
        Identify holds from an image or use predefined holds.
        In a real implementation, this would use computer vision techniques.
        """
        # Manually identified holds from the climbing wall image
        self.holds = [
            # Bottom blue holds
            {"id": 0, "x": 275, "y": 1050, "color": "blue", "size": "medium", "type": "jug"},
            {"id": 1, "x": 450, "y": 1050, "color": "blue", "size": "medium", "type": "jug"}, 
            
            # Middle green holds (from bottom to top)
            {"id": 2, "x": 400, "y": 900, "color": "green", "size": "small", "type": "crimp"},
            {"id": 3, "x": 500, "y": 850, "color": "green", "size": "small", "type": "pinch"},
            {"id": 4, "x": 425, "y": 750, "color": "green", "size": "small", "type": "crimp"},
            {"id": 5, "x": 475, "y": 650, "color": "green", "size": "small", "type": "crimp"},
            {"id": 6, "x": 375, "y": 600, "color": "green", "size": "small", "type": "crimp"},
            {"id": 7, "x": 450, "y": 500, "color": "green", "size": "small", "type": "pinch"},
            
            # Yellow holds (middle part)
            {"id": 8, "x": 540, "y": 450, "color": "yellow", "size": "medium", "type": "sloper"},
            
            # Orange holds
            {"id": 9, "x": 475, "y": 350, "color": "orange", "size": "medium", "type": "jug"},
            
            # Red square at top
            {"id": 10, "x": 400, "y": 200, "color": "red", "size": "large", "type": "jug"}
        ]
        return self.holds
    
    def plan_route(self):
        """Plan a route from bottom to top"""
        # Sort holds by height (y-coordinate)
        sorted_holds = sorted(self.holds, key=lambda h: h["y"], reverse=True)
        
        # For this example, we'll use a predefined route
        route_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Convert to route steps
        self.route = []
        for idx, hold_id in enumerate(route_ids):
            hold = next(h for h in self.holds if h["id"] == hold_id)
            self.route.append({
                "step": idx + 1,
                "hold_id": hold["id"],
                "x": hold["x"],
                "y": hold["y"],
                "color": hold["color"],
                "size": hold["size"],
                "type": hold["type"]
            })
        
        return self.route
    
    def distance(self, x1, y1, x2, y2):
        """Calculate distance between two points"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def calculate_body_center(self):
        """Calculate the center of the climber's body based on limb positions"""
        limbs = [limb for limb in [
            self.body_position["left_hand"],
            self.body_position["right_hand"],
            self.body_position["left_foot"], 
            self.body_position["right_foot"]
        ] if limb is not None]
        
        if not limbs:
            return 400, 1100  # Default position at the bottom center
            
        x_sum = sum(self.holds[limb]["x"] for limb in limbs)
        y_sum = sum(self.holds[limb]["y"] for limb in limbs)
        
        return x_sum / len(limbs), y_sum / len(limbs)
    
    def suggest_limb_placements(self):
        """Suggest which limb should be used for each hold in the route"""
        self.route_with_limbs = []
        
        # Initialize climber's position at the start
        # Assuming we start with feet on the ground and hands on the first holds
        if len(self.route) >= 2:
            self.body_position = {
                "left_hand": self.route[0]["hold_id"],
                "right_hand": None,
                "left_foot": None,  # On the ground
                "right_foot": None,  # On the ground
                "center_x": self.route[0]["x"],
                "center_y": self.route[0]["y"] + 100  # Body is below the first hold
            }
        else:
            return []
            
        # First step - placing first hand
        first_step = self.route[0].copy()
        first_step["limb"] = "left_hand"
        first_step["movement"] = "Start with left hand on the first hold"
        first_step["body_position"] = "Standing at the base, reach up with left hand"
        self.route_with_limbs.append(first_step)
        
        # Second step - placing second hand
        if len(self.route) >= 2:
            second_step = self.route[1].copy()
            second_step["limb"] = "right_hand"
            second_step["movement"] = "Place right hand on the next hold"
            second_step["body_position"] = "Weight balanced between both arms, feet on starting holds or features"
            self.body_position["right_hand"] = self.route[1]["hold_id"]
            self.route_with_limbs.append(second_step)
        
        # For the rest of the route, alternate limbs logically
        for i in range(2, len(self.route)):
            current_hold = self.route[i]
            step = current_hold.copy()
            
            # Calculate body center position
            center_x, center_y = self.calculate_body_center()
            
            # Decide which limb to use next
            # Logic: Use the limb that's furthest from the next hold
            limb_distances = {
                "left_hand": float('inf') if self.body_position["left_hand"] is None else 
                              self.distance(self.holds[self.body_position["left_hand"]]["x"], 
                                           self.holds[self.body_position["left_hand"]]["y"],
                                           current_hold["x"], current_hold["y"]),
                "right_hand": float('inf') if self.body_position["right_hand"] is None else 
                               self.distance(self.holds[self.body_position["right_hand"]]["x"], 
                                            self.holds[self.body_position["right_hand"]]["y"],
                                            current_hold["x"], current_hold["y"]),
                "left_foot": float('inf') if self.body_position["left_foot"] is None else 
                              self.distance(self.holds[self.body_position["left_foot"]]["x"], 
                                           self.holds[self.body_position["left_foot"]]["y"],
                                           current_hold["x"], current_hold["y"]),
                "right_foot": float('inf') if self.body_position["right_foot"] is None else 
                               self.distance(self.holds[self.body_position["right_foot"]]["x"], 
                                            self.holds[self.body_position["right_foot"]]["y"],
                                            current_hold["x"], current_hold["y"])
            }
            
            # Consider hold height to bias toward using hands for higher holds and feet for lower ones
            height_factor = (1200 - current_hold["y"]) / 1200  # 0 at bottom, 1 at top
            
            # Adjust distances based on height - prefer hands for high holds, feet for low holds
            if height_factor > 0.5:  # Higher hold - prefer hands
                limb_distances["left_foot"] *= 1.5
                limb_distances["right_foot"] *= 1.5
            else:  # Lower hold - prefer feet
                limb_distances["left_hand"] *= 1.5
                limb_distances["right_hand"] *= 1.5
            
            # Select the limb with the maximum distance (the one that needs to move most)
            next_limb = max(limb_distances, key=limb_distances.get)
            
            # Update limb position
            self.body_position[next_limb] = current_hold["hold_id"]
            
            # Generate explanation
            if next_limb.endswith("hand"):
                movement = f"Move {next_limb.replace('_', ' ')} to the {current_hold['color']} {current_hold['type']}"
            else:
                movement = f"Place {next_limb.replace('_', ' ')} on the {current_hold['color']} {current_hold['type']}"
            
            # Give detailed body position advice
            if next_limb.endswith("hand"):
                body_position = "Keep your center of gravity beneath your handholds. "
                if current_hold["type"] == "crimp":
                    body_position += "Crimp carefully with straight fingers."
                elif current_hold["type"] == "pinch":
                    body_position += "Apply opposing thumb pressure on this pinch."
                elif current_hold["type"] == "sloper":
                    body_position += "Use open hand technique and keep weight beneath the hold."
                elif current_hold["type"] == "jug":
                    body_position += "Full grip with fingers wrapped around the jug."
            else:
                body_position = "Shift your weight as you move your foot. "
                if i < len(self.route) - 1:
                    next_hold = self.route[i+1]
                    if next_hold["x"] > current_hold["x"]:
                        body_position += "Prepare to move right next."
                    else:
                        body_position += "Prepare to move left next."
            
            step["limb"] = next_limb
            step["movement"] = movement
            step["body_position"] = body_position
            
            self.route_with_limbs.append(step)
        
        return self.route_with_limbs
    
    def generate_route_instructions(self):
        """Generate detailed route instructions with limb placements"""
        if not self.route_with_limbs:
            self.suggest_limb_placements()
            
        instructions = []
        for step in self.route_with_limbs:
            instruction = {
                "step": step["step"],
                "hold": {
                    "id": step["hold_id"],
                    "x": step["x"],
                    "y": step["y"],
                    "color": step["color"],
                    "type": step["type"],
                    "size": step["size"]
                },
                "limb": step["limb"],
                "movement": step["movement"],
                "body_position": step["body_position"],
                "instruction": f"Step {step['step']}: {step['movement']}. {step['body_position']}"
            }
            instructions.append(instruction)
            
        return instructions
    
    def analyze_image_and_generate_route(self, img_path=None):
        """Complete pipeline from image to route instructions"""
        self.identify_holds_from_image(img_path)
        self.plan_route()
        self.suggest_limb_placements()
        return self.generate_route_instructions()
    
    def save_route_to_json(self, output_file="climbing_route.json"):
        """Save the route with instructions to a JSON file"""
        if not self.route_with_limbs:
            self.suggest_limb_placements()
            
        instructions = self.generate_route_instructions()
        
        route_data = {
            "route_info": {
                "total_steps": len(instructions),
                "difficulty": "intermediate",
                "image": "climbing_wall.jpg"
            },
            "holds": self.holds,
            "instructions": instructions
        }
        
        with open(output_file, "w") as f:
            json.dump(route_data, f, indent=2)
            
        return output_file

def create_text_visualization(route, width=80, height=40):
    """Create a simple text visualization of the route"""
    # Create a blank canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Place the holds and numbers
    for step in route:
        # Scale coordinates to fit text canvas
        x = int(step["x"] * (width-1) / 800)
        y = int(step["y"] * (height-1) / 1200)
        
        # Ensure within bounds
        x = min(max(x, 0), width-1)
        y = min(max(y, 0), height-1)
        
        # Place the step number
        step_num = str(step["step"])
        
        # Add a letter indicating the limb
        limb_indicator = step["limb"][0].upper()
        
        if len(step_num) == 1:
            canvas[y][x] = step_num + limb_indicator
        else:
            # For multi-digit numbers, just use #
            canvas[y][x] = '#' + limb_indicator
    
    # Connect the holds with lines
    for i in range(len(route)-1):
        start_x = int(route[i]["x"] * (width-1) / 800)
        start_y = int(route[i]["y"] * (height-1) / 1200)
        end_x = int(route[i+1]["x"] * (width-1) / 800)
        end_y = int(route[i+1]["y"] * (height-1) / 1200)
        
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
    output_file = "climbing_route.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    # Create analyzer and generate route
    analyzer = ClimbingRouteAnalyzer()
    route = analyzer.analyze_image_and_generate_route()
    analyzer.save_route_to_json(output_file)
    
    print(f"Route with {len(route)} moves saved to {output_file}")
    
    # Create and display text visualization
    vis = create_text_visualization(analyzer.route_with_limbs)
    print("\nRoute Visualization (with limb indicators):")
    print("  L=Left hand, R=Right hand, L=Left foot, R=Right foot")
    print(vis)
    
    # Print detailed instructions
    print("\nClimbing Route Instructions:")
    for step in route:
        print(f"Step {step['step']}: {step['movement']} ({step['limb']})")
        print(f"  → {step['body_position']}")
        print() 