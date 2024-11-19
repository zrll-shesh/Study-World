from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from urllib.parse import quote
import os
from flask_login import current_user
from functools import wraps
from random import randint
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin :
            flash("Kamu tidak memiliki akses untuk halaman ini.", "danger")
            return render_template("error.html", error_code=403, error_message="Kamu tidak memiliki akses untuk halaman ini.")
        return f(*args, **kwargs)
    return decorated_function

admin = Blueprint('admin', __name__)

def generate_test_data(x, views=None):
    today = datetime.now()
    data = []
    for i in range(x):  # Last 7 days
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        line = randint(50, 500)  # Random views between 50 and 500
        if views:
            data.append({'date': date, 'views': line})
        else:
            data.append({'date': date, 'user': line})
    return data[::-1]  # Reverse to have the oldest date first


@admin.route('/home', methods=['GET','POST'])
@admin_required
def home():
    if request.method == 'POST':
        data = request.get_json()
        chart_data = {}
        if data.get('graph')['user']:
            chart_data['user'] = generate_test_data(data.get('date'))
        if data.get('graph')['views']:
            chart_data['views'] = generate_test_data(data.get('date'), True)
        box_data = [
            randint(1,100),
            randint(1,10000),
            randint(1,100),
            randint(1,10000)
        ]
        return jsonify({"chart_data": chart_data, "box_data": box_data})
    return render_template("admin/home.html", current_url=request.path)

@admin.route('/page-management')
@admin_required
def pages():
    return render_template("admin/page-management.html", current_url=request.path)

@admin.route('/user-management')
@admin_required
def users():
    return render_template("admin/home.html", current_url=request.path)

@admin.route('/settings')
@admin_required
def settings():
    return render_template("admin/home.html", current_url=request.path)
