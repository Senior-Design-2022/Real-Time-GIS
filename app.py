# follow this to configure the environment
# https://www.tutorialspoint.com/flask/flask_environment.htm
# running this file will open the development server at http://localhost:3000 in debug mode
# test routes are:
# http://localhost:3000

from flask import Flask, render_template
from CoTUtils.CoTUtility import CoTUtility
from SocketUtils.SocketUtils import QueuedUDPClient
from flask_sock import Sock
from pathlib import Path
import json

app = Flask(__name__)
sock = Sock(app)


# render home page
@app.route('/')
def serve_leaflet():
   return render_template('index.html')


@sock.route('/feed')
def feed(sock):
   with open(Path(__file__).parent / "./config/location1/config0.json") as settings:
      wanted_params = json.load(settings)
      with QueuedUDPClient('127.0.0.1',1870) as scot:
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
