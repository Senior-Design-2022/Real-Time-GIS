# follow this to configure the environment
# https://www.tutorialspoint.com/flask/flask_environment.htm
# running this file will open the development server at http://localhost:3000 in debug mode
# test routes are:
# http://localhost:3000
# http://localhost:3000/test

from flask import Flask, render_template
from CoT_Stream_Simulator.server import CoTServer
from threading import Thread
from flask_sock import Sock
import time
import json
import copy

# class to hold CoT data from the CoT server
class CoT:
   def __init__(self) -> None:
      self.time = ''
      self.id = ''
      self.lat = float()
      self.lon = float()
      self.alt = float()

   # convert to JSON to send over socket
   def toJSON(self):
      return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

   # for printing
   def __str__(self) -> str:
      return self.time + ',' + self.id + ',' + str(self.lat) + ',' + str(self.lon) + ',' + str(self.alt)

   # to check equality
   def __eq__(self, other):
      if isinstance(other, self.__class__):
         return self.__dict__ == other.__dict__
      else:
         return False

app = Flask(__name__)
sock = Sock(app)

stream_data = CoT() # data passthrough from CoTServer

# CoT Server thread initialization
server = CoTServer('127.0.0.1', 1870, stream_data)
cot_ingest_thread = Thread(target=server.create_server)

# render home page
@app.route('/')
def serve_leaflet():
   return render_template('index.html')

# route for testing
@app.route('/test')
def test():
   print(stream_data)
   return "Test page"

# init web socket
@sock.route('/feed')
def feed(sock):
   previous = CoT()
   while True:
      # send data to socket once every second
      time.sleep(1)
      # ensures same data point isn't sent repeatedly
      if stream_data == previous:
         continue
      sock.send(stream_data.toJSON())
      previous = copy.copy(stream_data)
      

if __name__ == '__main__':
   cot_ingest_thread.daemon = True
   cot_ingest_thread.start()
   
   app.run(host='localhost', port='3000', debug=False)

   
   