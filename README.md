# Projection Games Framework

[PROGAF](https://www.progaf.org) (Projection Games Framework) is a software framework to support development of games and other applications using projection mapping (also known as surface projection, video mapping or spatial augmented reality) and/or real world object tracking using cameras. Expected uses for the framework include the development of games and possibly other applications across several domains including education, training, marketing, exhibition, entertainment and art.

The goal of the project is to provide a light, conceptually clean, open source framework to support application development. Main features are:
- Object-oriented abstraction layer providing: 
  - Hardware Integration (standard camera, depth camera, projector)
  - Object detection, identification and tracking (with specific detectors for faces, eyes, hands, geometric shapes and blobs) using [OpenCV](https://opencv.org/) and Google [MediaPipe](https://github.com/google/mediapipe)
  - Gestures and events detection and processing
  - Easy integration of detected objects into other frameworks / game engines: 
    - PyGame
    - Panda3D

The framework also supports projection-mapping applications with specific features:
- Easy and intuitive projector-camera alignment and calibration
- Projection mapping over static surfaces and/or moving objects in real time
- Capabilities to render/project in real time any combination of video streams, images, textures, text or graphics

To install, clone the github main repo, install python dependencies: `<pip install -r requirements.txt>` and take a look to the provided examples.
