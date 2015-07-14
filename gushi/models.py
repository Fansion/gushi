# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app, request
from werkzeug.security import generate_password_hash, check_password_hash

from . import login_manager
from permissions import Permission

import datetime
import hashlib

db = SQLAlchemy()


class Role(db.Model):

    """角色"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.REPOST | Permission.UPVOTE | Permission.SHARE | Permission.FOLLOW, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
        db.session.commit()

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return "Role %s" % self.name


class User(UserMixin, db.Model):

    """用户"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(32))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    stories = db.relationship(
        'Story', backref='user', lazy='dynamic', order_by='desc(Story.created)')
    upvotes = db.relationship(
        'Upvote', backref='user', lazy='dynamic', order_by='desc(Upvote.created)')

    @staticmethod
    def insert_admin():
        u = User.query.filter_by(
            email=current_app.config['FLASKY_ADMIN']).first()
        if u is None:
            u = User(email=current_app.config[
                     'FLASKY_ADMIN'], username='root', password=current_app.config['FLASKY_PASSWORD'])
            db.session.add(u)
            db.session.commit()

    @staticmethod
    def insert_anonymous_user():
        u = User.query.filter_by(username='匿名').first()
        if u is None:
            u = User(email=current_app.config[
                     'FLASKY_ANONYMOUS'], username='匿名')
            db.session.add(u)
            db.session.commit()

    def __repr__(self):
        return "User %s" % self.username


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Story(db.Model):

    """故事"""
    __tablename__ = 'stories'
    id = db.Column(db.Integer, primary_key=True)
    parent_story_id = db.Column(db.Integer)
    parent_stories_ids = db.Column(db.Text)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    repost_count = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    upvotes = db.relationship(
        'Upvote', backref='story', lazy='dynamic', order_by='desc(Upvote.created)')

    def to_json(self):
        json_story = {
            # 'parent_story' : url_for('api.get_story', id=self.parent_story_id, _external=True),
            'parent_story_id': self.parent_story_id,
            'parent_stories_ids': self.parent_stories_ids,
            'title': self.title,
            'content': self.content,
            'repost_count': self.repost_count,
            'created': self.created,
            # 'user': url_for('api.get_user', id=self.user_id, _external=True),
            'user_id': self.user_id,
            'upvotes': self.upvotes
        }
        return json_story

    @staticmethod
    def from_json(json_story):
        parent_story_id = json_story.get('parent_story_id')
        parent_stories_ids = json_story.get('parent_stories_ids')
        title = json_story.get('title')
        content = json_story.get('content')
        user_id = json_story.get('user_id')
        if not title or not title.strip():
            raise ValidationError('story does not have a title')
        if not content or not content:
            raise ValidationError('story does not have a body')
        if not user_id or not user_id:
            raise ValidationError('story does not have a user_id')
        return Story(parent_story_id=parent_story_id, parent_stories_ids=parent_stories_ids,
                     title=title, content=content, user_id=user_id)

    def __repr__(self):
        return "Story (%s->%s)" % (self.title, self.content)


class Upvote(db.Model):

    """点赞"""
    __tablename__ = 'upvotes'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'))

    def __repr__(self):
        return "Upvote %s->%s" % (self.user_id, self.story_id)


class Follow(db.Model):

    """关注"""
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    fans_id = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "Follow %s->%s" % (self.fans_id, self.user_id)
