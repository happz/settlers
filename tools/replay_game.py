#!/usr/bin/python -W ignore:the:DeprecationWarning:MySQLdb:34

import games.settlers
import lib.env
import lib.event
import sys

import lib.events.game.settlers

def rc_add(src, dst):
  prev = rc_copy(dst)

  for k in dst.keys():
    dst[k] = dst[k] + src[k]

  return prev

def rc_sub(src, dst):
  prev = rc_copy(dst)

  for k in dst.keys():
    dst[k] = dst[k] - src[k]

  return prev

def rc_copy(src):
  return games.settlers.ResourceContainer(wood = src.wood, rock = src.rock, grain = src.grain, sheep = src.sheep, clay = src.clay)

def rc_str(rc):
  return '%i,%i,%i,%i,%i' % (rc.wood, rc.clay, rc.sheep, rc.grain, rc.rock)

CONFIG = sys.argv[1]
GID = int(sys.argv[2])

db_session = lib.env.init_env(CONFIG)

game = games.settlers.Game(games.settlers.GameRecord.load_from_db(GID))

players = {}
for i in range(0, game.limit):
  players[game.players[i].user.id] = {'name': game.players[i].user.name, 'resources': games.settlers.ResourceContainer()}

cards = {}

events = lib.event.history(game.id, hidden = None)
events.reverse()

building_free_paths = False

for event in events:
  def pr_gse(msg, rc_prev = None, rc_new = None):
    actor = None
    actee = None

    if hasattr(event, 'user'):
      actor = event.user.name
    elif hasattr(event, 'thief'):
      actor = event.thief.name
    else:
      actor = '<system>'

    m = []
    m.append('%3i' % event.round)
    m.append('%15s' % actor)

    if rc_prev != None:
      m.append('%12s' % rc_str(rc_prev))
    if rc_new != None:
      m.append('%12s' % rc_str(rc_new))

    m.append(msg)

    print ' | '.join(m)

  if     event.type != lib.events.game.settlers.SettlersEvent.PATH_BUILT \
     and event.type != lib.events.game.settlers.SettlersEvent.LONGEST_PATH_BONUS_EARNED:
    building_free_paths = False

  if event.type == lib.events.game.settlers.SettlersEvent.CARD_USED:
    cards[event.card.id] = True
    pr_gse('Used card, id %i' % event.card.id)

    if event.card.type == games.settlers.Card.TYPE_ROADS:
      building_free_paths = True

  elif event.type == lib.events.game.settlers.SettlersEvent.CARD_BOUGHT:
    cards[event.card.id] = False
    rc_prev = rc_sub(games.settlers.ResourceContainer(grain = 1, sheep = 1, rock = 1), players[event.user.id]['resources'])

    pr_gse('Bought card, id %i, type %s' % (event.card.id, games.settlers.Card.map_card2str[event.card.type]), rc_prev = rc_prev, rc_new = players[event.user.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.LONGEST_PATH_BONUS_EARNED:
    pr_gse('Earned path bonus')

  elif event.type == lib.events.game.settlers.SettlersEvent.MIGHTEST_CHILVARY_BONUS_EARNED:
    pr_gse('Earned chilvary bonus')

  elif event.type == lib.events.game.settlers.SettlersEvent.RESOURCE_STOLEN:
    r = games.settlers.ResourceContainer()
    r[event.resource] = 1

    rc_prev_victim = rc_sub(r, players[event.victim.id]['resources'])
    rc_prev_thief  = rc_add(r, players[event.thief.id]['resources'])

    pr_gse('Stolen resources: victim: %15s, resources: %s' % (event.victim.name, rc_str(r)), rc_prev = rc_prev_victim, rc_new = players[event.victim.id]['resources'])
    pr_gse('Stolen resources: thief:  %15s, resources: %s' % (event.victim.name, rc_str(r)), rc_prev = rc_prev_thief, rc_new = players[event.thief.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.RESOURCES_STOLEN:
    rc_prev = rc_sub(event.resources, players[event.victim.id]['resources'])

    pr_gse('Stolen resources: victim: %15s, resources: %s' % (event.victim.name, rc_str(event.resources)), rc_prev = rc_prev, rc_new = players[event.victim.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.DICE_ROLLED:
    pr_gse('Dice rolled: %i' % event.dice)

  elif event.type == lib.events.game.settlers.SettlersEvent.VILLAGE_BUILT:
    rc_prev = rc_sub(games.settlers.ResourceContainer(wood = 1, clay = 1, grain = 1, sheep = 1), players[event.user.id]['resources'])
    pr_gse('Build village', rc_prev = rc_prev, rc_new = players[event.user.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.TOWN_BUILT:
    rc_prev = rc_sub(games.settlers.ResourceContainer(grain = 2, rock = 3), players[event.user.id]['resources'])
    pr_gse('Build town', rc_prev = rc_prev, rc_new = players[event.user.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.PATH_BUILT:
    if building_free_paths == True:
      rc_prev = rc_copy(players[event.user.id]['resources'])
    else:
      rc_prev = rc_sub(games.settlers.ResourceContainer(wood = 1, clay = 1), players[event.user.id]['resources'])
    pr_gse('Build path', rc_prev = rc_prev, rc_new = players[event.user.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.RESOURCES_RECEIVED:
    rc_prev = rc_add(event.resources, players[event.user.id]['resources'])
    pr_gse('Received resources: %s' % rc_str(event.resources), rc_prev = rc_prev, rc_new = players[event.user.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.RESOURCES_EXCHANGED:
    rc_prev = rc_copy(players[event.user.id]['resources'])
    rc_sub(event.src, players[event.user.id]['resources'])
    rc_add(event.dst, players[event.user.id]['resources'])
    pr_gse('Exchanged resources: %s -> %s' % (rc_str(event.src), rc_str(event.dst)), rc_prev = rc_prev, rc_new = players[event.user.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.MONOPOLY:
    rc_prev_victim = rc_sub(event.resources, players[event.victim.id]['resources'])
    rc_prev_thief  = rc_add(event.resources, players[event.thief.id]['resources'])

    pr_gse('Stolen resources: victim: %15s, resources: %s' % (event.victim.name, rc_str(r)), rc_prev = rc_prev_victim, rc_new = players[event.victim.id]['resources'])
    pr_gse('Stolen resources: thief:  %15s, resources: %s' % (event.victim.name, rc_str(r)), rc_prev = rc_prev_thief, rc_new = players[event.thief.id]['resources'])

  elif event.type == lib.events.game.settlers.SettlersEvent.THIEF_PLACED:
    pass

  elif event.type == lib.events.game.settlers.SettlersEvent.NEW_DICE_LINE:
    pass

print '-- -- -- -- -- -- -- --'

for p in game.players.itervalues():
  print '%10s: %s' % (p.user.name, rc_str(p.resources))
  print '          : %s' % (rc_str(players[p.user.id]['resources']))
