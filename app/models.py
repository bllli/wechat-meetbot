# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from . import db
from werkzeug.security import generate_password_hash, check_password_hash

from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from datetime import datetime


class Permission:
    MEET = 0x01
    MANAGE_PAGE_LOGIN = 0x04
    ADMINISTER = 0x80


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (
                Permission.MEET, True
            ),
            'Manager': (
                Permission.MEET |
                Permission.MANAGE_PAGE_LOGIN, False
            ),
            'Administer': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Meet(db.Model):
    __tablename__ = 'meets'
    user_sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user_affirmant_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    confirmed = db.Column(db.Integer, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_timestamp = db.Column(db.DateTime, default=None)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            u2 = User.query.offset(randint(0, user_count - 1)).first()
            m = Meet(sender=u,
                     affirmant=u2,
                     timestamp=forgery_py.date.date(True))
            db.session.add(m)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True)
    wechat_id = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    score = db.Column(db.Integer, index=True, default=0)
    ban = db.Column(db.Boolean, default=False)
    limit = db.Column(db.SmallInteger, default=0)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    meet_sender = db.relationship('Meet',
                                     foreign_keys=[Meet.user_sender_id],
                                     backref=db.backref('sender', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')
    meet_affirmant = db.relationship('Meet',
                                     foreign_keys=[Meet.user_affirmant_id],
                                     backref=db.backref('affirmant', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.nickname

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.nickname == current_app.config['MEETBOT_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.score is None:
            self.score = 0

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                nickname=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word(),
                score=randint(1, 200) * 10
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
