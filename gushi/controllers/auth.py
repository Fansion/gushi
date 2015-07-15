# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, request,  session, flash, current_app
from flask.ext.login import login_user, logout_user, login_required

from ..forms import SigninForm, RegisterForm
from ..models import db, User
from ..decorators import logout_required
from ..utils import signin_user
from ..qq_api import APIClient


import requests


bp = Blueprint('auth', __name__)

# 说明：
# 在本站注册登陆无需验证邮箱，直接登陆
# 直接注册登陆不检查状态
# 直接注册登陆退出使用flask_login的logout_user


@bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登陆')
        return redirect(url_for('auth.signin'))
    return render_template('auth/register.html', form=form)


@bp.route('/signin', methods=['GET', 'POST'])
@logout_required
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('该邮箱尚未注册，请重新登陆')
            return render_template('auth/signin.html', form=form)
        if user is not None and user.verify_password(form.password.data):
            flash('欢迎登陆GuShi')
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('site.index'))
        flash('邮箱或密码错误，请重新登陆')
    return render_template('auth/signin.html', form=form)


@bp.route('/signout')
@login_required
def signout():
    logout_user()
    flash('成功登出GuShi,欢迎再次访问本站')
    return redirect(url_for('site.index'))


@bp.route('qq_pre_signin')
@logout_required
def qq_pre_signin():
    pass


@bp.route('qq_signin')
@logout_required
def qq_signin():
    pass


@bp.route('/douban_pre_signin')
@logout_required
def douban_pre_signin():
    config = current_app.config
    return redirect(config.get('DOUBAN_LOGIN_URL'))


@bp.route('/douban_signin')
@logout_required
def douban_signin():
    """通过豆瓣OAuth登陆
    user_id实际是User表中的douban_id字段
    """
    # get current authed user id
    code = request.args.get('code')
    if not code:
        return redirect(url_for('site.index'))
    url = "https://www.douban.com/service/auth2/token"
    config = current_app.config
    data = {
        'client_id': config.get('DOUBAN_CLIENT_ID'),
        'client_secret': config.get('DOUBAN_SECRET'),
        'redirect_uri': config.get('DOUBAN_REDIRECT_URI'),
        'grant_type': 'authorization_code',
        'code': code
    }
    res = requests.post(url, data=data).json()
    if 'douban_user_id' not in res:
        return redirect(url_for('site.index'))

    user_id = int(res['douban_user_id'])
    user = User.query.filter_by(douban_id=user_id).first()
    if user:
        user.access_token = res['access_token']
    else:
        url = "https://api.douban.com/v2/user/%d" % user_id
        user_info = requests.get(url).json()
        # get user info from douban, store id as email for gravatar
        user = User(email=user_info['id'], douban_id=user_id,
                    username=user_info['name'])
    flash('欢迎使用豆瓣账户登陆GuShi')
    login_user(user)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('site.index'))
