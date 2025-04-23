"""route_planner_backend.py
A minimal offline backend prototype that
1. Detects climbing holds in an image using color-based detection.
2. Converts detected holds into a graph.
3. Finds an "optimal" route (bottom‑up shortest path) with simple heuristics.
4. Outputs ordered step instructions that the React front‑end can display.

Requirements (install via pip):
    pip install opencv-python networkx numpy

Assumptions:
- Camera perspective is roughly front‑on (no strong skew).
- Route criteria is: minimise total vertical distance + slight penalty for big
  horizontal moves.  Edit WEIGHT_HORIZ to change that.
"""

import os
import cv2
import numpy as np
import networkx as nx

# ---------------- Configuration ----------------
WEIGHT_HORIZ = 1.2    # cost multiplier for horizontal moves (>1 penalises lateral dynos)

# ---------------- Core Functions ---------------

def color_based_hold_detection(img_path):
    """Detect holds based on color"""
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Could not read image at {img_path}")
    
    height, width, _ = img.shape
    holds = []
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for different holds (green, blue, orange, yellow, red)
    color_ranges = [
        # Green holds
        (np.array([35, 50, 50]), np.array([85, 255, 255])),
        # Blue holds
        (np.array([90, 50, 50]), np.array([130, 255, 255])),
        # Orange/yellow holds
        (np.array([10, 50, 50]), np.array([30, 255, 255])),
        # Red holds (wraps around hue space)
        (np.array([0, 50, 50]), np.array([10, 255, 255])),
        (np.array([160, 50, 50]), np.array([180, 255, 255]))
    ]
    
    hold_id = 0
    for lower, upper in color_ranges:
        # Create mask and find contours
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                x_c = x + w/2
                y_c = y + h/2
                holds.append({"id": hold_id, "x": float(x_c), "y": float(y_c), "w": float(w), "h": float(h)})
                hold_id += 1
    
    print(f"Detected {len(holds)} holds using color detection")
    return holds


def build_hold_graph(holds):
    """Create a graph where each hold is a node; edges weighted by cost of moving."""
    G = nx.DiGraph()
    # Sort by vertical position (top of image is y=0)
    holds_sorted = sorted(holds, key=lambda h: h["y"], reverse=False)  # top‑down

    for h in holds_sorted:
        G.add_node(h["id"], **h)

    for i, src in enumerate(holds_sorted):
        for j, dst in enumerate(holds_sorted):
            if dst["y"] > src["y"]:  # only connect upward moves
                dx = abs(dst["x"] - src["x"])
                dy = abs(dst["y"] - src["y"])
                cost = dy + WEIGHT_HORIZ * dx
                G.add_edge(src["id"], dst["id"], weight=cost)
    return G


def find_optimal_route(G):
    """Return list of hold ids representing cheapest path from lowest to highest hold."""
    # source nodes ~ bottom 20% of image; target nodes ~ top 20%
    ys = np.array([d["y"] for _, d in G.nodes(data=True)])
    y_max, y_min = ys.max(), ys.min()

    low_ids = [n for n, d in G.nodes(data=True) if d["y"] >= y_max - 0.2 * (y_max - y_min)]
    top_ids = [n for n, d in G.nodes(data=True) if d["y"] <= y_min + 0.2 * (y_max - y_min)]

    best_cost = np.inf
    best_path = None

    for s in low_ids:
        for t in top_ids:
            try:
                path = nx.shortest_path(G, s, t, weight="weight")
                cost = nx.path_weight(G, path, weight="weight")
                if cost < best_cost:
                    best_cost = cost
                    best_path = path
            except nx.NetworkXNoPath:
                continue
    return best_path or []


def route_to_steps(route, G):
    """Convert list of node ids to human‑readable steps with coordinates."""
    steps = []
    for idx, node_id in enumerate(route):
        data = G.nodes[node_id]
        steps.append(
            {
                "step": idx + 1,
                "x": int(data["x"]),
                "y": int(data["y"]),
                "instruction": f"Step {idx+1}: move to hold at (x={int(data['x'])}, y={int(data['y'])})",
            }
        )
    return steps

def visualize_route(img_path, steps):
    """Visualize the detected holds and route on the image"""
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Could not read image at {img_path}")
    
    # Draw detected holds and route
    for i, step in enumerate(steps):
        x, y = step["x"], step["y"]
        # Draw circle for hold position
        cv2.circle(img, (x, y), 15, (0, 255, 0), 2)
        # Draw step number
        cv2.putText(img, str(step["step"]), (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw line for route
        if i < len(steps) - 1:
            next_x, next_y = steps[i + 1]["x"], steps[i + 1]["y"]
            cv2.line(img, (x, y), (next_x, next_y), (255, 0, 0), 2)
    
    # Save the visualization
    output_path = "climbing_route_visualization.jpg"
    cv2.imwrite(output_path, img)
    print(f"Route visualization saved to {output_path}")
    return output_path

# ---------------- CLI / Demo ------------------
if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="Compute optimal climbing route from image")
    parser.add_argument("image", help="Path to climbing wall image")
    parser.add_argument("--json_out", default="route.json", help="Where to save route JSON")
    parser.add_argument("--visualize", action="store_true", help="Visualize detected route")
    args = parser.parse_args()

    holds = color_based_hold_detection(args.image)
    if len(holds) < 2:
        raise SystemExit("Not enough holds detected – check image quality or adjust color ranges.")

    G = build_hold_graph(holds)
    route = find_optimal_route(G)

    if not route:
        raise SystemExit("No path found from bottom to top – try relaxing constraints.")

    steps = route_to_steps(route, G)
    with open(args.json_out, "w") as f:
        json.dump(steps, f, indent=2)
    print(f"Route with {len(steps)} moves saved to {args.json_out}")
    
    if args.visualize:
        vis_path = visualize_route(args.image, steps)
        print(f"Route visualization saved to {vis_path}") 