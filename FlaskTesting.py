# follow this to configure the environment
# https://www.tutorialspoint.com/flask/flask_environment.htm
# running this file will open the development server at http://127.0.0.1:5000
# test routes are:
# http://127.0.0.1:5000
# http://127.0.0.1:5000/test

from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
   return "Home page"

@app.route('/test')
def test():
   return "Test page"

if __name__ == '__main__':
   app.run()