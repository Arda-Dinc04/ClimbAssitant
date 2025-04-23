"""
Climbing Route Analyzer Server
-----------------------------
A simple Flask server that handles image uploads, analyzes climbing routes,
and returns optimized routes with limb placement suggestions.
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import base64
import json
import time
from route_analyzer import ClimbingRouteAnalyzer

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze_route():
    """
    Analyze a climbing wall image and return route suggestions
    
    Expects a JSON payload with:
    {
        "image": "base64 encoded image data" or null if using demo image,
        "useDemo": true/false
    }
    """
    data = request.json
    
    # Handle demo mode
    if data.get('useDemo', False):
        # Use the predefined image and route
        analyzer = ClimbingRouteAnalyzer()
        route_data = analyzer.analyze_image_and_generate_route()
        
        # Create route data JSON
        route_json = {
            "route_info": {
                "total_steps": len(route_data),
                "difficulty": "intermediate",
                "image": "demo_image"
            },
            "holds": analyzer.holds,
            "instructions": route_data
        }
        
        return jsonify(route_json)
    
    # Handle image upload
    if 'image' in data and data['image']:
        # Extract the base64 image data
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        
        # Save the image to a temporary file
        image_filename = f"climbing_wall_{int(time.time())}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        
        # Analyze the image
        analyzer = ClimbingRouteAnalyzer()
        route_data = analyzer.analyze_image_and_generate_route(image_path)
        
        # Create route data JSON
        route_json = {
            "route_info": {
                "total_steps": len(route_data),
                "difficulty": "intermediate",
                "image": image_filename
            },
            "holds": analyzer.holds,
            "instructions": route_data
        }
        
        return jsonify(route_json)
    
    return jsonify({"error": "No image provided"}), 400

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    print("Starting Climbing Route Analyzer Server...")
    print("Open your browser to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0') 