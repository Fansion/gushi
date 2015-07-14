# -*- coding: utf-8 -*-

import os


class Config:
    # set True in development
    DEBUG = False
    TESTING = False

    # administrator
    FLASKY_ADMIN = 'admin@default.com'
    FLASKY_ANONYMOUS = 'anonymous@default.com'
    FLASKY_PASSWORD = 'default'

    # number
    FLASK_STORIES_PER_PAGE = 5

    # app config
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    SESSION_COOKIE_NAME = 'default_session'

    # db config
    DB_USER = 'user'
    DB_PASSWORD = 'password'
    DB_HOST = 'host'
    DB_NAME = 'db'
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@host/db"

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # used as a general-purpose encryption key by Flask and several
    # third-party extensions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # smtp config
    SMTP_SERVER = ""
    SMTP_PORT = 25
    SMTP_USER = ""
    SMTP_PASSWORD = ""
    SMTP_FROM = ""
    SMTP_ADMIN = ""
