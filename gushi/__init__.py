# -*- coding: utf-8 -*-

from flask import Flask, request, url_for, render_template, g, session, flash
from flask_wtf.csrf import CsrfProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager
from flask.ext.moment import Moment

from . import filters, permissions
from .utils import signout_user
from .config import load_config

config = load_config()

# The current_user variable used in the conditional
# is defined by Flask-Login and is automatically available
# to view functions and templates. This variable contains
# the user currently logged in, or a proxy anonymous user
# object if the user is not logged in.
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.signin'
login_manager.login_message = '请先登陆以获得相应操作权限'

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def register_login_manager(app):
    """注册login_manager"""
    login_manager.init_app(app)


def register_jinja(app):
    # inject vars into template context to avoid having
    # to add a template argument in every render_template()
    # call, a context processor can be used. Context processors
    # make variables globally available to all templates.
    @app.context_processor
    def inject_vars():
        return dict(Permission=permissions.Permission)

    # url generator for pagination
    def url_for_other_page(page):
        """Generate url for pagination"""
        view_args = request.view_args.copy()
        args = request.args.copy().to_dict()
        combined_args = dict(view_args.items() + args.items())
        combined_args['page'] = page
        return url_for(request.endpoint, **combined_args)
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page


def register_routes(app):
    from .controllers import site, user, auth, admin
    # from .api_1_0 import api
    app.register_blueprint(site.bp, url_prefix='')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(auth.bp, url_prefix='/auth')
    # app.register_blueprint(api, url_prefix='/api/v1.0')


def register_error_handle(app):
    @app.errorhandler(403)
    def page_403(error):
        return render_template('site/403.html'), 403

    @app.errorhandler(404)
    def page_404(error):
        return render_template('site/404.html'), 404

    @app.errorhandler(405)
    def page_405(error):
        return render_template('site/405.html'), 405

    @app.errorhandler(500)
    def page_500(error):
        return render_template('site/500.html'), 500


def register_db(app):
    from .models import db
    db.init_app(app)


def register_mail(app):
    from .utils import mail
    mail.init_app(app)


def get_mail_handler():
    import logging
    from logging.handlers import SMTPHandler
    credentials = (config.SMTP_USER, config.SMTP_PASSWORD)
    mail_handler = SMTPHandler(config.SMTP_SERVER, config.SMTP_FROM,
                               config.SMTP_ADMIN, 'gushi-log', credentials, ())
    from logging import Formatter
    mail_handler.setFormatter(Formatter('''
        Message type:       %(levelname)s
        Location:           %(pathname)s:%(lineno)d
        Module:             %(module)s
        Function:           %(funcName)s
        Time:               %(asctime)s

        Message:

        %(message)s
    '''))
    mail_handler.setLevel(logging.ERROR)
    return mail_handler


def register_logger(app):
    """send error log to admin by smtp"""
    if not app.debug:
        app.logger.addHandler(get_mail_handler())


def register_moment(app):
    moment = Moment(app)


def get_current_user():
    """获取当前user，同时进行session有效性的检测
    """
    # 对应utils.py中signin_user方法
    # 豆瓣登陆则验证邮箱, 非豆瓣登陆不验证邮箱直接返回空值退出
    if 'signin_method' not in session:
        return None
    if 'user_id' not in session:
        return None
    from .models import User
    # 此处是user_id而不是douban_id
    user = User.query.filter(User.id == session['user_id']).first()
    if not user:
        signout_user()
        return None
    return user


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # CSRF protect
    CsrfProtect(app)

    if app.debug:
        DebugToolbarExtension(app)

    register_jinja(app)
    register_routes(app)
    register_error_handle(app)
    register_db(app)
    register_logger(app)
    register_login_manager(app)
    register_moment(app)
    register_mail(app)

    app.jinja_env.filters['markdown'] = filters.markdown
    app.jinja_env.filters['normalize'] = filters.normalize
    app.jinja_env.filters[
        'engrolename_chinrolename'] = filters.engrolename_chinrolename
    app.jinja_env.filters['ismyself'] = filters.ismyself

    @app.before_request
    def before_request():
        g.user = get_current_user()
        if g.user:
            if not g.user.is_activated:
                flash('账户尚未激活，请先登陆' + g.user.email + '查收验证邮件并激活账户')
                signout_user()
            if g.user.is_banned:
                flash('账户已被禁用, 请联系管理员')
                signout_user()

    return app

app = create_app()
