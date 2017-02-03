# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from .. import db
from ..models import User, Meet,Permission
from ..decorators import permission_required
from flask_login import current_user
from flask import current_app


def dosomething(source, content):
    content = content.strip().lower()
    if content[:len(u"设置昵称")] == u"设置昵称":
        nickname = content[len(u"设置昵称"):].strip()
        if nickname == '':
            return '请使用 “设置昵称" + 空格 + 你想起的昵称 来设置昵称'
        user = User.query.filter_by(wechat_id=source).first()
        if user is not None:
            # 修改昵称
            if User.query.filter_by(nickname=nickname).first() is not None:
                # 已被占用，不允许重新设置
                return '此昵称已被占用=。=|||'
            else:
                # 未被占用，可以修改
                user.nickname = nickname
                db.session.add(user)
                return '昵称修改成功！'
        else:
            # 设置昵称
            if User.query.filter_by(nickname=nickname).first() is not None:
                # 已被占用，不允许重新设置
                return '此昵称已被占用=。=|||'
            else:
                user = User(nickname=nickname, wechat_id=source)
                db.session.add(user)
                return '恭喜，你的基本信息已经设置完成啦。\n' \
                       '唔，现在你可以使用面基指令进行面基啦！希望你能通过这个小小的机器人遇见更多有趣的人。有趣的灵魂终将相遇w\n' \
                       '面基指令：“meet 对方昵称”\n' \
                       '查看自己的昵称：“whoami”\n' \
                       '查询我的分数：“score” 或 “我的分数”\n' \
                       '查看排行榜: “排行榜”'

    user = User.query.filter_by(wechat_id=source).first()
    if user is None:
        return '请先使用 “设置昵称” + 空格 + 你想起的昵称 来设置昵称'

    if content[:len(u"meet")] == u"meet":
        if user.limit > 10:
            return '未被对方确认的面基申请已经超过%d条,请等待对方确认' % 10
        user_b_nickname = content[len(u"meet"):].strip()
        if user_b_nickname == '':
            return '请使用 “meet” + 空格 + 对方昵称 来确认面基～'
        user_b = User.query.filter_by(nickname=user_b_nickname).first()
        if user_b is not None:
            # 说明用户B存在
            # 先看一下有没有用户B向用户A发起的面基记录
            if user_b.nickname == user.nickname:
                return '不能和自己面基的哦～'
            meet = user_b.meet_sender.filter_by(user_affirmant_id=user.id).first()
            if meet is not None:
                if meet.confirmed:
                    return '您已经和%s面基过了呦' % user_b_nickname
                else:
                    user.score += 10
                    db.session.add(user)

                    user_b.score += 10
                    user_b.limit -= 1
                    db.session.add(user_b)

                    new_meet = Meet(sender=user, affirmant=user_b, confirmed=True)
                    db.session.add(new_meet)

                    meet.confirmed = True
                    db.session.add(meet)

                    return '与%s面基成功！各加十分！ 您现在的分数是%d' % (user_b_nickname, user.score)
            else:
                if user.meet_sender.filter_by(user_affirmant_id=user_b.id).first() is not None:
                    return '已经发送过与 %s 面基指令了，对方还没有确认～' % user_b_nickname
                new_meet = Meet(sender=user, affirmant=user_b, confirmed=False)
                db.session.add(new_meet)

                user.limit += 1
                db.session.add(user)
                return '面基记录已添加～，请让对方发送面基指令，确认后才会加分哦～'
        else:
            return '用户 %s 不存在，是不是大小写弄错了=。=||' % user_b_nickname

    elif content == u"whoami":
        return "你好，%s" % user.nickname

    elif content == u"排行榜" or content == u"phb":
        string = "Top 10"
        for q_user in User.query.order_by(User.score.desc()).limit(10).all():
            string += "\n%s, %d分" % (q_user.nickname, q_user.score)
        return string

    elif content == u"score" or content == u"我的分数":
        return '你的分数是:%d' % user.score

    return '额...本机器人智商有限，看不懂～请使用以下指令\n' \
           '面基指令：“meet 对方昵称”\n' \
           '查看自己的昵称：“whoami”\n' \
           '查询我的分数：“score” 或 “我的分数”\n' \
           '查看排行榜: “排行榜”'


# @permission_required(Permission.MEET)
