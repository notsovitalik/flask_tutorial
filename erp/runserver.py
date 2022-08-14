from first.first import app as first_app
from second.second import app as second_app
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

application = Flask(__name__)

application.wsgi_app = DispatcherMiddleware(None, {
    '/first': first_app,
    '/second': second_app,
})

if __name__ == '__main__':
    application.run(host="0.0.0.0", port = 8000, debug=True)