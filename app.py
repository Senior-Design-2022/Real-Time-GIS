# follow this to configure the environment
# https://www.tutorialspoint.com/flask/flask_environment.htm
# running this file will open the development server at http://localhost:3000 in debug mode
# test routes are:
# http://localhost:3000

from flask import Flask, render_template, send_from_directory
from flask_sock import Sock
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from CoTUtils.CoTUtility import CoTUtility
from SocketUtils.SocketUtils import SITQueuedUDPClient
from Logger.SaveReplay import SaveReplay

# for colored prints
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# initialize flask application
app = Flask(__name__, static_folder='static')
sock = Sock(app)

# initialize logger for saving replays
logger = SaveReplay(debug=True)

# render home page
@app.route('/')
def serve_leaflet():
   return render_template('index.html')

@sock.route('/feed')
def feed(sock):
   with open(Path(__file__).parent / "./config/location1/config0.json") as settings:
      wanted_params = json.load(settings)
      with SITQueuedUDPClient('127.0.0.1',1870) as scot:
         while(1):
            if scot.available():
               item, good = scot.getitem()
               
               # checks for a timeout
               if good:
                  # raw input
                  print(f"\n{bcolors.HEADER}raw:{bcolors.ENDC}")
                  print(item)
                  logger.write_to_log(item[1])

                  # parse to front end format
                  parsed = CoTUtility.parseData(item[1], wanted_params)
                  
                  # print parsed input
                  print(f"{bcolors.HEADER}parsed:{bcolors.ENDC}")
                  print(parsed)

                  # send to front end
                  sock.send(json.dumps(parsed))
                  

if __name__ == '__main__':
   app.run(host='localhost', port='3000', debug=False)
