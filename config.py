# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    wechat_token = os.environ.get('wechat_token')
    wechat_appid = os.environ.get('wechat_appid')
    wechat_appsecret = os.environ.get('wechat_appsecret')
    wechat_encoding_aes_key = os.environ.get('wechat_encoding_aes_key')

    SECRET_KEY = 'ajsbdfkbk23briupHP*(T(*Yiug3br'  # 此处需要脸滚键盘
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MEETBOT_ADMIN = os.environ.get('MEETBOT_ADMIN') or 'bllli'  # 修改为你自己的

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'date-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@url:port/datebase'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}