from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(), nullable=False)
    signedup_on = db.Column(db.DateTime(timezone=True), default=func.now())
    role = db.Column(db.String(10), nullable=False, default="user")
    posts = db.relationship("Post", cascade="all, delete", backref="user")
    comments = db.relationship("Comment", cascade="all, delete", backref="user")
    likes = db.relationship("Like", cascade="all, delete", backref="user")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    posted_on = db.Column(db.DateTime(timezone=True), default=func.now())
    comments = db.relationship("Comment", cascade="all, delete", backref="post")
    likes = db.relationship("Like", cascade="all, delete", backref="post")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    commented_on = db.Column(db.DateTime(timezone=True), default=func.now())
    post_id = db.Column(
        db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False
    )


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    liked_on = db.Column(db.DateTime(timezone=True), default=func.now())
    post_id = db.Column(
        db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False
    )
