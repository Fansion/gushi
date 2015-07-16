# -*- coding: utf-8 -*-

from flask import render_template, Blueprint, redirect, url_for, flash, request, current_app
from flask.ext.login import login_required, current_user

from ..models import db, User, Story, Upvote
from ..forms import StoryForm, RepostStoryForm, UserForm, PasswordForm

bp = Blueprint('user', __name__)


@bp.route('/mine')
@login_required
def mine():
    """我的"""
    return redirect(url_for('user.my_stories'))


@bp.route('/my_stories', defaults={'page': 1})
@bp.route('/my_stories/page/<int:page>')
@login_required
def my_stories(page):
    my_stories = Story.query.filter_by(
        user_id=current_user.id).order_by(Story.created.desc())
    my_stories = my_stories.paginate(
        page, current_app.config['FLASK_STORIES_PER_PAGE'], error_out=True)

    my_stories__son_stories = []
    for my_story in my_stories.items:
        son_stories = Story.query.filter_by(
            parent_story_id=my_story.id).order_by(Story.created.desc()).all()
        my_stories__son_stories.append((my_story, son_stories))
    return render_template('user/mine.html', stories=my_stories, page=page,
                           my_stories__son_stories=my_stories__son_stories, my=True)


@bp.route('/my_upvote_stories', defaults={'page': 1})
@bp.route('/my_upvote_stories/page/<int:page>')
@login_required
def my_upvote_stories(page):
    # 拿到我喜欢的故事
    # me = User.query.filter_by(id=current_user.id).first()
    # my_upvote_stories = []
    # for upvote in me.upvotes:
    #     my_upvote_stories.append(upvote.story)
    my_upvote_stories = Story.query.join(
        Upvote).filter_by(user_id=current_user.id)
    my_upvote_stories = my_upvote_stories.paginate(
        page, current_app.config['FLASK_STORIES_PER_PAGE'], error_out=True)

    my_upvote_stories__son_stories = []
    for my_upvote_story in my_upvote_stories.items:
        son_stories = Story.query.filter_by(
            parent_story_id=my_upvote_story.id).order_by(Story.created.desc()).all()
        my_upvote_stories__son_stories.append((my_upvote_story, son_stories))
    return render_template('user/mine.html', stories=my_upvote_stories, page=page, my_upvote_stories__son_stories=my_upvote_stories__son_stories, my_upvote=True)


@bp.route('/create_story', methods=['GET', 'POST'])
@login_required
def create_story():
    form = StoryForm()
    if form.validate_on_submit():
        title = form.title.data.strip()
        content = form.content.data.strip()
        story = Story(user_id=current_user.id, title=title, content=content)
        db.session.add(story)
        db.session.commit()
        return redirect(url_for('user.my_stories'))
    return render_template('user/create_story.html', form=form)


@bp.route('/create_repost/<int:story_id>', methods=['GET', 'POST'])
@login_required
def create_repost(story_id):
    form = RepostStoryForm()
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
    if form.validate_on_submit():
        content = form.content.data.strip()
        new_story = Story(user_id=current_user.id, title=story.title, content=content,
                          parent_story_id=story_id, parent_stories_ids=story.parent_stories_ids + "," + str(story_id) if story.parent_stories_ids else str(story_id))
        db.session.add(new_story)
        db.session.commit()
        return redirect(url_for('user.my_stories'))
    return render_template('user/create_repost.html', form=form, stories__son_stories=stories__son_stories)


def redirect_url(default='site.index'):
    return request.args.get('next') or request.referrer or url_for(default)


@bp.route('/upvote/<int:story_id>')
@login_required
def upvote(story_id):
    upvote = Upvote.query.filter(Upvote.user_id == current_user.id).filter(
        Upvote.story_id == story_id).first()
    if not upvote:
        upvote = Upvote(user_id=current_user.id, story_id=story_id)
        db.session.add(upvote)
        db.session.commit()
        flash('成功点赞')
        return redirect(redirect_url())
    flash('已赞过')
    return redirect(redirect_url())


@bp.route('/setting/<int:user_id>', methods=['GET', 'POST'])
@login_required
def setting(user_id):
    user = User.query.filter_by(id=user_id).first()
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.email = form.email.data.strip()
        user.username = form.username.data.strip()
        db.session.add(user)
        db.session.commit()
        flash('个人信息修改成功')
        redirect(url_for('user.setting', user_id=user.id))
    return render_template('user/setting.html', form=form, user=user)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new.data.strip()
        db.session.add(current_user)
        db.session.commit()
        flash('密码修改成功')
        redirect(url_for('user.change_password'))
    return render_template('user/change_password.html', form=form)
