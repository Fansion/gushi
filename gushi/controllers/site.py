# -*- coding: utf-8 -*-

from flask import render_template, Blueprint, redirect, url_for, request, flash, current_app, jsonify
from flask.ext.login import current_user

from ..models import db, Story, User

import os
from datetime import datetime

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """首页"""
    return redirect(url_for('site.hot'))


@bp.route('/hot')
def hot():
    stories = Story.query.limit(4).all()
    ids_stories = {}
    for story in stories:
        ids_stories[story.id] = story
    # 按照点赞数从高到低决定热门故事
    ids_stories = sorted(
        ids_stories.items(), key=lambda d: d[1].upvotes.count(), reverse=True)
    hot_stories = [story for upvotes_count, story in ids_stories]

    hot_stories__son_stories = []
    for hot_story in hot_stories:
        son_stories = Story.query.filter_by(
            parent_story_id=hot_story.id).order_by(Story.created.desc()).all()
        hot_stories__son_stories.append((hot_story, son_stories))
    return render_template('site/index.html', hot_stories__son_stories=hot_stories__son_stories, hot=True)


@bp.route('/new', defaults={'page': 1})
@bp.route('/new/page/<int:page>')
def new(page):
    new_stories__son_stories = []
    new_stories = Story.query.order_by(Story.created.desc())
    new_stories = new_stories.paginate(
        page, current_app.config['FLASK_STORIES_PER_PAGE'], error_out=True)

    for hot_story in new_stories.items:
        son_stories = Story.query.filter_by(
            parent_story_id=hot_story.id).order_by(Story.created.desc()).all()
        new_stories__son_stories.append((hot_story, son_stories))
    return render_template('site/index.html', stories=new_stories, page=page, new_stories__son_stories=new_stories__son_stories, new=True)


@bp.route('/about')
def about():
    """关于"""
    return render_template('site/about.html')


@bp.route('/reposts/<int:story_id>')
def reposts(story_id):
    stories__son_stories = []
    # 原故事
    story = Story.query.filter_by(id=story_id).first()
    son_stories = Story.query.filter_by(
        parent_story_id=story_id).order_by(Story.created.desc()).all()
    # 添加父故事
    if story.parent_stories_ids:
        for parent_story_id in story.parent_stories_ids.split(','):
            parent_story = Story.query.filter_by(id=parent_story_id).first()
            stories__son_stories.append((parent_story, Story.query.filter_by(
                parent_story_id=parent_story.id).order_by(Story.created.desc()).all()))
    # 添加待续写的故事
    stories__son_stories.append((story, son_stories))
    return render_template('site/reposts.html', stories__son_stories=stories__son_stories)


@bp.route('/user/<int:user_id>/stories')
def user_stories(user_id):
    stories__son_stories = []
    user = User.query.filter_by(id=user_id).first()
    stories = Story.query.filter_by(user_id=user_id).all()
    for story in stories:
        # 添加子故事
        son_stories = Story.query.filter_by(
            parent_story_id=story.id).order_by(Story.created.desc()).all()
        stories__son_stories.append((story, son_stories))
    return render_template('site/user_stories.html', stories__son_stories=stories__son_stories, user=user)
