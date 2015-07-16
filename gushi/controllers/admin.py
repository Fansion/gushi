# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, request,  session, flash
from flask.ext.login import login_user, logout_user, login_required

from ..models import db, Upvote, Story, User
from ..decorators import admin_required, permission_required
from ..forms import SingleStoryForm

import datetime

bp = Blueprint('admin', __name__)


@bp.route('/audit')
@login_required
@admin_required
def audit():
    stories = Story.query.order_by(Story.created.desc())
    return render_template('auth/auth.html', stories=stories)


@bp.route('/edit/<int:story_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(story_id):
    story = Story.query.get_or_404(story_id)
    form = SingleStoryForm(obj=story)
    form.user_id.choices = [(t.id, t.username)
                            for t in User.query.order_by(User.id)]
    if form.validate_on_submit():
        story.title = form.title.data
        story.content = form.content.data
        story.user_id = form.user_id.data
        db.session.add(story)
        db.session.commit()
        return redirect(url_for('admin.audit'))
    return render_template('auth/edit.html', story=story, form=form)


@bp.route('/delete/<int:story_id>', methods=['POST'])
@login_required
@admin_required
def delete(story_id):
    story = Story.query.get_or_404(story_id)
    if story:
        for upvote in story.upvotes:
            db.session.delete(upvote)
        db.session.delete(story)
        db.session.commit()
        flash('成功删除故事')
    else:
        flash('无故事可删除')
    return redirect(url_for('admin.audit'))
