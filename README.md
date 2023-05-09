# Real Time Geoinformation System

Application for tracking targets in real time created as a part of Senior Design at Stevens Institute of Technology.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install packages.

#### Setup for the Flask virtual environment can be found [here](https://www.tutorialspoint.com/flask/flask_environment.htm).

## Starting the Application
The application can be run by using the [start.bat](https://github.com/Senior-Design-2022/Real-Time-GIS/blob/main/start.bat) file. \
Configuration of the host IP and port can be done in [start.bat](https://github.com/Senior-Design-2022/Real-Time-GIS/blob/main/start.bat)

### Replay File Locations
When a recording is started, it will be automatically created in the [/Logger/replays](https://github.com/Senior-Design-2022/Real-Time-GIS/tree/main/Logger/replays) directory of the repository. Additionally, for a recording to be discoverable by the application, it must be in this directory.

### Static Overlay File Locations
Static overlays must be placed in the [/static/overlays](https://github.com/Senior-Design-2022/Real-Time-GIS/tree/main/static/overlays) directory of the repository to be servable by the server.

### Offline Tiles File Locations
Similarly, offline map tiles must be placed in the [/static/tiles](https://github.com/Senior-Design-2022/Real-Time-GIS/tree/main/static/tiles) directory of the repository to be servable by the server. \
Within this directory, tiles should be contained in folders and *NOT* in the root of the /static/tiles directory.
