import os
import secrets
from PIL import Image
from flask import url_for, current_app
from erp import mail
from flask_mail import Message


def save_picture(form_image, need_to_resize=True):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, 'static/profile_pics', image_fn)
    # we need to resize image (if we want to)
    if need_to_resize:
        output_size = (125, 125)
        form_image_ = Image.open(form_image)
        form_image_.thumbnail(output_size)
        form_image = form_image_
    form_image.save(image_path)
    return image_fn
    

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request', sender = 'notsobikeparts@gmail.com', recipients=[user.email])
    msg.body = f"""To reset your password visit following link:
{url_for('users.reset_token', token=token, _external=True)}

If you don't make this request, ignore thie email
    """
    mail.send(msg)