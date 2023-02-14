# follow this to configure the environment
# https://www.tutorialspoint.com/flask/flask_environment.htm
# running this file will open the development server at http://localhost:3000 in debug mode
# test routes are:
# http://localhost:3000

from flask import Flask, render_template
from CoT_Stream_Simulator.server import CoTServer
from SITCoTmsg.SITCoTmsg import CoTUtility, SITQueuedUDPClient
from threading import Thread
from flask_sock import Sock
from pathlib import Path
import json

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

@sock.route('/feed')
def feed(sock):
   with open(Path(__file__).parent / "./config/location1/config0.json") as settings:
      wanted_params = json.load(settings)
      with SITQueuedUDPClient('127.0.0.1',1870) as scot:
         while(1):
               if(scot.available()):
                  item, good = scot.getitem()
                  print("Received " + "="*40)
                  print(item)
                  print("Decoded " + "="*40)

                  parsed = CoTUtility.parseData(item[1], wanted_params)
                  print(parsed)
                  sock.send(json.dumps(parsed))
                  
if __name__ == '__main__':
   app.run(host='localhost', port='3000', debug=False)

   
   