from email.mime import image
import os
from random import random
from datetime import datetime
import secrets
from PIL import Image
from crypt import methods
from flask import render_template, url_for, flash, redirect, request, abort
from erp import app, db, bcrypt, login_manager, mail
from erp.forms import (LoginForm, RegistrationForm, UpdateAccountForm, PostForm, RequestResetForm,
                       ResetPasswordForm)
from erp.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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


def save_picture(form_image, need_to_resize=True):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static/profile_pics', image_fn)
    # we need to resize image (if we want to)
    if need_to_resize:
        output_size = (125, 125)
        form_image_ = Image.open(form_image)
        form_image_.thumbnail(output_size)
        form_image = form_image_
    form_image.save(image_path)
    return image_fn
    

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.image.data:
            image_file = save_picture(form.image.data)
            # also i want to drop old picture before changing the name in db
            old_picture_path = os.path.join(app.root_path, 'static/profile_pics', current_user.image)
            if os.path.isfile(old_picture_path):
                os.remove(os.path.join(app.root_path, 'static/profile_pics', current_user.image))
            # and then change name to new file in db
            current_user.image = image_file
        current_user.username = form.username.data
        current_user.email = form.email.data 
        db.session.commit()
        flash('your account has been updated!', category = 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pics/{current_user.image}')
    return render_template('account.html', titile='account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data,
                    content = form.content.data,
                    date_posted = datetime.utcnow(),
                    user_id = current_user.id
                    )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', category = 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', titile='new post', form=form
                        , legend = 'New post')


@app.route('/post/<int:post_id>')
def post(post_id):
    # post = Post.query.get(post_id)
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author.id != current_user.id:
        abort(403) 
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', category = 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', titile='update post', form=form
                        , legend = 'Update post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author.id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', category = 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query\
            .filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request', sender = 'notsobikeparts@gmail.com', recipients=[user.email])
    msg.body = f"""To reset your password visit following link:
{url_for('reset_token', token=token, _external=True)}

If you don't make this request, ignore thie email
    """
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('email for reseting pssword has been sent', category='info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='reset password', form=form)
 

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', category='warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated', category='success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='reset password', form=form)