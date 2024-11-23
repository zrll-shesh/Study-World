from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
import os 
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.auth_page'
load_dotenv('website/.env')
app = Flask(__name__)
def create_app():
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] =  os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    from .views import views
    from .auth import auth
    from .admin import admin
    from .models import User
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin/')

    create_database(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    if not os.path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()

# @app.errorhandler(Exception)
# def handle_exception(e):
#     error_code = getattr(e, 'code', 500)
#     error_message = getattr(e, 'description', 'Sepertinya ada yang salah')
#     return render_template('error.html', error_code=error_code, error_message=error_message), error_code