from . import db
from flask_login import UserMixin, current_user
from collections import defaultdict
from datetime import timedelta

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
    Class = db.Column(db.String(150), nullable=False)
    Course = db.Column(db.String(150), nullable=False)
    Module = db.Column(db.String(150), nullable=False)
    Visit_point = db.Column(db.Integer, nullable=False, default=0)
    Finish_point = db.Column(db.Integer, nullable=False, default=0)
    Creator = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    Created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    view = db.relationship('DailyTrack', backref='tracked_content', lazy=True)

class DailyTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    user_point = db.Column(db.Integer, nullable=False, default=0)
    page_view = db.Column(db.Integer, nullable=False, default=0)
    page = db.Column(db.String(150), db.ForeignKey('content.id'), nullable=False)

def TrackViewPoints(page):
    #track all point and view for each module
    user_id = current_user.get_id()
    page_id = Content.query.filter_by(Module=page).first().id
    if user_id:
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

def get_content():
    # get all content to show in courses    
    all_content = Content.query.all()
    result = defaultdict(lambda x: defaultdict(list))
    for content in all_content:
        result[content.Class][content.Course].append(content)
    for class_name, courses in result.items():
        for course, content_list in courses.items():
            # sort content from the oldest to newest
            content_list.sort(key=lambda x: x.Created_at)
    return {class_name: {course_name: [content.Module for content in content_list] 
            for course_name, content_list in courses.items()} 
            for class_name, courses in result.items()}

def content_dash(views_range_date, user_range_date):
    # get information for admin dashboard
    total_user = User.query.count()
    total_content = Content.query.count()
    total_views = db.session.query(db.func.sum(DailyTrack.page_view)).scalar()
    date_now = db.func.curent_date().date
    if views_range_date == 'all':
        views_range_date = 0
    views_start_date = date_now - timedelta(days=views_range_date)
    views_every_day = db.session.query(db.func.sum(DailyTrack.page_view))\
        .filter(DailyTrack.date.between(views_start_date, date_now)).group_by(DailyTrack.date).all()
    if user_range_date == 'all':
        user_range_date = 0
    user_start_date = date_now - timedelta(days=user_range_date)
    new_user_every_day = db.session.query(db.func.count(User.id))\
        .filter(User.timestamp.between(user_start_date, date_now)).group_by(User.timestamp).all()
    return views_every_day, new_user_every_day, total_user, total_content, total_views

def page_information(page):
    # get information for each page to show in page management
    page_id = Content.query.filter_by(Module=page).first().id
    page_view = db.session.query(db.func.sum(DailyTrack.page_view)).filter(
        DailyTrack.page == page_id
    ).scalar()
    created_at = Content.query.get(page_id).Created_at
    creator = User.query.get(Content.query.get(page_id).Creator).username
    return page_view, creator, created_at

def point_information(user_id, leader=None, range_date=None):
    # get point information for each user
    top_leader = None
    user_point_every_day = None
    if leader:
        top_leader = db.session.query(DailyTrack.user_id,
                    db.func.sum(DailyTrack.user_point)).group_by(DailyTrack.user_id).order_by(
                    db.func.sum(DailyTrack.user_point).desc()).limit(3).all()
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