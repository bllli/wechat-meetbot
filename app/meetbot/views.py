# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.messages import *
from wechat_sdk.exceptions import ParseError
from flask import template_rendered, redirect, request, url_for


conf = WechatConf(
    token='your token',
    appid='your appid',
    appsecret='your appsecret',
    encrypt_mode='your mode',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key='your aes key'  # 如果传入此值则必须保证同时传入 token, appid
)

wechat = WechatBasic(conf=conf)

from . import meetbot
from .doSometing import dosomething
from ..models import User
from flask_login import login_user
from pymysql.err import OperationalError


@meetbot.route('/wechatInterface', methods=['POST', 'GET'])
def meetbot():
    if request.method == 'GET':
        items = request.args.items()
        d = dict(items)
        try:
            signature = str(d['signature']).encode('utf-8')
            timestamp = str(d['timestamp']).encode('utf-8')
            nonce = str(d['nonce']).encode('utf-8')
            echostr = str(d['echostr']).encode('utf-8')
        except KeyError:
            return 'err', 500
        if wechat.check_signature(signature, timestamp, nonce):
            return echostr
        else:
            return 'Too simple!', 500

    if request.method == 'POST':
        items = request.args.items()
        d = dict(items)
        try:
            signature = str(d['signature']).encode('utf-8')
            timestamp = str(d['timestamp']).encode('utf-8')
            nonce = str(d['nonce']).encode('utf-8')
        except KeyError:
            return 'err', 500
        if wechat.check_signature(signature, timestamp, nonce):
            try:
                wechat.parse_data(request.get_data())
            except ParseError:
                print('Invalid Body Text')
                return wechat.response_text(content=u'服务器提了一个错误')
            source = wechat.message.source
            try:
                user = User.query.filter_by(wechat_id=source).first()
            except:
                try:
                    user = User.query.filter_by(wechat_id=source).first()
                except :
                    return wechat.response_text(content="服务器提了一个小错误，请尝试再发送一次")
            if user is not None:
                login_user(user, False)
            if isinstance(wechat.message, TextMessage):
                content = wechat.message.content.strip()
                response = dosomething(source, content)
                return wechat.response_text(content=response)
            if isinstance(wechat.message, EventMessage):
                if wechat.message.type == 'subscribe':
                    return wechat.response_text(content='嗨，欢迎使用Fc动漫音乐节的面基机器人。请按照以下提示设置你的基本信息：\n'
                                                        '设置昵称:"设置昵称 你的CN"')
            return wechat.response_text(content='本宝宝看不懂你发的是啥～\n' \
                                                '面基指令：“meet 对方昵称”\n' \
                                                '查看自己的昵称：“whoami”\n' \
                                                '查询我的分数：“score” 或 “我的分数”\n' \
                                                '查看排行榜: “排行榜”'
                                        )
        else:
            return 'Sometimes naive.', 500
