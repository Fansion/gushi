# -*- coding: utf-8 -*-

from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, SubmitField, TextField, PasswordField, SelectField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Email

from models import User


class RegisterForm(Form):

    email = StringField(
        '邮箱*', description='未被注册过的邮箱', validators=[DataRequired('邮箱不能为空'), Length(1, 64), Email('邮箱格式不正确')])
    username = TextField(
        '昵称*', description='未被使用过的昵称', validators=[DataRequired('昵称不能为空'), Length(1, 64)])
    password = PasswordField('密码*', validators=[
        DataRequired('密码不能为空'),
        EqualTo('confirm', message='密码不一致，请重新输入密码')]
    )
    confirm = PasswordField(
        '确认*', description='重复输入密码确认', validators=[DataRequired('密码不能为空')])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册过，请更换邮箱')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用，请更换用户名')


class SigninForm(Form):

    email = StringField(
        '邮箱*', description='使用已注册过的邮箱', validators=[DataRequired('邮箱不能为空'), Length(1, 64), Email('邮箱格式不正确')])
    password = PasswordField('密码*', validators=[DataRequired('密码不能为空')])
    # recaptcha = RecaptchaField()
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class StoryForm(Form):

    title = TextField(
        '标题', description='标题', validators=[DataRequired('标题不能为空')])
    content = TextAreaField(
        '内容', description='鼠标移到右下角点击移动拖大此框,支持markdown', validators=[DataRequired('内容不能为空')])


class RepostStoryForm(Form):

    content = TextAreaField(
        '内容', description='鼠标移到右下角点击移动拖大此框,支持markdown', validators=[DataRequired('内容不能为空')])


class SingleStoryForm(Form):

    title = TextField('故事标题')
    content = TextField('故事内容')
    user_id = SelectField('创建人',  coerce=int)
