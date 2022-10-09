# follow this to configure the environment
# https://www.tutorialspoint.com/flask/flask_environment.htm
# running this file will open the development server at http://localhost:3000 in debug mode
# test routes are:
# http://localhost:3000
# http://localhost:3000/test
# http://localhost:3000/leaflet (this serves the static leaflet html page)

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
   return "Home page"

@app.route('/test')
def test():
   return "Test page"

@app.route('/leaflet')
def serve_leaflet():
   return render_template('leaflet_testing.html')

if __name__ == '__main__':
   app.run(host='localhost', port='3000', debug=True)