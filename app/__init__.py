from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from dotenv import load_dotenv

import os

load_dotenv()

db = SQLAlchemy()


class AdminPage(AdminIndexView):
    @expose("/")
    def index(self):
        if current_user.role == "user":
            return redirect(url_for("views.home"))
        return self.render("/admin/index.html")


class AdminView(ModelView):
    def is_accessible(self):
        return True if current_user.role == "admin" else False

    def inaccessible_callback(self):
        return redirect(url_for("views.home"))


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["FLASK_ADMIN_SWATCH"] = os.getenv("FLASK_ADMIN_SWATCH")

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Post, Comment, Like

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    admin = Admin(app, index_view=AdminPage(), template_mode="bootstrap3")
    admin.add_view(AdminView(User, db.session))
    admin.add_view(AdminView(Post, db.session))
    admin.add_view(AdminView(Comment, db.session))
    admin.add_view(AdminView(Like, db.session))

    return app
