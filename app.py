# follow this to configure the environment
# https://www.tutorialspoint.com/flask/flask_environment.htm
# running this file will open the development server at http://localhost:3000 in debug mode
# test routes are:
# http://localhost:3000
# http://localhost:3000/test

from flask import Flask, render_template
from CoT_Stream_Simulator.server import CoTServer
from threading import Thread
from turbo_flask import Turbo
from flask_sock import Sock
import time
import signal

app = Flask(__name__)
turbo = Turbo(app)
sock = Sock(app)

test_list = list()

server = CoTServer('127.0.0.1', 1870, test_list)
cot_ingest_thread = Thread(target=server.create_server)


@app.route('/')
def serve_leaflet():
   return render_template('index.html')

@app.route('/test')
def test():
   print(test_list)
   return "Test page"


@sock.route('/feed')
def feed(sock):
   while True:
      time.sleep(1)
      for data in test_list:
         sock.send(data)
      

if __name__ == '__main__':
   cot_ingest_thread.daemon = True
   cot_ingest_thread.start()
   
   app.run(host='localhost', port='3000', debug=False)

   
   