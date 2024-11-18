from flask import Blueprint, render_template, redirect, url_for, flash, request
from urllib.parse import quote
import os
from flask_login import current_user
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin :
            flash("Kamu tidak memiliki akses untuk halaman ini.", "danger")
            return render_template("error.html", error_code=403, error_message="Kamu tidak memiliki akses untuk halaman ini.")
        return f(*args, **kwargs)
    return decorated_function

admin = Blueprint('admin', __name__)

@admin.route('/home')
@admin_required
def home():
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