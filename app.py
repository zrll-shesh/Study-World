from flask import Flask, render_template,request
from urllib.parse import quote
import os

app = Flask(__name__)
courses_dir = os.path.join(os.getcwd(), "templates/courses")
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

all_courses = get_courses()
@app.route('/courses/<class_name>')
def courses(class_name):
    if class_name in all_courses:
        course_data = all_courses[class_name]
        img_paths = {}
        courses_list = {}
        # Collect image paths, courses, and course files
        for course_data_dict in course_data:
            for course_name, course_files in course_data_dict.items():
                img_paths[course_name] = []
                for course_file in course_files:
                    img_paths[course_name].append(f"/static/img/courses/{class_name}/{course_file}.jpg")
                courses_list[course_name] = (course_files) 
        # Render the courses page with dynamic data
        return render_template('courses.html', class_name=class_name, 
                               img_paths=img_paths, courses=courses_list, 
                               classes=all_courses.keys(),
                               current_url=quote(request.path))
    else:
        return render_template('404.html')

# Route for rendering specific course files
@app.route('/courses/<class_name>/<course>/<course_file>')
def course_file_route(class_name, course, course_file):
    course_file_path = os.path.join(courses_dir, class_name, course, f"{course_file}.html")
    if os.path.exists(course_file_path):
        return render_template(course_file_path, classes=all_courses.keys())
    else:
        return render_template('404.html')

@app.route('/')
def home():
    example = [
        {"name": "Kimia", "class": "Kelas XII MIPA", "image": "chemistry.webp"},
        {"name": "Biologi", "class": "Kelas XI MIPA", "image": "biology.webp"},
        {"name": "Matematika", "class": "Kelas XI MIPA", "image": "math.webp"},
        {"name": "Fisika", "class": "Kelas X MIPA", "image": "physics.webp"},
        {"name": "Python", "class": "Untuk semua", "image": "coding.webp"},
    ]
    return render_template('home.html', classes=all_courses.keys(), courses=example, current_url=request.path)

@app.route('/profile')
def profile():
    return render_template('profile.html', current_url=request.path)

@app.route('/settings')
def settings():
    return render_template('settings.html', current_url=request.path)

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)