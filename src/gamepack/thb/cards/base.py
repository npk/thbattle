# -*- coding: utf-8 -*-
# Cards and Deck classes

from game.autoenv import Game, GameError
import random
import logging
log = logging.getLogger('THBattle_Cards')

from utils import BatchList

from .. import actions

class Card(object):
    NOTSET = 0
    SPADE = 1
    HEART = 2
    CLUB = 3
    DIAMOND = 4

    card_classes = {}

    def __init__(self, suit=NOTSET, number=0, resides_in=None):
        self.syncid = 0 # Deck will touch this
        self.suit = suit
        self.number = number
        self.resides_in = resides_in

    def __data__(self):
        return dict(
            type=self.__class__.__name__,
            suit=self.suit,
            number=self.number,
            syncid=self.syncid,
        )

    def __eq__(self, other):
        if not isinstance(other, Card): return False
        return self.syncid == other.syncid

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 84065234 + self.syncid

    def sync(self, data):
        if data['syncid'] != self.syncid:
            raise GameError('Card: out of sync')
        clsname = data['type']
        cls = Card.card_classes.get(clsname)
        if not cls: raise GameError('Card: unknown card class')
        self.__class__ = cls
        self.suit = data['suit']
        self.number = data['number']

    def move_to(self, resides_in):
        if self.resides_in is not None:
            self.resides_in.remove(self)

        if resides_in is not None:
            resides_in.append(self)

        self.resides_in = resides_in

from collections import deque

class CardList(deque):
    # performance hack
    DECKCARD = 'deckcard'
    DROPPEDCARD = 'droppedcard'
    HANDCARD = 'handcard'
    SHOWNCARD = 'showncard'
    EQUIPS = 'equips'
    FATETELL = 'fatetell'
    def __init__(self, owner, type):
        self.owner = owner
        self.type = type
        deque.__init__(self)

    def __repr__(self):
        return "CardList(owner=%s, type=%s, len([...]) == %d)" % (self.owner, self.type, len(self))

    extend = deque.extendleft
    append = deque.appendleft
    appendright = deque.append
    extendright = deque.extend

class Deck(object):
    def __init__(self):
        from .definition import card_definition
        self.cards_record = {}
        self.droppedcards = CardList(None, CardList.DROPPEDCARD)
        cards = CardList(None, CardList.DECKCARD)
        self.cards = cards
        if Game.SERVER_SIDE:
            cards.extendright(
                cls(suit, n, cards)
                for cls, suit, n in card_definition
            )
            random.shuffle(cards)
        elif Game.CLIENT_SIDE:
            self.cards.extendright(
                HiddenCard(Card.NOTSET, 0, cards)
                for i in xrange(len(card_definition))
            )

    def getcards(self, num):
        g = Game.getgame()
        rst = []

        if len(self.cards) <= num:
            if Game.SERVER_SIDE:
                # performance hack
                dropped = self.droppedcards
                random.shuffle(dropped)
                cards = self.cards
                rec = self.cards_record
                for c in dropped:
                    c.resides_in = cards
                    del rec[c.syncid]
                    c.syncid = 0
                cards.extendright(dropped)
            elif Game.CLIENT_SIDE:
                rec = self.cards_record
                for c in self.droppedcards:
                    del rec[c.syncid]
                cards = self.cards
                cards.extendright(
                    HiddenCard(Card.NOTSET, 0, cards)
                    for i in xrange(len(self.droppedcards))
                )

            self.droppedcards.clear()

        for i in xrange(num):
            c = self.cards[i]
            if not c.syncid:
                sid = g.get_synctag()
                c.syncid = sid
            rst.append(c)
            self.cards_record[sid] = c

        return rst

    def lookupcards(self, idlist):
        return [self.cards_record.get(cid) for cid in idlist]

    def shuffle(self, cl):
        g = Game.getgame()
        for c in cl:
            try:
                del self.cards_record[c.syncid]
            except KeyError:
                pass

        if Game.SERVER_SIDE:
            random.shuffle(cl)
            for c in cl:
                c.syncid = g.get_synctag()
        elif Game.CLIENT_SIDE:
            cl[:] = [HiddenCard(Card.NOTSET, 0, cl) for i in xrange(len(cl))]

class HiddenCard(Card): # special thing....
    associated_action = None
    target = None