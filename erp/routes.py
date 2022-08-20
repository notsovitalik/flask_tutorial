from flask import render_template, url_for, flash, redirect, request
from erp import app, db, bcrypt, login_manager
from erp.forms import LoginForm, RegistrationForm
from erp.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required


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
@app.route('/home')
def home():
    return render_template('home.html', posts=posts, title = 'notsoerp')

@app.route('/about')
def about():
    return render_template('about.html', posts=posts, title = 'about')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data
                    , email=form.email.data
                    , password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data} account created! You can log in now.', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', titile='register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            requested_page = request.args.get('next')
            return redirect(requested_page) if requested_page else redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful! Please check your username and/or password', category='danger')
    return render_template('login.html', titile='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html', titile='account')