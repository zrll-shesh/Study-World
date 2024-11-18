from flask import Blueprint, render_template, redirect, request,url_for
from urllib.parse import quote
from . import db
import os
from flask_login import login_required, current_user

views = Blueprint('views', __name__)
courses_dir = os.path.join(os.getcwd(), "website/templates/courses")
def get_courses():
    courses = {}
    for class_name in os.listdir(courses_dir):
        class_path = os.path.join(courses_dir, class_name)
        if os.path.isdir(class_path):
            courses[class_name] = []
            for course in os.listdir(class_path):
                course_path = os.path.join(class_path, course)
                if os.path.isdir(course_path):
                    course_data = {course: []}
                    for course_file in os.listdir(course_path):
                        if course_file.endswith(".html"):
                            course_name = course_file.replace(".html", "")
                            course_data[course].append(course_name)
                    courses[class_name].append(course_data)
    return courses

@views.route('/courses/<class_name>')
@login_required
def courses(class_name):
    try:
        all_courses = get_courses()
        if class_name in all_courses:
            course_data = all_courses[class_name]
            courses_list = {}
            # Collect image paths, courses, and course files
            for course_data_dict in course_data:
                for course_name, course_files in course_data_dict.items():
                    courses_list[course_name] = (course_files)

            return render_template('user/courses.html', class_name=class_name,
                                courses=courses_list, 
                                classes=all_courses.keys(),
                                current_url=quote(request.path))
        else:
            return redirect(url_for(views.handle_exception))
    except Exception as e:
        print(f"An error occurred: {e}")

# Route for rendering specific course files
@views.route('/courses/<class_name>/<course>/<course_file>')
@login_required
def course_file_route(class_name, course, course_file):
    all_courses = get_courses()
    course_file_path = os.path.join(courses_dir, class_name, course, f"{course_file}.html")
    if os.path.exists(course_file_path):
        return render_template(course_file_path, classes=all_courses.keys())
    else:
        return redirect(url_for(views.handle_exception))

@views.route('/home')
@login_required
def home():
    try:
        all_courses = get_courses()
        example = [
            {"name": "Kimia", "class": "Kelas XII MIPA", "image": "chemistry.webp"},
            {"name": "Biologi", "class": "Kelas XI MIPA", "image": "biology.webp"},
            {"name": "Matematika", "class": "Kelas XI MIPA", "image": "math.webp"},
            {"name": "Fisika", "class": "Kelas X MIPA", "image": "physics.webp"},
            {"name": "Python", "class": "Untuk semua", "image": "coding.webp"},
        ]
        return render_template('user/home.html', classes=all_courses.keys(), courses=example, current_url=request.path)
    except Exception as e:
        print(f"An error occurred: {e}")

@views.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', current_url=request.path)

@views.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html', current_url=request.path)

@views.errorhandler(Exception)
def handle_exception(e):
    error_code = getattr(e, 'code', 500)
    return render_template('error.html', error_code=error_code), error_code