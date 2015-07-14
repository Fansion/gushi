# -*- coding: utf-8 -*-


from .default_sample import Config


class ProductionConfig(Config):

    FLASKY_ADMIN = 'admin@production.com'
    FLASKY_PASSWORD = 'production'

    # db config
    DB_USER = 'user'
    DB_PASSWORD = 'user'
    DB_HOST = 'host'
    DB_NAME = 'db'
    SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s/%s" % (
        DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

    SECRET_KEY = ';;963qRU}1j99kjzb8^k3x(8&@6-B{'
