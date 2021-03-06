# -*- coding: utf-8 -*-

from gamepack.thb import actions
from gamepack.thb import characters
from gamepack.thb.ui.ui_meta.common import gen_metafunc
from gamepack.thb.ui.ui_meta.common import passive_clickable, passive_is_action_valid
from gamepack.thb.ui.ui_meta.common import limit1_skill_used
from gamepack.thb.ui.resource import resource as gres

__metaclass__ = gen_metafunc(characters.rumia)


class Darkness:
    # Skill
    name = u'黑暗'
    custom_ray = True

    def clickable(game):
        try:
            if limit1_skill_used('darkness_tag'):
                return False
            act = game.action_stack[-1]
            if isinstance(act, actions.ActionStage):
                return True
        except IndexError:
            pass
        return False

    def is_action_valid(g, cl, tl):
        skill = cl[0]
        cl = skill.associated_cards
        if not cl or len(cl) != 1:
            return (False, u'请选择一张牌')

        if not len(tl):
            return (False, u'请选择第一名玩家（先出弹幕）')
        elif len(tl) == 1:
            return (False, u'请选择第二名玩家（后出弹幕）')
        else:
            return (True, u'你们的关系…是~这样吗？')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return u'|G【%s】|r在黑暗中一通乱搅，结果|G【%s】|r和|G【%s】|r打了起来！' % (
            act.source.ui_meta.char_name,
            act.target_list[0].ui_meta.char_name,
            act.target_list[1].ui_meta.char_name,
        )


class DarknessAction:
    def ray(act):
        src = act.source
        tl = act.target_list
        return [(src, tl[1]), (tl[1], tl[0])]


class Cheating:
    # Skill
    name = u'作弊'
    clickable = passive_clickable
    is_action_valid = passive_is_action_valid


class CheatingDrawCards:
    def effect_string(act):
        return u'突然不知道是谁把太阳挡住了。等到大家回过神来，赫然发现牌堆里少了一张牌！'


class Rumia:
    # Character
    char_name = u'露米娅'
    port_image = gres.rumia_port
    description = (
        u'|DB宵暗的妖怪 露米娅 体力：3|r\n\n'
        u'|G黑暗|r：出牌阶段，你可以弃一张牌并选择除你以外的两名角色。若如此做，视为由你选择的其中一名角色对另一名角色使用一张【弹幕战】。额外的，此【弹幕战】属于人物技能，不是符卡效果。\n\n'
        u'|G作弊|r：弃牌阶段后，你摸一张牌。'
    )
