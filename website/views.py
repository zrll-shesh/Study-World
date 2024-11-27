from flask import Blueprint, render_template, redirect, request, url_for, jsonify
from urllib.parse import quote
from .models import get_content, TrackViewPoints, TrackFinishPoints, point_information
import os
from flask_login import login_required, current_user
from . import app

views = Blueprint('views', __name__)
courses_dir = os.path.join(os.getcwd(), "website/templates/courses")

@views.route('/courses/<class_name>')
@login_required
def courses(class_name):
    try:
        all_courses = get_content()
        if class_name in all_courses:
            courses_data = all_courses[class_name]
            return render_template('user/courses.html', class_name=class_name,
                                courses=courses_data, 
                                classes=all_courses.keys(),
                                current_url=quote(request.path),
                                user= current_user)
        else:
            return redirect(url_for(views.handle_exception))
    except Exception as e:
        return redirect(url_for(app.handle_exception, e=e))
    
# Route for rendering specific course files
@views.route('/courses/<class_name>/<course>/<course_file>', methods=['GET', 'POST'])
@login_required
def course_file_route(class_name, course, course_file):
    if request.method == 'POST':
        TrackFinishPoints(course_file)
    all_courses = get_content()
    course_file_path = os.path.join(courses_dir, class_name, course, f"{course_file}.html")
    if os.path.exists(course_file_path):
        TrackViewPoints(course_file)
        with open(course_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return render_template("template_module.html", content=html_content)
    else:
        return redirect(url_for(app.handle_exception))

@views.route('/home')
@login_required
def home():
    try:
        all_courses = get_content()
        example = [
            {"name": "Kimia", "class": "Kelas XII MIPA", "image": "chemistry.webp"},
            {"name": "Biologi", "class": "Kelas XI MIPA", "image": "biology.webp"},
            {"name": "Matematika", "class": "Kelas XI MIPA", "image": "math.webp"},
            {"name": "Fisika", "class": "Kelas X MIPA", "image": "physics.webp"},
            {"name": "Python", "class": "Untuk semua", "image": "coding.webp"},
        ]
        return render_template('user/home.html', classes=all_courses.keys(), courses=example, user= current_user, current_url=request.path)
    except Exception as e:
        return redirect(url_for(app.handle_exception, e=e))

@views.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    user_point, rank_data, chart_data = point_information(range_date='all')
    if request.method == 'POST':
        return jsonify(chart_data)
    print(rank_data)
    return render_template('user/profile.html', user= current_user, current_url=request.path, user_point=user_point, users_points= rank_data)

@views.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html', user= current_user, current_url=request.path)