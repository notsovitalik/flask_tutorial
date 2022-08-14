from home.home import app as home_app
from second.second import app as second_app
from flask import Flask
import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# creating our superapp, that starts alll other apps
application = Flask(__name__)

# define all our apps and 
application.wsgi_app = DispatcherMiddleware(None, {
    '/home': home_app,
    '/second': second_app,
})

if __name__ == '__main__':
    application.run(host="0.0.0.0", port = 8000
                    , debug=True)