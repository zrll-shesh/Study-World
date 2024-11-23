from . import db
from flask import url_for
from flask_login import UserMixin, current_user
from collections import defaultdict
from datetime import datetime,timedelta
from bs4 import BeautifulSoup
from sqlalchemy import func
import os
import base64


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.Date, nullable=False, default=db.func.current_date())
    content = db.relationship('Content', backref='creator', lazy=True)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Class = db.Column(db.String(150), nullable=False, index=True)
    Course = db.Column(db.String(150), nullable=False, index=True)
    Module = db.Column(db.String(150), nullable=False, index=True)
    Visit_point = db.Column(db.Integer, nullable=False, default=0)
    Finish_point = db.Column(db.Integer, nullable=False, default=0)
    Creator = db.Column(db.String(150), db.ForeignKey('user.username'), nullable=False)
    Created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    Views = db.Column(db.Integer, nullable=False, default=0)
    img_path = db.Column(db.String(150), nullable=False)

class DailyTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    page = db.Column(db.String(150), db.ForeignKey('content.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    user_point = db.Column(db.Integer, nullable=False, default=0)
    page_view = db.Column(db.Integer, nullable=False, default=0)

class TempContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Class = db.Column(db.String(150), index=True)
    Course = db.Column(db.String(150), index=True)
    Module = db.Column(db.String(150), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    generated_html = db.Column(db.Text)
    Visit_point = db.Column(db.Integer, default=0)
    Finish_point = db.Column(db.Integer, default=0)
    Created_at = db.Column(db.DateTime, default=db.func.now())

def TrackViewPoints(page):
    #track all point and view for each module
    user_id = current_user.get_id()
    page_id = Content.query.filter_by(Module=page).first().id
    page_views = Content.query.filter_by(Module=page).first().Views
    if user_id:
        page_views += 1
        today = db.func.current_date()
        data = DailyTrack.query.filter_by(user_id=user_id, page=page_id, date=today).first()
        point = Content.query.get(page_id).Visit_point
        if data:
            data.page_view += 1
            data.user_point += point
        else:
            new_track = DailyTrack(user_id=user_id, page=page_id, page_view=1, user_point=point)
            db.session.add(new_track)
        db.session.commit()
    else:
        return
    
def TrackFinishPoints(page):
    # add point if user finish the module
    user_id = current_user.get_id()
    page_id = Content.query.filter_by(Module=page).first().id
    data = DailyTrack.query.filter_by(user_id=user_id, page=page_id, date=db.func.current_date()).first()
    point = Content.query.get(page_id).Finish_point
    data.user_point += point
    db.session.commit()

def get_content(is_latest=False):
    # get all content to show in courses   
    if is_latest:
        latest_content = Content.query.order_by(Content.Created_at.desc()).limit(5).all()
        return latest_content
    all_content = Content.query.with_entities(
        Content.Class, Content.Course, Content.Module, Content.Created_at, Content.img_path
    ).order_by(Content.Class, Content.Course, Content.Created_at).all()
    result = defaultdict(lambda: defaultdict(list))
    for content in all_content:
        result[content.Class][content.Course].append((content.Module, content.img_path))
    return dict(result)

def content_dash(range_date):
    # get information for admin dashboard
    date_now = datetime.now().date()

    new_user = User.query.filter(func.date(User.timestamp) == date_now).count()
    total_user = User.query.count()
    total_content = Content.query.count()
    total_views = db.session.query(db.func.sum(DailyTrack.page_view)).scalar() or 0
    
    views_data = []
    user_data = []
    if range_date == 'all':
        views_data = db.session.query(DailyTrack.date, db.func.sum(DailyTrack.page_view))\
        .group_by(DailyTrack.date).all()
        user_data = db.session.query(User.timestamp,db.func.count(User.id))\
        .group_by(User.timestamp).all()
    else:
        range_date = int(range_date)
        start_date = date_now - timedelta(days=range_date)
        views_data = db.session.query(DailyTrack.date, db.func.sum(DailyTrack.page_view))\
        .filter(DailyTrack.date.between(start_date, date_now)).group_by(DailyTrack.date).all()
        user_data= db.session.query(User.timestamp, func.count(User.id))\
        .filter(User.timestamp.between(start_date, date_now)).group_by(User.timestamp).all()
    views_every_day = [{'date' : str(v[0]), 'views' : v[1]} for v in views_data]
    new_user_every_day = [{'date' : str(u[0]), 'user' : u[1]} for u in user_data]
    return new_user, total_user, total_content, total_views, new_user_every_day, views_every_day

def pages_information(is_draft=False):
    if is_draft:
        unique_classes = db.session.query(TempContent.Class).distinct().all()
        unique_courses = db.session.query(TempContent.Course).distinct().all()
        all_content = TempContent.query.order_by(TempContent.Created_at.desc()).all()
    else:
        unique_classes = db.session.query(Content.Class).distinct().all()
        unique_courses = db.session.query(Content.Course).distinct().all()
        all_content = Content.query.order_by(Content.Created_at.desc()).all()
    classes = [classe[0] for classe in unique_classes]
    courses = [course[0] for course in unique_courses]

    def format_datetime(dt):
        return dt.strftime('%d %B %Y %H:%M:%S')
    data_contents = [{
            'id' : content.id,
            'class': content.Class,
             'course': content.Course,
             'module': content.Module,
             'creator': getattr(content, 'Creator', None),
             'created_at': format_datetime(content.Created_at),
            'views': getattr(content, 'Views', None)}
    for content in all_content]
    return data_contents, classes, courses

def delete_page(id_content, is_draft=False):
    if is_draft:
        page = TempContent.query.filter_by(id=id_content).first()
    else:
        page = Content.query.filter_by(id=id_content).first()
        path_file = os.path.join(os.getcwd(), 'website/static/courses', page.Class, page.Course, page.Module,'.html')
        os.remove(path=path_file)
    if page:
        db.session.delete(page)
        db.session.commit()

def save_images_and_get_updated_html(html_content, class_name,course_name, module_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')
    
    for idx,image in enumerate(images):
        src = image.get('src')
        if src.startswith('data:image'):
            img_data = src.split(",")[1]
            img_type = src.split(";")[0].split("/")[1]
            
            # Generate a filename for the image
            image_filename = f"{module_name} img{idx+1}.{img_type}"
            if idx == 0:
                img_path = image_filename
            
            # Determine the directory for storing the image file
            directory = os.path.join(os.getcwd(),'website/static/img/courses', class_name, course_name)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            image_path = os.path.join(directory, image_filename)
            
            # Save the base64 image to the file
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(img_data))
            # Update the image src in the HTML to the relative file path
            image['src'] = url_for('uploaded_file', filename=os.path.join(course_name, class_name, image_filename))
    return str(soup), img_path
    
def save_html(html_content, class_name, course_name, module_name):
    directory = os.path.join('website/static/courses', class_name, course_name,'.html')
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, module_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

def update_publish(id_tempcontent,classe=None, course=None, module=None, html=None, is_published=None, Visit_point=None, Finish_point=None):
    if id_tempcontent and not is_published:
        temp_content = TempContent.query.filter_by(id=id_tempcontent).first()
        temp_content.Class = classe
        temp_content.Course = course
        temp_content.Module = module
        temp_content.generated_html = html
        temp_content.Visit_point = Visit_point
        temp_content.Finish_point = Finish_point
    if id_tempcontent and is_published:
        temp_content = TempContent.query.filter_by(id=id_tempcontent).first()
        html_with_img, img_path = save_images_and_get_updated_html(temp_content.generated_html, classe, course, module)
        save_html(html_with_img, classe, course, module)
        content = Content(Module=module, Class=classe, Course=course, Visit_point=Visit_point, Finish_point=Finish_point, img_path=img_path)
        db.session.add(content)
        db.session.delete(temp_content)
    db.session.commit()

def get_tempcontent(id_tempcontent=None, list_path=None, html=None):
    if id_tempcontent:
        return TempContent.query.filter_by(id=id_tempcontent).first()
    else:
        if list_path:
            temp_content = TempContent.query.filter_by(Class=list_path[0], Course=list_path[1], Module=list_path[2]).first()
        else:
            temp_content = TempContent(Class=None, Course=None, Module=None, generated_html=html, user_id=current_user.get_id())
            db.session.add(temp_content)
            db.session.commit()
        return temp_content

def delete_tempcontent(id_tempcontent=None):
    if id_tempcontent:
        temp_content = TempContent.query.filter_by(id=id_tempcontent).first()
        db.session.delete(temp_content)
        db.session.commit()
        
def point_information(user_id, leader=None, range_date=None):
    # get point information for each user
    if leader:
        top_leader = db.session.query(
            DailyTrack.user_id, db.func.sum(DailyTrack.user_point)
        ).group_by(DailyTrack.user_id).order_by(
            db.func.sum(DailyTrack.user_point).desc()
        ).limit(3).all()
    if range_date == 'all':
        user_point_every_day = db.session.query(DailyTrack.date, db.func.sum(DailyTrack.user_point)).filter(
            DailyTrack.user_id == user_id
        ).group_by(DailyTrack.date).all()
    elif range_date:
        start_date = db.func.current_date() - timedelta(days=range_date)
        user_point_every_day = db.session.query(DailyTrack.date, db.func.sum(DailyTrack.user_point)).filter(
            DailyTrack.user_id == user_id
        ).filter(DailyTrack.date.between(start_date, db.func.current_date())).group_by(DailyTrack.date).all()
    user_point = db.session.query(db.func.sum(DailyTrack.user_point)).filter(
        DailyTrack.user_id == user_id
    ).scalar()
    return user_point, top_leader, user_point_every_day