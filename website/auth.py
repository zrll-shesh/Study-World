from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from email_validator import validate_email
from string import punctuation
from .models import User
from . import mail, db
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import random

auth = Blueprint('auth', __name__)

def is_emailValid(email):
    try:
        validate_email(email)
        return True
    except Exception as e:
        print(e)
        return False

def generated_send_OTP(email):
    otp_code = random.randint(10**5, 10**6)
    msg = Message("Study World OTP Code", recipients=[email])
    msg.body = f"Your OTP Code is\n\n{otp_code}"
    mail.send(msg)
    return otp_code

@auth.route('/auth')
def auth_page():
    return render_template("auth.html")

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user: 
        if check_password_hash(user.password, password):
            if user.admin:
                return jsonify({"success": True, 'redirect': url_for('admin.home')})
            else:    
                return jsonify({"success": True, 'redirect': url_for('views.home')})
        else:
            return jsonify({"success": False, 'Message': 'Password salah, coba lagi.'})
    return jsonify({"success": False, 'Message': 'Email tidak ditemukan'})

otp_stored = {}
@auth.route('/signup', methods=['POST'])
def signup():
    global new_user
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password1 = data.get('password1')
    password2 = data.get('password2')
    response = {
        "success": False,
        "Message": ""
        }
    user = User.query.filter_by(email=email).first()
    if user:
        response['Message'] = "Email sudah terdaftar"
    elif len(name) < 4:
        response['Message'] = "Nama terlalu pendek"
    elif not is_emailValid(email):
        response['Message'] = "Email tidak valid"
    elif password1 != password2:
        response['Message'] = "Password tidak sama"
    elif len(password1) < 8:
        response['Message'] = "Password kurang dari 8 karakter"
    elif not any(c.isdigit() for c in password1):
        response['Message'] = "Password harus terdiri dari minimal satu angka"
    elif not any(c.isupper() for c in password1):
        response['Message'] = "Password harus terdiri dari minimal satu huruf besar"
    elif not any(c.islower() for c in password1):
        response['Message'] = "Password harus terdiri dari minimal satu huruf kecil"
    elif not any(c in punctuation for c in password1):
        response['Message'] = "Password harus terdiri dari minimal satu karakter spesial"
    else:
        response["success"] = True
        otp_stored[email] = {
            'username' : name,
            'password' : generate_password_hash(password1),
            'otp' : generated_send_OTP(email)
        }
        session['email'] = email
    return jsonify(response)

@auth.route('/otp', methods=['POST'])
def otp_confirmation():
    data = request.get_json()
    otp_input = data.get('otp')
    email = session.get('email')
    response = {
        "success": False,
        "Message": ""
    }
    if not email:
        response['Message'] = "Email tidak ditemukan. Silakan signup terlebih dahulu."

    elif email in otp_stored and otp_stored[email]['otp'] == otp_input:
        username = otp_stored[email]['username']
        password = otp_stored[email]['password']
        new_user = User(email=email, name=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        del otp_stored[email]
        session.pop('email', None)
        response = {
            "success": True,
            "redirect" : url_for('views.home')
        }
    else:
        response['Message'] = "OTP tidak valid"
    return jsonify(response)

@auth.route('/logout')
def logout():
    return redirect(url_for('auth.auth_page'))
