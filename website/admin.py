from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from urllib.parse import quote
import os
from flask_login import current_user
from functools import wraps
from random import randint, choice
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

classes = ["Kelas X MIPA", "Kelas XI MIPA", "Kelas XII MIPA"]
courses = ["Kimia", "Biologi", "Matematika", "Fisika", "Python"]
data_content = [{'class': 'Kelas XII MIPA', 'course': 'Fisika', 'module': 'Module 8', 'creator': 'John Doe', 'created_at': '2024-08-11 01:09:46', 'views': 269}, {'class': 'Kelas XI MIPA', 'course': 'Kimia', 'module': 'Module 5', 'creator': 'John Doe', 'created_at': '2024-05-26 01:09:46', 'views': 467}, {'class': 'Kelas X MIPA', 'course': 'Biologi', 'module': 'Module 3', 'creator': 'Jane Roe', 'created_at': '2024-01-20 01:09:46', 'views': 468}, {'class': 'Kelas X MIPA', 'course': 'Python', 'module': 'Module 5', 'creator': 'Jane Roe', 'created_at': '2024-02-17 01:09:46', 'views': 24}, {'class': 'Kelas XI MIPA', 'course': 'Matematika', 'module': 'Module 2', 'creator': 'Bob Johnson', 'created_at': '2024-06-02 01:09:46', 'views': 57}, {'class': 'Kelas XI MIPA', 'course': 'Python', 'module': 'Module 8', 'creator': 'Bob Johnson', 'created_at': '2024-07-10 01:09:46', 'views': 428}, {'class': 'Kelas XII MIPA', 'course': 'Python', 'module': 'Module 10', 'creator': 'Alice Smith', 'created_at': '2024-11-09 01:09:46', 'views': 233}, {'class': 'Kelas XI MIPA', 'course': 'Biologi', 'module': 'Module 4', 'creator': 'Bob Johnson', 'created_at': '2024-05-30 01:09:46', 'views': 151}, {'class': 'Kelas X MIPA', 'course': 'Kimia', 'module': 'Module 9', 'creator': 'Jane Roe', 'created_at': '2024-09-23 01:09:46', 'views': 418}, {'class': 'Kelas XII MIPA', 'course': 'Python', 'module': 'Module 3', 'creator': 'John Doe', 'created_at': '2024-08-11 01:09:46', 'views': 248}, {'class': 'Kelas XI MIPA', 'course': 'Kimia', 'module': 'Module 9', 'creator': 'Jane Roe', 'created_at': '2024-07-05 01:09:46', 'views': 392}, {'class': 'Kelas XI MIPA', 'course': 'Kimia', 'module': 'Module 5', 'creator': 'Alice Smith', 'created_at': '2024-06-09 01:09:46', 'views': 348}, {'class': 'Kelas X MIPA', 'course': 'Python', 'module': 'Module 3', 'creator': 'Bob Johnson', 'created_at': '2024-02-12 01:09:46', 'views': 287}, {'class': 'Kelas X MIPA', 'course': 'Matematika', 'module': 'Module 4', 'creator': 'Bob Johnson', 'created_at': '2024-06-22 01:09:46', 'views': 80}, {'class': 'Kelas XI MIPA', 'course': 'Biologi', 'module': 'Module 6', 'creator': 'Bob Johnson', 'created_at': '2024-10-16 01:09:46', 'views': 399}, {'class': 'Kelas XI MIPA', 'course': 'Matematika', 'module': 'Module 5', 'creator': 'Jane Roe', 'created_at': '2024-07-10 01:09:46', 'views': 61}, {'class': 'Kelas XII MIPA', 'course': 'Kimia', 'module': 'Module 10', 'creator': 'John Doe', 'created_at': '2024-05-17 01:09:46', 'views': 22}, {'class': 'Kelas XII MIPA', 'course': 'Matematika', 'module': 'Module 7', 'creator': 'Bob Johnson', 'created_at': '2024-03-20 01:09:46', 'views': 367}, {'class': 'Kelas XI MIPA', 'course': 'Fisika', 'module': 'Module 2', 'creator': 'John Doe', 'created_at': '2024-03-24 01:09:46', 'views': 111}, {'class': 'Kelas XII MIPA', 'course': 'Python', 'module': 'Module 2', 'creator': 'Alice Smith', 'created_at': '2024-09-04 01:09:46', 'views': 76}]

@admin.route('/page-management', methods=['GET', 'POST'])
@admin_required
def pages():
    global data_content
    if request.method == 'POST':
        data = request.get_json()
        delete = data.get("delete")
        if delete:
            module_to_delete = delete.get("module")
            if module_to_delete:
                data_content = [content for content in data_content if content['module'] != module_to_delete]
        filtered_content = [
            content for content in data_content
            if (content['class'] in data.get("classes",[])) and
               (content['course'] in data.get("courses",[]))
        ]
        return render_template("admin/page_update.html", content_data=filtered_content)
    return render_template("admin/page-management.html", current_url=request.path, classes=classes, courses=courses, content_data=data_content)

@admin.route('/edit/courses/<class_name>/<course>/<course_file>')
@admin_required
def edit_module(class_name, course, course_file):
    return render_template("admin/page_update.html", current_url=request.path)

@admin.route('/add-post')
@admin_required
def add_page():
    

@admin.route('/user-management')
@admin_required
def users():
    return render_template("admin/home.html", current_url=request.path)

@admin.route('/settings')
@admin_required
def settings():
    return render_template("admin/home.html", current_url=request.path)
