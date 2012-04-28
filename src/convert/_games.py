import convert

import hlib.database

import games
import games.settlers

import events.game
import events.game.settlers

# pylint: disable-msg=F0401
import hruntime

convert.map_cid_to_card = {}

def __convert_resources(rs):
  rs = [int(s) for s in rs.split(',')]

  ret = games.settlers.Resources()
  ret.sheep = rs[0]
  ret.wood = rs[1]
  ret.rock = rs[2]
  ret.grain = rs[3]
  ret.clay = rs[4]

  return ret

class ConvertDiceRolls(convert.Convertor):
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertDiceRolls, self).__init__('dice_rolls', *args, **kwargs)

  def convert_item(self, record):
    self.game.dice_rolls_append(int(record.number))

  def run(self):
    super(ConvertDiceRolls, self).run('SELECT %s FROM `settlers_dice_rolls` WHERE `game` = ' + str(self.orig_gid) + ' ORDER BY `id` ASC', ['number'])

class ConvertPlayers(convert.Convertor):
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertPlayers, self).__init__('players', *args, **kwargs)

  def convert_item(self, record):
    orig_uid = int(record.user)

    p = games.settlers.Player(self.game, convert.map_uid_to_user[orig_uid])

    p.last_board	= int(record.last_board)
    p.turns_missed	= int(record.turns_missed)
    p.turns_missed_notlogged = int(record.turns_missed_notlogged)
    p.confirmed		= (record.confirmed == 1)
    p.migtest_chilvary	= (record.mightest_chilvary == 1)
    p.longest_path	= (record.longest_path == 1)

    res = games.settlers.Resources()
    res.sheep	= int(record.sheep)
    res.wood	= int(record.wood)
    res.rock	= int(record.rock)
    res.grain	= int(record.grain)
    res.clay	= int(record.clay)

    p.resources		= res

    self.game.players.push(p)

  def run(self):
    super(ConvertPlayers, self).run('SELECT %s FROM `settlers_players` WHERE `game` = ' + str(self.orig_gid) + ' ORDER BY `id` ASC', ['id', 'last_board', 'turns_missed', 'turns_missed_notlogged', 'confirmed', 'mightest_chilvary', 'longest_path', 'sheep', 'wood', 'rock', 'grain', 'clay', 'user'])

class ConvertCards(convert.Convertor):
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertCards, self).__init__('cards', *args, **kwargs)

  def convert_item(self, record):
    c = games.settlers.Card(self.game, None, int(record.type), int(record.bought))
    c.used = int(record.used)

    self.game.players[int(record.user)].cards.push(c)

    convert.map_cid_to_card[int(record.id)] = c

  def run(self):
    super(ConvertCards, self).run('SELECT %s FROM `cards` WHERE `game` = ' + str(self.orig_gid), ['player', 'type', 'bought', 'used', 'id'])

class ConvertFields(convert.Convertor):
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertFields, self).__init__('fields', *args, **kwargs)

  def convert_item(self, record):
    f = games.settlers.BoardField(self.game, record.type, record.thief, record.number, record.material)
    self.game.board.fields.push(f)

  def run(self):
    super(ConvertFields, self).run('SELECT %s WHERE `game` = ' + str(self.orig_gid) + '  ORDER BY `id` ASC', ['type', 'number', 'material', 'thief'])

class ConvertNodes(convert.Convertor):
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertNodes, self).__init__('nodes', *args, **kwargs)

  def convert_item(self, record):
    i = int(record.owner)
    if i == -1:
      owner = games.DummyOwner()
    else:
      owner = self.game.players[i]

    n = games.settlers.BoardNode(self.game, record.type, owner)
    n.fixed = (record.fixed == 1)
    self.game.board.nodes.push(n)

  def run(self):
    super(ConvertNodes, self).run('SELECT %s FROM `settlers_nodes` WHERE `game` = ' + str(self.orig_gid) + ' ORDER BY `id` ASC', ['type', 'owner', 'fixed'])

class ConvertPaths(convert.Convertor):
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertPaths, self).__init__('paths', *args, **kwargs)

  def convert_item(self, record):
    i = int(record.owner)
    if i == -1:
      owner = games.DummyOwner()
    else:
      owner = self.game.players[i]

    p = games.settlers.BoardPath(self.game, record.type, owner)
    p.fixed = (record.fixed == 1)
    self.game.board.paths.push(p)

  def run(self):
    super(ConvertPaths, self).run('SELECT %s FROM `settlers_paths` WHERE `game` = ' + str(self.orig_gid) + ' ORDER BY `id` ASC', ['type', 'owner', 'fixed'])

class ConvertPorts(convert.Convertor): 
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertPorts, self).__init__('ports', *args, **kwargs)

  def convert_item(self, record):
    p = games.settlers.BoardPort(self.game, int(record.clock), int(record.material), [int(n) for n in record.nodes.split('|')])
    self.game.board.ports.push(p)

  def run(self):
    super(ConvertPorts, self).run('SELECT %s FROM `settlers_ports` WHERE `game` = ' + str(self.orig_gid) + ' ORDER BY `id` ASC', ['clock', 'material', 'nodes'])

class ConvertEvents(convert.Convertor):
  def __init__(self, *args, **kwargs):
    self.game = None
    self.orig_gid = None

    super(ConvertEvents, self).__init__('events', *args, **kwargs)

  def convert_item(self, record): 
    eid = int(record.type)

    U = lambda i: convert.map_uid_to_user[int(getattr(record, 'param' + str(i)))]

    if False:
      pass

    elif eid == 21:
      e = events.game.GameCreated(game = self.game)

    elif eid == 22:
      e = events.game.GameFinished(game = self.game)

    elif eid == 23:
      e = events.game.GameCanceled(game = self.game)

    elif eid == 24:
      e = events.game.GameStarted(game = self.game)

    elif eid == 25:
      e = events.game.PlayerJoined(game = self.game, user = U(1))

    elif eid == 26:
      e = events.game.ChatPost(game = self.game, user = U(1))

    elif eid == 27:
      e = events.game.PlayerMissed(game = self.game, user = U(1), logged = (record.param2 == '1'))

    elif eid == 28:
      e = events.game.Pass(game = self.game, prev = U(1), next = U(2))

    elif eid == 29:
      e = events.game.PlayerInvited(game = self.game, user = U(1))

    elif eid == 101:
      cid = int(record.param2)
      if cid not in convert.map_cid_to_card:
        return

      e = events.game.CardUsed(game = self.game, user = U(1), card = convert.map_cid_to_card[cid])

    elif eid == 102:
      cid = int(record.param2)
      if cid not in convert.map_cid_to_card:
        return

      e = events.game.CardBought(game = self.game, user = U(1), card = convert.map_cid_to_card[cid])

    elif eid == 103:
      e = events.game.settlers.LongestPathBonusEarned(game = self.game, user = U(1))

    elif eid == 104:
      e = events.game.settlers.MightestChilvaryBonusEarned(game = self.game, user = U(1))

    elif eid == 105:
      e = events.game.settlers.ResourceStolen(game = self.game, thief = U(2), victim = U(3), resource = int(record.param1))

    elif eid == 106:
      e = events.game.settlers.ResourcesStolen(game = self.game, victim = U(2), resources = __convert_resources(record.param1))

    elif eid == 107:
      e = events.game.settlers.DiceRolled(game = self.game, user = U(1), dice = int(record.param2))

    elif eid == 108:
      e = events.game.settlers.VillageBuilt(game = self.game, user = U(1), node = self.game.board.nodes[int(record.param2)])

    elif eid == 109:
      e = events.game.settlers.TownBuilt(game = self.game, user = U(1), node = self.game.board.nodes[int(record.param2)])

    elif eid == 110:
      e = events.game.settlers.PathBuilt(game = self.game, user = U(1), path = self.game.board.paths[int(record.param2)])

    elif eid == 111:
      e = events.game.settlers.ResourcesReceived(game = self.game, user = U(1), resources = __convert_resources(record.param2))

    elif eid == 112:
      src = __convert_resources(record.param2)
      dst = __convert_resources(record.param3)
      e = events.game.settlers.ResourcesExchanged(game = self.game, user = U(1), src = src, dst = dst)

    elif eid == 113:
      e = events.game.settlers.Monopoly(game = self.game, thief = U(1), victim = U(2), resources = __convert_resources(record.param3))

    elif eid == 114:
      e = events.game.settlers.ThiefPlaced(game = self.game, user = U(1), field = self.game.board.fields[int(record.param2)])

    elif eid == 115:
      e = events.game.settlers.NewDiceLine(game = self.game)

    e.stamp = int(record.stamp)
    e.hidden = (int(record.hidden) == 1 and True or False)

    self.game.events.push(e)

  def run(self):
    super(ConvertEvents, self).run('SELECT %s FROM `events` WHERE `game` = ' + str(self.orig_gid), ['id', 'type', 'stamp', 'hidden', 'game', 'tournament', 'round', 'param1', 'param2', 'param3'])

class Convertor(convert.Convertor):
  def convert_item(self, record):

    orig_gid = int(record.id)

    convert.map_cid_to_card = {}

    flags = games.settlers.GameCreationFlags({
      'name':		unicode(record.name),
      'limit':		int(record.limit),
      'turn_limit':	int(record.turn_limit),
      'password':	(len(record.password) > 0 and unicode(record.password) or None),
      'desc':		unicode(record.desc),
      'kind':		unicode(record.kind),
      'dont_shuffle':	(record.dont_shuffle == 'true'),
      'owner':		convert.map_uid_to_user[int(record.owner)]
    })

    g = games.settlers.Game(flags)

    g.type		= int(record.type)
    g.round		= int(record.round)
    g.forhont		= int(record.forhont)
    g.last_pass		= int(record.last_pass)
    g.deleted		= (record.deleted == 'true')
    g.suspended		= (record.suspended == 1)
    g.card_line		= unicode(record.cardline)
    g.card_index	= int(record.cardindex)
    g.dice_limit	= int(record.dicelimit)
    g.dice_line		= unicode(record.diceline)
    g.dice_index	= int(record.diceindex)

    g.longest_length	= int(record.longest_length)
    orig_lps_owner = int(record.longest_owner)

    # dice rolls
    g.dice_rolls = hlib.database.SimpleList()
    c = ConvertDiceRolls(self.db, game = g, orig_gid = orig_gid)
    c.run()

    # players
    c = ConvertPlayers(self.db, game = g, orig_gid = orig_gid)
    c.run()

    if orig_lps_owner == -1:
      g.longest_owner = games.DummyOwner()
    else:
      g.longest_owner = g.players[orig_lps_owner]

    # cards
    c = ConvertCards(self.db, game = g, orig_gid = orig_gid)
    c.run()

    # board
    g.board = games.settlers.Board(g, init = False)

    # fields
    c = ConvertFields(self.db, game = g, orig_gid = orig_gid)
    c.run()

    # nodes
    c = ConvertNodes(self.db, game = g, orig_gid = orig_gid)
    c.run()

    # paths
    c = ConvertPaths(self.db, game = g, orig_gid = orig_gid)
    c.run()

    # ports
    c = ConvertPorts(self.db, game = g, orig_gid = orig_gid)
    c.run()

    # events
    c = ConvertEvents(self.db, game = g, orig_gid = orig_gid)
    c.run()

    if g.can_be_archived == True:
      hruntime.dbroot.games_archived[g.id] = g

    else:
      hruntime.dbroot.games.push(g)

  def run(self):
    super(Convertor, self).run('SELECT %s FROM `settlers_games` ORDER BY `id` DESC LIMIT 100', ['name', 'limit', 'turn_limit', 'password', 'desc', 'kind', 'dont_shuffle', 'cardline', 'cardindex', 'dicelimit', 'diceline', 'diceindex', 'type', 'owner', 'round', 'forhont', 'last_pass', 'deleted', 'suspended', 'id', 'longest_length', 'longest_owner'])

convert.CONVERTORS['games'] = Convertor
