from flask import Blueprint, render_template, redirect, url_for, flash

from . import db
from .models import User
from .utils import basic_auth

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Regexp,
)

from password_strength import PasswordPolicy

from flask_login import login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

import re


class LogInForm(FlaskForm):
    email = EmailField(
        label="メールアドレス", validators=[DataRequired(message="メールアドレスを入力してください")]
    )
    password = PasswordField(
        label="パスワード", validators=[DataRequired(message="パスワードを入力してください")]
    )
    submit = SubmitField(label="ログイン")


class SignUpForm(FlaskForm):
    def validate_email(form, email_to_check):
        email_exists = User.query.filter_by(email=email_to_check.data).first()
        if email_exists:
            raise ValidationError(message="正しいメールアドレスを入力してください")

    def validate_username(form, username_to_check):
        username_exists = User.query.filter_by(username=username_to_check.data).first()
        if username_exists:
            raise ValidationError(message="ユーザー名は既に使用されています")

    def validate_password(form, password_to_check):
        password_policy = PasswordPolicy.from_names(strength=0.5)
        if password_policy.test(password_to_check.data) != []:
            raise ValidationError(message="パスワードが弱すぎます")

    name = StringField(
        label="名前",
        validators=[Length(min=3, max=50), DataRequired(message="名前を入力してください")],
        description="3文字以上50文字以下",
    )

    username = StringField(
        label="ユーザー名",
        validators=[
            Regexp(
                regex=r"^(?!.*pakapaka.*|.*admin.*)([0-9a-zA-Z_])",
                flags=re.IGNORECASE,
                message="不正なユーザー名です",
            ),
            Length(min=5, max=20),
            DataRequired(message="ユーザー名を入力してください"),
        ],
        description="5文字以上20文字以下の英数字およびアンダーバーのみ",
    )
    email = EmailField(
        label="メールアドレス",
        validators=[
            Email(message="正しいメールアドレスを入力してください", check_deliverability=True),
            DataRequired(),
        ],
    )
    password = PasswordField(
        label="パスワード",
        validators=[DataRequired("パスワードを入力してください")],
    )
    confirm = PasswordField(
        label="パスワード（確認）",
        validators=[EqualTo("password", message="パスワードが一致しませんでした"), DataRequired()],
    )
    agree_to_tos = BooleanField(
        validators=[DataRequired(message="ご利用いただくには利用規約への同意が必要です")],
        description="利用規約 に同意します",
    )
    submit = SubmitField(label="登録する")


class AccountDeletionForm(FlaskForm):
    email = EmailField(
        label="メールアドレス",
        validators=[
            Email(message="正しいメールアドレスを入力してください", check_deliverability=True),
            DataRequired(),
        ],
    )
    password = PasswordField(
        label="パスワード", validators=[DataRequired(message="パスワードを入力してください")]
    )
    submit = SubmitField(label="退会する")


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
@basic_auth.login_required
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                flash(message="ログインしました")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
        else:
            flash(message="メールアドレスまたはパスワードが間違っています")
    return render_template("login.html", form=form, user=current_user)


@auth.route("/signup", methods=["GET", "POST"])
@basic_auth.login_required
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            password=generate_password_hash(form.password.data, method="scrypt"),
            name=form.name.data,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash(message="登録が完了しました")
        return redirect(url_for("views.home"))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(message=f"{err_msg}")

    return render_template("signup.html", form=form, user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash(message="ログアウトしました")
    return redirect(url_for("views.index"))


@auth.route("/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    form = AccountDeletionForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.id == current_user.id:
                if check_password_hash(user.password, form.password.data):
                    db.session.delete(user)
                    db.session.commit()
                    flash(message="アカウントは削除されました")
                    return redirect(url_for("views.index"))
        else:
            flash(message="メールアドレスまたはパスワードが間違っています")
    return render_template(
        "delete.html",
        form=form,
        user=current_user,
        name=current_user.name,
        username=current_user.username,
    )
