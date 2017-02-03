# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import redirect, session, url_for, render_template, flash, abort, request

from . import main, forms
from .. import db
from ..models import User, Permission, Meet
from ..decorators import permission_required
from flask_login import login_required


@main.route('/', methods=['POST', 'GET'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.score.desc()).paginate(page, per_page=50, error_out=False)
    users = pagination.items
    return render_template('index.html', users=users, pagination=pagination)


@main.route('/user/<nickname>')
@login_required
@permission_required(Permission.MANAGE_PAGE_LOGIN)
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        abort(404)
    # meet_logs = Meet.query.order_by(Meet.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)

    pagination = user.meet_sender.order_by(Meet.timestamp.desc()).paginate(page, per_page=50, error_out=False)
    meet_logs = pagination.items
    return render_template('user.html', user=user, meet_logs=meet_logs, pagination=pagination)
