from flask import Blueprint, render_template, redirect, request,url_for
from urllib.parse import quote
from .models import get_content, TrackViewPoints, TrackFinishPoints
import os
from flask_login import login_required, current_user

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
        print(f"An error occurred: {e}")

# Route for rendering specific course files
@views.route('/courses/<class_name>/<course>/<course_file>')
@login_required
def course_file_route(class_name, course, course_file):
    all_courses = get_content()
    course_file_path = os.path.join(courses_dir, class_name, course, f"{course_file}.html")
    if os.path.exists(course_file_path):
        TrackViewPoints(course_file)
        return render_template(course_file_path, classes=all_courses.keys(), user= current_user)
    else:
        return redirect(url_for(views.handle_exception))

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
        print(f"An error occurred: {e}")

@views.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user= current_user, current_url=request.path)

@views.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html', user= current_user, current_url=request.path)

@views.errorhandler(Exception)
def handle_exception(e):
    error_code = getattr(e, 'code', 500)
    return render_template('error.html', error_code=error_code), error_code