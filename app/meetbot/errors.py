# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from . import meetbot
from .views import wechat


@meetbot.app_errorhandler(403)
def permission_denied(e):
    return wechat.response_text(u"权限不够，可能是您没有管理员权限，或是您的帐号已被封禁")
