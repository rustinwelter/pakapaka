from flask import Blueprint, render_template, flash, redirect, url_for, jsonify

from flask_login import login_required, current_user

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

from .models import Post, User, Comment, Like
from . import db

from .utils import basic_auth

from datetime import timedelta

delta = timedelta(hours=9)


class PostForm(FlaskForm):
    textarea = TextAreaField(validators=[DataRequired()])
    submit = SubmitField(label="投稿")


class CommentForm(FlaskForm):
    textarea = TextAreaField(validators=[DataRequired()])
    submit = SubmitField(label="コメントする")


views = Blueprint("views", __name__)


# @views.app_errorhandler(404)
# def page_not_found(e):
#     return render_template("404.html", user=current_user), 404


# @views.app_errorhandler(500)
# def internal_error(e):
#     return render_template("500.html", user=current_user), 500


@views.route("/")
@basic_auth.login_required
def index():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    return render_template("index.html", user=current_user)


@views.route("/home")
@login_required
def home():
    form = CommentForm()
    posts = Post.query.all()
    return render_template(
        "home.html", form=form, user=current_user, posts=posts[::-1], delta=delta
    )


@views.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        text = form.textarea.data
        if text:
            flash(message="投稿しました")
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("views.home"))
        else:
            flash(message="入力内容がありません")
    return render_template("create-post.html", form=form, user=current_user)


@views.route("/delete-post/<post_id>")
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        flash(message="該当する投稿は存在しません")
    elif current_user.id != post.author:
        flash(message="権限がありません")
    else:
        db.session.delete(post)
        db.session.commit()
        flash(message="投稿は削除されました")
    return redirect(url_for("views.home"))


@views.route("/user/<username>")
@login_required
def posts(username):
    form = CommentForm()

    user = User.query.filter_by(username=username).first()

    if not user:
        flash(message="該当するユーザーは存在しません")
        return redirect(url_for("views.home"))

    posts = user.posts
    return render_template(
        "posts.html",
        form=form,
        user=current_user,
        posts=posts,
        username=username,
        name=user.name,
        delta=delta,
    )


@views.route("/post-comment/<post_id>", methods=["POST"])
@login_required
def post_comment(post_id):
    form = CommentForm()
    text = form.textarea.data
    if form.validate_on_submit():
        if not text:
            flash(message="入力内容がありません")
        else:
            post = Post.query.filter_by(id=post_id)
            if post:
                comment = Comment(text=text, author=current_user.id, post_id=post_id)
                db.session.add(comment)
                db.session.commit()
            else:
                flash(message="該当する投稿が存在しません")

    return redirect(url_for("views.home"))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash(message="該当するコメントは存在しません")
    elif current_user.id != comment.author:
        flash(message="権限がありません")
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for("views.home"))


@views.route("/like-post/<post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        jsonify({"error": "該当する投稿は存在しません"}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    return jsonify(
        {
            "likes": len(post.likes),
            "liked": current_user.id in map(lambda x: x.author, post.likes),
        }
    )


@views.route("/terms-of-service")
@basic_auth.login_required
def terms_of_service():
    return render_template("terms-of-service.html", user=current_user)


@views.route("/privacy-policy")
@basic_auth.login_required
def privacy_policy():
    return render_template("privacy-policy.html", user=current_user)
