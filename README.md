# ClimbAssitant

1. Take an image of a bouldering problem
2. . Detect the holds and wall layout
  3. Hold Detection (Computer Vision / Object Detection)
    We need to detect:
      Where holds are
      Which are start, middle, and top holds
      Train a YOLOv8 or Detectron2 model on climbing hold annotations
     
5. Predict the optimal sequence of body positions (moves) to solve it
  Pose Dataset Collection (Pro Climbers)
    Gather climbing videos/images of pros on V0–V4 routes (Simple for now)
    Annotate:
      Body positions (keypoints: feet/hands/hips)
      Sequence of moves (this becomes your target prediction)
      Use pose estimation (e.g., OpenPose, AlphaPose) to auto-label joints
      Structure into a dataset: [(hold layout, climber path)]

    Modeling Optimal Movement
      You’ll need to train a model that learns from pose sequences given hold positions:
      Input: Image of wall (or detected hold map)
      Output: Sequence of predicted joint positions or hold usage order

7. Base this on prior examples of professionals climbing similar problems

Task	                        Tool
Pose Estimation	      MediaPipe, OpenPose, AlphaPose
Object Detection	    YOLOv8, Detectron2
Graph Modeling	      PyTorch Geometric, DGL
Video Labeling	      CVAT, VOTT
