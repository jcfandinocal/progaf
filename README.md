# PROGAF
A python framework to develop games with real world object tracking (using cameras) combined with projection mapping

## Installation
To install, just run `pip install progaf`. Please take a look a the provided [examples](https://github.com/jcfandinocal/progaf/tree/main/examples)

## About
The goal of the project is to provide a light, conceptually clean, open source framework to support application development using projection mapping (also known as surface projection, video mapping or spatial augmented reality) and/or real world object tracking using cameras. Expected uses for the framework include the development of games and possibly other applications across several domains including education, training, marketing, exhibition, entertainment and art.

Main features are:
- Object-oriented abstraction layer including: 
  - Hardware Integration (standard camera, depth camera, projector)
  - Object detection, identification and tracking (with specific detectors for faces, eyes, hands, geometric shapes and blobs) using [OpenCV](https://opencv.org) and Google [MediaPipe](https://github.com/google/mediapipe)
  - Gestures and events detection and processing
  - Integration of detected objects into existing game engines: 
    - [PyGame](https://github.com/pygame/pygame)
    - [Panda3D](https://www.panda3d.org)

The framework also supports projection-mapping applications with specific features:
- Easy and intuitive projector-camera alignment and calibration
- Affine and pespective transformations of application objects
- Projection mapping over static surfaces and/or moving objects in real time
- Capabilities to render/project in real time any combination of video streams, images, textures, text or graphics

## Contributing
Contributions are welcome. Please feel free to fork the repo and submit pull requests.
