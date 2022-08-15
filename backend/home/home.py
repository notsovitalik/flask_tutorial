from flask import Flask, render_template, url_for
from distutils.log import debug
import os

# define new html templates folder
template_folder = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_folder = os.path.join(template_folder, 'frontend')
template_folder = os.path.join(template_folder, 'templates')

app = Flask(__name__, template_folder=template_folder)

posts = [
    {
        'author': 'me',
        'title': 'title',
        'content': 'cont',
        'date_posted': 'today'
    },
    {
        'author': 'you',
        'title': 'toootle',
        'content': 'tonc',
        'date_posted': 'tomorrow'
    }
]

@app.route('/')
def home():
    return render_template('home.html', posts=posts, title = 'notsoerp')
