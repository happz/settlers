def __convert_resources(rs):
  rs = [int(s) for s in rs.split(',')]

  ret = games.settlers.Resources()
  ret.sheep = rs[0]
  ret.wood = rs[1]
  ret.rock = rs[2]
  ret.grain = rs[3]
  ret.clay = rs[4]

  return ret

def convert_settlers_game(r):
  orig_r = r
  orig_gid = int(r[19])

  flags = games.settlers.GameCreationFlags({
    'name':		unicode(r[0]),
    'limit':		int(r[1]),
    'turn_limit':	int(r[2]),
    'password':		(len(r[3]) > 0 and unicode(r[3]) or None),
    'desc':		unicode(r[4]),
    'kind':		unicode(r[5]),
    'dont_shuffle':	(r[6] == 'true'),
    'owner':		hruntime.dbroot.users[users_by_id[r[13]]]
  })

  g = games.settlers.Game(flags)

  g.type		= int(r[12])
  g.round		= int(r[14])
  g.forhont		= int(r[15])
  g.last_pass		= int(r[16])
  g.deleted		= (r[17] == 'true')
  g.suspended		= (r[18] == 1)
  g.card_line		= unicode(r[7])
  g.card_index		= int(r[8])
  g.dice_limit		= int(r[9])
  g.dice_line		= unicode(r[10])
  g.dice_index		= int(r[11])

  g.longest_length	= int(r[20])
  orig_lps_owner = int(r[21])

  # dice rolls
  g.dice_rolls		= hlib.database.SimpleList()
  rs = sql.query('SELECT `number` FROM `settlers_dice_rolls` WHERE `game` = %i ORDER BY `id` ASC' % orig_gid)
  for r in rs:
    g.dice_rolls.append(int(r[0]))

  # players
  rs = sql.query('SELECT `id`, `last_board`, `turns_missed`, `turns_missed_notlogged`, `confirmed`, `mightest_chilvary`, `longest_path`, `sheep`, `wood`, `rock`, `grain`, `clay`, `user` FROM `settlers_players` WHERE `game` = %i ORDER BY `id` ASC' % orig_gid)
  for r in rs:
    orig_pid = int(r[0])
    orig_uid = int(r[12])

    p = games.settlers.Player(g, hruntime.dbroot.users[users_by_id[orig_uid]])

    p.last_board	= int(r[1])
    p.turns_missed	= int(r[2])
    p.turns_missed_notlogged = int(r[3])
    p.confirmed		= (r[4] == 1)
    p.migtest_chilvary	= (r[5] == 1)
    p.longest_path	= (r[6] == 1)

    res = games.settlers.Resources()
    res.sheep	= int(r[7])
    res.wood	= int(r[8])
    res.rock	= int(r[9])
    res.grain	= int(r[10])
    res.clay	= int(r[11])

    p.resources		= res

    g.players.push(p)

  if orig_lps_owner == -1:
    g.longest_owner	= games.DummyOwner()
  else:
    g.longest_owner	= g.players[orig_lps_owner]

  # cards
  card_map = {}
  rs = sql.query('SELECT `player`, `type`, `bought`, `used`, `id` FROM `cards` WHERE `game` = %i' % orig_gid)
  for r in rs:
    c = games.settlers.Card(g, None, int(r[1]), int(r[2]))
    c.used = int(r[3])

    g.players[int(r[0])].cards.push(c)

    card_map[int(r[4])] = c

  ## Board
  board = games.settlers.Board(g, init = False)

  # Fields
  for r in sql.query('SELECT `type`, `number`, `material`, `thief` FROM `settlers_fields` WHERE `game` = %i ORDER BY `id` ASC' % orig_gid):
    f = games.settlers.BoardField(g, r[0], r[3], r[1], r[2])
    board.fields.push(f)

  # Nodes
  for r in sql.query('SELECT `type`, `owner`, `fixed` FROM `settlers_nodes` WHERE `game` = %i ORDER BY `id` ASC' % orig_gid):
    i = int(r[1])
    if i == -1:
      owner = games.DummyOwner()
    else:
      owner = g.players[i]

    n = games.settlers.BoardNode(g, r[0], owner)
    n.fixed = (r[2] == 1)
    board.nodes.push(n)

  # Paths
  for r in sql.query('SELECT `type`, `owner`, `fixed` FROM `settlers_paths` WHERE `game` = %i ORDER BY `id` ASC' % orig_gid):
    i = int(r[1])
    if i == -1:
      owner = games.DummyOwner()
    else:
      owner = g.players[i]

    p = games.settlers.BoardPath(g, r[0], owner)
    p.fixed = (r[2] == 1)
    board.paths.push(p)

  # Ports
  for r in sql.query('SELECT `clock`, `material`, `nodes` FROM `settlers_ports` WHERE `game` = %i ORDER BY `id` ASC' % orig_gid):
    p = games.settlers.BoardPort(g, int(r[0]), int(r[1]), [int(n) for n in r[2].split('|')])
    board.ports.push(p)

  g.board = board

  # events
  rs = sql.query('SELECT `id`, `type`, `stamp`, `hidden`, `game`, `tournament`, `round`, `param1`, `param2`, `param3` FROM `events` WHERE `game` = %i' % orig_gid)
  for r in rs:
    eid = int(r[1])

    if False:
      pass

    elif eid == 21:
      e = events.game.GameCreated(game = g)

    elif eid == 22:
      e = events.game.GameFinished(game = g)

    elif eid == 23:
      e = events.game.GameCanceled(game = g)

    elif eid == 24:
      e = events.game.GameStarted(game = g)

    elif eid == 25:
      e = events.game.PlayerJoined(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]])

    elif eid == 26:
      e = events.game.ChatPost(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]])

    elif eid == 27:
      e = events.game.PlayerMissed(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], logged = r[8] == '1')

    elif eid == 28:
      e = events.game.Pass(game = g, prev = hruntime.dbroot.users[users_by_id[int(r[7])]], next = hruntime.dbroot.users[users_by_id[int(r[8])]])

    elif eid == 29:
      e = events.game.PlayerInvited(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]])

    elif eid == 101:
      cid = int(r[8])
      if cid not in card_map:
        continue

      e = events.game.CardUsed(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], card = card_map[cid])

    elif eid == 102:
      cid = int(r[8])
      if cid not in card_map:
        continue

      e = events.game.CardBought(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], card = card_map[cid])

    elif eid == 103:
      e = events.game.settlers.LongestPathBonusEarned(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]])

    elif eid == 104:
      e = events.game.settlers.MightestChilvaryBonusEarned(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]])

    elif eid == 105:
      e = events.game.settlers.ResourceStolen(game = g, thief = hruntime.dbroot.users[users_by_id[int(r[8])]], victim = hruntime.dbroot.users[users_by_id[int(r[9])]], resource = int(r[7]))

    elif eid == 106:
      resources = __convert_resources(r[7])
      e = events.game.settlers.ResourcesStolen(game = g, victim = hruntime.dbroot.users[users_by_id[int(r[8])]], resources = resources)

    elif eid == 107:
      e = events.game.settlers.DiceRolled(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], dice = int(r[8]))

    elif eid == 108:
      e = events.game.settlers.VillageBuilt(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], node = g.board.nodes[int(r[8])])

    elif eid == 109:
      e = events.game.settlers.TownBuilt(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], node = g.board.nodes[int(r[8])])

    elif eid == 110:
      e = events.game.settlers.PathBuilt(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], path = g.board.paths[int(r[8])])

    elif eid == 111:
      resources = __convert_resources(r[8])
      e = events.game.settlers.ResourcesReceived(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], resources = resources)

    elif eid == 112:
      src = __convert_resources(r[8])
      dst = __convert_resources(r[9])
      e = events.game.settlers.ResourcesExchanged(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], src = src, dst = dst)

    elif eid == 113:
       resources = __convert_resources(r[9])
       e = events.game.settlers.Monopoly(game = g, thief = hruntime.dbroot.users[users_by_id[int(r[7])]], victim = hruntime.dbroot.users[users_by_id[int(r[8])]], resources = resources)

    elif eid == 114:
      e = events.game.settlers.ThiefPlaced(game = g, user = hruntime.dbroot.users[users_by_id[int(r[7])]], field = g.board.fields[int(r[8])])

    elif eid == 115:
      e = events.game.settlers.NewDiceLine(game = g)

    e.stamp = int(r[2])
    e.hidden = (int(r[3]) == 1 and True or False)

    g.events.push(e)

#  print '%i: state=%i, time diff=%i, active=%s' % (orig_gid, g.state, (hruntime.time - g.last_pass), g.is_active)

  if g.can_be_archived == True:
    hruntime.dbroot.games_archived[g.id] = g
#    print 'Game archived'
  else:
    hruntime.dbroot.games.push(g)
#    print 'Game available'

#  print g.id, g.board

def open_pb(maxval):
  return progressbar.ProgressBar(widgets = [progressbar.Percentage(), progressbar.Bar()], maxval = maxval, term_width = 80, fd = sys.stdout).start()

# Convert global chat posts
print 'Global chat posts'
r_cnt = sql.query('SELECT COUNT(*) FROM `settlers_forum`.`posts`')[0][0]
rs = sql.query("SELECT `message`, `poster`, `posted` FROM `settlers_forum`.`posts` ORDER BY `id` ASC")
pb = open_pb(r_cnt)
i = 0
for r in rs:
  convert_global_chat_post(r)

  i += 1
  pb.update(i)

print
print

commit()

# Convert Settlers games
print 'Games'
r_cnt = sql.query('SELECT COUNT(*) FROM `settlers_games`')[0][0]
#rs = sql.query('SELECT `name`, `limit`, `turn_limit`, `password`, `desc`, `kind`, `dont_shuffle`, `cardline`, `cardindex`, `dicelimit`, `diceline`, `diceindex`, `type`, `owner`, `round`, `forhont`, `last_pass`, `deleted`, `suspended`, `id`, `longest_length`, `longest_owner` FROM `settlers_games` ORDER BY `id` DESC LIMIT 0, 20')
rs = sql.query('SELECT `name`, `limit`, `turn_limit`, `password`, `desc`, `kind`, `dont_shuffle`, `cardline`, `cardindex`, `dicelimit`, `diceline`, `diceindex`, `type`, `owner`, `round`, `forhont`, `last_pass`, `deleted`, `suspended`, `id`, `longest_length`, `longest_owner` FROM `settlers_games` ORDER BY `id` DESC LIMIT 100')
#rs = [r for r in _rs]
#rs = sql.query('SELECT `name`, `limit`, `turn_limit`, `password`, `desc`, `kind`, `dont_shuffle`, `cardline`, `cardindex`, `dicelimit`, `diceline`, `diceindex`, `type`, `owner`, `round`, `forhont`, `last_pass`, `deleted`, `suspended`, `id`, `longest_length`, `longest_owner` FROM `settlers_games` WHERE `id` = 26988')
pb = open_pb(r_cnt)
i = 0
for r in rs:
  convert_settlers_game(r)

  i += 1
  pb.update(i)

  if i % 1000 == 0:
    commit()

print
print

commit()
