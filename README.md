# Real Time Geoinformation System

Application for tracking targets in real time created as a part of Senior Design at Stevens Institute of Technology.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install packages.

```bash
pip install flask
pip install flask_sock
```

#### Setup for the Flask virtual environment can be found [here](https://www.tutorialspoint.com/flask/flask_environment.htm).


## Running

Run `app.py` to start server.
Server will be visible on [localhost:3000](localhost:3000).

Once the server is running, the stream simulator or load tester can be used to populate the server with input streams for testing.

### Simulating input streams
```bash
python3 stream_simulator.py <number of streams>
```

### Load Testing

```bash
python3 load_tester.py <number of streams>
```