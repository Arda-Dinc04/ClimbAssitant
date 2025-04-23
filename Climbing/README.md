# Climbing Route Analyzer

A web application that analyzes climbing routes from images and provides optimal movement suggestions with limb placement guidance.

## Features

- **Image Analysis**: Upload images of climbing walls or routes
- **Route Planning**: Automatically identifies the most efficient climbing path
- **Limb Placement**: Suggests which limb (left/right hand/foot) should be used for each hold
- **Movement Guidance**: Provides step-by-step instructions with body positioning advice
- **Interactive Visualization**: Shows the route on the climbing wall with numbered steps

## Getting Started

### Running the Application

#### Option 1: Simple HTML-only Version (No Installation Required)

Simply open the `index.html` file in any modern web browser:

1. Double-click on the `index.html` file in the Climbing directory
2. The application will open in your default browser
3. Use the "Load Demo Image" button to see a demonstration of the route analysis
4. Upload your own climbing wall images to analyze them

#### Option 2: With Flask Server (For Advanced Features)

If you want to use the full version with backend processing:

1. Install the required Python packages:
   ```
   pip install flask
   ```

2. Navigate to the Climbing directory:
   ```
   cd Climbing
   ```

3. Start the server:
   ```
   python server.py
   ```

4. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

### How to Use

1. **Upload Image:** Click "Upload Climbing Wall Image" to select a photo of a climbing wall
2. **Analyze:** Click "Analyze Route" to process the image and get route suggestions
3. **Follow Instructions:** The system will suggest which limb to use for each hold
4. **Demo:** Click "Load Demo Image" to see how the route analysis works with a sample image

## How It Works

1. **Hold Detection**: The system identifies climbing holds in the uploaded image
2. **Route Planning**: Creates an optimal route from bottom to top
3. **Limb Placement**: Analyzes each move to determine the best limb placement
4. **Visualization**: Displays the route with numbered steps and limb indicators

## Project Structure

- `index.html` - The web interface for the application (can be used standalone)
- `route_analyzer.py` - Core climbing route analysis algorithm
- `server.py` - Flask server for advanced features (optional)
- `README.md` - Documentation

## Future Improvements

- Support for real-time camera input
- Integration with computer vision models for automatic hold detection
- Advanced biomechanical analysis for more accurate movement suggestions
- User profiles to track climbing progress and preferences
- Support for different climbing styles and techniques

## License

This project is licensed under the MIT License - see the LICENSE file for details. 