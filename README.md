# Real Time Geoinformation System

Application for tracking targets in real time.

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

### Simulating input streams
In the directory `/CoT_Stream_Simulator`, run `simulated_client.py`. Settings for what will be sent can be tweaked within `simulated_client.py`.