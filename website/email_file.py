import random
from flask import session
from flask_mail import Message
from flask import url_for
from jinja2 import Template
from website.models import User, DailyTrack
from sqlalchemy import func
from website import mail, db, app
from datetime import datetime
import os

def generated_send_OTP(email):
    with open(os.path.join(os.getcwd(), 'website/templates/mail/otp.html'), 'r', encoding='utf-8') as file:
        template = Template(file.read())
    otp_code = random.randint(10**5, 10**6)
    msg = Message(
        "OTP Verifikasi Study World",
        recipients=[email],
        html=template.render(otp_code=otp_code)
        )
    mail.send(msg)
    session['otp_code'] = otp_code
    session['otp_timestamp'] = datetime.now()

def daily_report():
    with open(os.path.join(os.getcwd(), 'website/templates/mail/daily_report.html'), 'r', encoding='utf-8') as file:
        template = Template(file.read())
    users = User.query.filter(User.email_notif['daily_report']).all()
    for user in users:
        points = db.session.query(func.sum(DailyTrack.user_point)).filter(DailyTrack.user_id == user.id).filter(DailyTrack.date == db.func.current_date()).scalar()
        if points == None:
                points = 0
        msg = Message(
            subject="Laporan Harian Study World", 
            recipients=[user.email],
            html= template.render(user=user.username, points=points, total_points=user.points, url_for=url_for)
            )
        mail.send(msg)

def daily_reminder():
    with open(os.path.join(os.getcwd(), 'website/templates/mail/daily_reminder.html'), 'r', encoding='utf-8') as file:
        template = Template(file.read())
    users = User.query.filter(User.email_notif['daily_reminder']).all()
    for user in users:
        msg = Message(
            subject="Pengingat Harian Study World", 
            recipients=[user.email],
            html= template.render(user=user.username, url_for=url_for)
            )
        mail.send(msg)