from distutils.log import debug
from flask import Flask


app = Flask(__name__)

@app.route('/')
def hello_world():
    return f"Hello, it's {__name__}"

