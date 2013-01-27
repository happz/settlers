import cPickle
import math
import random
import types

import hlib
import lib.datalayer
import hlib.log
import games
import games.settlers.board_def

import hlib.api
import hlib.engine
import hlib.event

import games.color

# pylint: disable-msg=F0401
import hruntime

InactivePathError		= lambda: games.GameError(msg = 'This path is not active right now', reply_status = 402)
InactiveNodeError		= lambda: games.GameError(msg = 'This node is not active right now', reply_status = 402)
InactiveNumberError		= lambda: games.GameError(msg = 'This number is not active right now', reply_status = 402)
TooManyVillagesError		= lambda: games.GameError(msg = 'You have too many villages', reply_status = 403)
TooManyTownsError		= lambda: games.GameError(msg = 'You have too many towns', reply_status = 403)
TooManyPathsError		= lambda: games.GameError(msg = 'You have too many paths', reply_status = 403)
NotEnoughPointCardsError	= lambda: games.GameError(msg = 'You can not use Point cards yet', reply_status = 402)

class ApiBoard(hlib.api.ApiJSON):
  def __init__(self, b):
    super(ApiBoard, self).__init__(['fields', 'nodes', 'paths', 'ports'])

    f = lambda n: [_x.to_api() for _x in getattr(b, n).values()]

    self.fields = f('fields')
    self.nodes  = f('nodes')
    self.paths  = f('paths')
    self.ports  = f('ports')

class Resource(games.Resource):
  RESOURCE_SHEEP   =  0
  RESOURCE_WOOD    =  1
  RESOURCE_ROCK    =  2
  RESOURCE_GRAIN   =  3
  RESOURCE_CLAY    =  4
  RESOURCE_DESERT  =  5

  RESOURCE_MIN     =  0
  RESOURCE_MAX     =  4

  map_resource2str = {-2: 'free',
                      -1: 'unknown',
                       0: 'sheep',
                       1: 'wood',
                       2: 'rock',
                       3: 'grain',
                       4: 'clay',
                       5: 'desert'
                      }

  map_str2resource = {'free':    -2,
                      'unknown': -1,
                      'sheep':    0,
                      'wood':     1,
                      'rock':     2,
                      'grain':    3,
                      'clay':     4,
                      'desert':   5
                     }

class Resources(games.Resources):
  def __init__(self):
    games.Resources.__init__(self)

    self.sheep = 0
    self.wood  = 0
    self.rock  = 0
    self.grain = 0
    self.clay  = 0

  def __len__(self):
    # pylint: disable-msg=R0201
    return 5

  def __getitem__(self, key):
    if type(key) in [types.IntType, types.LongType]:
      key = Resource.map_resource2str[key]

    return getattr(self, key)

  def __setitem__(self, key, value):
    if type(key) == types.IntType:
      key = Resource.map_resource2str[key]

    setattr(self, key, value)

  def keys(self):
    # pylint: disable-msg=R0201
    return ['wood', 'sheep', 'rock', 'grain', 'clay']

  def values(self):
    return [self.sheep, self.wood, self.rock, self.grain, self.clay]

  def max(self):
    return max(self.values())

class Player(games.Player):
  def __init__(self, game, user):
    games.Player.__init__(self, game, user)

    self.resources	= Resources()
    self.cards		= hlib.database.IndexedMapping()
    self.mightest_chilvary	= False
    self.longest_path	= False

    self.first_village	= None
    self.second_village	= None

  def __getattr__(self, name):
    if name == 'points':
      p = 0

      for n in self.game.board.get_used_nodes(player = self):
        if n.type == BoardNode.TYPE_VILLAGE:
          p += 1

        else:
          p += 2

      for c in self.cards.values():
        if c.type == Card.TYPE_POINT and c.is_used:
          p += 1

      if self.mightest_chilvary:
        p += 2

      if self.longest_path:
        p += 2

      return p

    if name == 'is_on_game':
      return self.game.type == Game.TYPE_GAME and self.is_on_turn

    if name == 'has_free_path':
      return len(self.game.board.get_used_paths(player = self)) < 15

    if name == 'has_free_village':
      return len([n for n in self.game.board.get_used_nodes(player = self) if n.type == BoardNode.TYPE_VILLAGE]) < 5

    if name == 'has_free_town':
      return len([n for n in self.game.board.get_used_nodes(player = self) if n.type == BoardNode.TYPE_TOWN]) < 4

    if name == 'can_roll_dice':
      return self.is_on_turn and self.game.type in [Game.TYPE_PREPARE_DICE, Game.TYPE_PREPARE_KNIGHT]

    if name == 'can_pass':
      if not self.is_on_turn:
        return False

      if self.game.type in [Game.TYPE_FREE, Game.TYPE_FINISHED, Game.TYPE_CANCELED]:
        return False

      if self.game.type == Game.TYPE_PLACE_FIRST:
        if len(self.game.board.get_used_nodes(player = self)) != 1 or len(self.game.board.get_used_paths(player = self)) != 1:
          return False
        return True

      if self.game.type == Game.TYPE_PLACE_SECOND:
        if len(self.game.board.get_used_nodes(player = self)) != 2 or len(self.game.board.get_used_paths(player = self)) != 2:
          return False
        return True

      if self.game.type == Game.TYPE_GAME:
        return True

      return False

    return games.Player.__getattr__(self, name)

  def to_state(self):
    d = games.Player.to_state(self)

    d.update({
      'points':			self.points,
      'has_longest_path':	self.longest_path,
      'has_mightest_chilvary':	self.mightest_chilvary,
      'can_roll_dice':		self.can_roll_dice,
      'first_village':		self.first_village and self.first_village.id or None,
      'second_village':		self.second_village and self.second_village.id or None,
      'resources':		{
        'total':		sum(self.resources.values())
      },
      'cards':			{
        'unused_cards':		len([c for c in self.cards.values() if c.is_used != True]),
        'used_knights':		len([c for c in self.cards.values() if c.type == Card.TYPE_KNIGHT and c.is_used])
      }
    })

    if self.id == self.game.my_player.id:
      d['cards']['cards'] = [c.to_api() for c in self.cards.values()]

      for k in self.resources.keys():
        d['resources'][k] = self.resources[k]

    return d

  def add_resource(self, node, field):
    if field.resource == Resource.RESOURCE_DESERT:
      return None

    if node.type == BoardNode.TYPE_VILLAGE:
      amount = 1
    else:
      amount = 2

    self.add_resource_raw(field.resource, amount)

    return (field.resource, amount)

  def apply_thief_to_full(self):
    if self.resources.sum() <= 0:
      return

    stolen = Resources()
    howmany = int(math.ceil(self.resources.sum() / 2))

    # pylint: disable-msg=W0612
    for i in range(howmany):
      while True:
        r = random.randint(Resource.RESOURCE_MIN, Resource.RESOURCE_MAX)

        if self.resources[r] > 0:
          break

      self.resources[r] -= 1
      stolen[r] += 1

    hlib.event.trigger('game.settlers.ResourcesStolen', self.game, game = self.game, resources = stolen, victim = self.user)

  def apply_thief_to_one(self, thief):
    if self.resources.sum() <= 0:
      return

    while True:
      r = random.randint(Resource.RESOURCE_MIN, Resource.RESOURCE_MAX)

      if self.resources[r] > 0:
        break

    self.resources[r] -= 1
    thief.add_resource_raw(r, 1)

    hlib.event.trigger('game.settlers.ResourceStolen', self.game, game = self.game, resource = r, thief = thief.user, victim = self.user)

  def exchange_resources(self, t, src, dst, pieces):
    if not self.is_on_game:
      raise games.NotYourTurnError()

    if src == dst:
      raise games.GameError(msg = 'You can not exchange resources for the same one')

    if self.resources[src] < pieces:
      raise games.NotEnoughResourcesError()

    if t == Game.RESOURCE_EXCHANGE_FOUR:
      k = 4

    elif t == Game.RESOURCE_EXCHANGE_THREE:
      k = 3
      if len(self.game.board.get_used_ports(self, Resource.RESOURCE_FREE)) <= 0:
        raise games.GameError(msg = 'You have no access to free port')

    elif t == Game.RESOURCE_EXCHANGE_TWO:
      k = 2
      if len(self.game.board.get_used_ports(self, src)) <= 0:
        raise games.GameError(msg = 'You have no access to this resource port')

    else:
      raise games.GameError(msg = 'Unknown exchange type')

    if pieces % k:
      raise games.GameError(msg = 'This is not valid number')

    self.resources[src] -= pieces
    self.resources[dst] += (pieces / k)

    src_c = Resources()
    src_c[src] = pieces
    dst_c = Resources()
    dst_c[dst] = (pieces / k)

    hlib.event.trigger('game.settlers.ResourcesExchanged', self.game, game = self.game, user = self.user, src = src_c, dst = dst_c)

  def apply_monopoly(self, thief, resource):
    amount = self.resources[resource]
    self.resources[resource] = 0
    thief.add_resource_raw(resource, amount)

    rc = Resources()
    rc[resource] = amount
    hlib.event.trigger('game.settlers.Monopoly', self.game, game = self.game, thief = thief.user, victim = self.user, resources = rc)

  def exchange_has_any_common(self):
    return self.game.type == games.Game.TYPE_GAME

  def exchange_four_has_any(self):
    if not self.exchange_has_any_common():
      return False

    return max(self.resources.values() >= 4)

  def exchange_three_has_any(self):
    if not self.exchange_has_any_common():
      return False

    return max(self.resources.values() >= 3) and len(self.game.board.get_used_ports(self, Resource.RESOURCE_FREE))

  def exchange_two_has_any(self):
    if not self.exchange_has_any_common():
      return False

    for k in self.resources.keys():
      if self.resources[k] >= 2 and len(self.game.board.get_used_ports(self, k)) > 0:
        return True

    return False

  def exchange_has_any(self):
    return (self.exchange_four_has_any() or self.exchange_three_has_any() or self.exchange_two_has_any())

class BoardField(hlib.database.DBObject):
  TYPE_UNKNOWN  = 0
  TYPE_SEA      = 1
  TYPE_DESERT   = 2
  TYPE_RESOURCE = 3

  map_type2str = {0: 'unknown',
                  1: 'sea',
                  2: 'desert',
                  3: 'resource'
                 }

  def __init__(self, game, typ, thief, number, resource):
    hlib.database.DBObject.__init__(self)

    self.game		= game
    self.id		= None
    self.type		= int(typ)
    self.number		= int(number)
    self.resource	= int(resource)
    self.thief		= bool(thief)

  def to_api(self):
    return {
      'id':		self.id,
      'type':		self.type,
      'number':		self.number,
      'resource':	self.resource,
      'thief':		self.thief
    }

class BoardPort(hlib.database.DBObject):
  def __init__(self, game, clock, resource, nodes):
    hlib.database.DBObject.__init__(self)

    self.game		= game
    self.id		= None
    self.clock		= clock
    self.resource	= resource
    self.nodes		= nodes

  def to_api(self):
    return {
      'id':		self.id,
      'clock':		self.clock,
      'resource':	self.resource,
      'nodes':		self.nodes
    }

class BoardPath(games.OwnerableDBObject):
  TYPE_FREE   = 1
  TYPE_OWNED  = 2

  POSITION_LT = 1
  POSITION_T  = 2
  POSITION_RT = 3
  POSITION_RB = 4
  POSITION_B  = 5
  POSITION_LB = 6

  map_pos2str = {1: 'lt',
                 2:  't',
                 3: 'rt',
                 4: 'lt',
                 5:  't',
                 6: 'rt'
                }

  def __init__(self, game, typ, owner):
    games.OwnerableDBObject.__init__(self, game, typ, owner)

    self._v_mark	= False

  def __getattr__(self, name):
    if name == '_v_mark':
      setattr(self, '_v_mark', False)
      return False

class BoardNode(games.OwnerableDBObject):
  TYPE_FREE    = 1
  TYPE_VILLAGE = 2
  TYPE_TOWN    = 3

  map_type2str = {1: 'free',
                  2: 'village',
                  3: 'town'}

class Card(games.Card):
  TYPE_KNIGHT    = 1
  TYPE_MONOPOLY  = 2
  TYPE_ROADS     = 3
  TYPE_INVENTION = 4
  TYPE_POINT     = 5

  map_card2str = {1: 'knight',
                  2: 'monopoly',
                  3: 'roads',
                  4: 'invention',
                  5: 'point'}

  def __getattr__(self, name):
    if name == 'can_be_used':
      if self.is_used:
        return False

      if not self.player.is_on_turn:
        return False

      if not self.player.is_on_game and self.type != Card.TYPE_KNIGHT:
        return False

      if not self.game.type in [Game.TYPE_PREPARE_KNIGHT, Game.TYPE_GAME]:
        return False

      if self.game.round == self.bought:
        return False

      for card in self.player.cards.values():
        if card.used == self.game.round:
          return False

      return True

    return games.Card.__getattr__(self, name)

COLOR_SPACE = games.color.ColorSpace('settlers', colors = [
  ('red', games.color.Color('red', 'Red', '#CC0000')),
  ('pink', games.color.Color('pink', 'Pink', '#DD21D4')),
  ('black', games.color.Color('black', 'Black', '#000000')),
  ('green', games.color.Color('green', 'Green', '#33FF00')),
  ('purple', games.color.Color('purple', 'Purple', '#990099')),
  ('dark_blue', games.color.Color('dark_blue', 'Dark blue', '#000099')),
  ('brown', games.color.Color('brown', 'Brown', '#663300')),
  ('dark_green', games.color.Color('dark_green', 'Dark green', '#347235')),
  ('orange', games.color.Color('orange', 'Orange', '#FF9900')),
  ('light_blue', games.color.Color('light_blue', 'Light blue', '#00CCCC'))
])

class Board(games.Board):
  # pylint: disable-msg=R0904

  COLORS = {1: ['#CC0000', 'red'],
            2: ['#FF9900', 'orange'],
            3: ['#DD21D4', 'pink'],
            4: ['#000000', 'black'],
            5: ['#33FF00', 'green'],
            6: ['#990099', 'purple'],
            7: ['#00CCCC', 'light_blue'],
            8: ['#000099', 'dark_blue'],
            9: ['#663300', 'brown'],
            10: ['#347235', 'dark_green']
           }

  def __init__(self, game, init = True):
    games.Board.__init__(self, game)

    self.fields = hlib.database.IndexedMapping(first_key = 1)
    self.nodes  = hlib.database.IndexedMapping(first_key = 1)
    self.paths  = hlib.database.IndexedMapping(first_key = 1)
    self.ports  = hlib.database.IndexedMapping()

    self.lps_length = -1
    self.lps_counter = 0
    self.lps_owner = 0
    self.lps_multi = False

    if not init:
      return

    self.init()

  def init(self):
    # create ports
    resources = [Resource.RESOURCE_SHEEP, Resource.RESOURCE_WOOD, Resource.RESOURCE_ROCK, Resource.RESOURCE_GRAIN, Resource.RESOURCE_CLAY]
    random.shuffle(resources)

    free_ports = 4

    free = random.randrange(0, 2)
    if free == 1:
      free = True
    else:
      free = False

    for desc in games.settlers.board_def.PORT_DESCS:
      if desc == []:
        continue

      if free and free_ports > 0:
        resource = Resource.RESOURCE_FREE
        free_ports -= 1
      else:
        resource = resources.pop(0)

      if len(desc['clock']) == 1:
        clock = desc['clock'][0]
        nodes = desc['nodes'][0]
      else:
        j = random.randrange(0, 2)
        clock = desc['clock'][j]
        nodes = desc['nodes'][j]

      free = not free

      self.ports.push(BoardPort(self.game, clock, resource, nodes))

    # create fields
    resources = [Resource.RESOURCE_SHEEP,
                 Resource.RESOURCE_SHEEP,
                 Resource.RESOURCE_SHEEP,
                 Resource.RESOURCE_SHEEP,
                 Resource.RESOURCE_ROCK,
                 Resource.RESOURCE_ROCK,
                 Resource.RESOURCE_ROCK,
                 Resource.RESOURCE_CLAY,
                 Resource.RESOURCE_CLAY,
                 Resource.RESOURCE_CLAY,
                 Resource.RESOURCE_WOOD,
                 Resource.RESOURCE_WOOD,
                 Resource.RESOURCE_WOOD,
                 Resource.RESOURCE_WOOD,
                 Resource.RESOURCE_GRAIN,
                 Resource.RESOURCE_GRAIN,
                 Resource.RESOURCE_GRAIN,
                 Resource.RESOURCE_GRAIN]

    if self.game.flags.floating_desert == True:
      resources.append(Resource.RESOURCE_DESERT)

    numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

    random.shuffle(resources)
    random.shuffle(numbers)

    for i in range(1, 20):
      if self.game.flags.floating_desert != True:
        if i == 10:
          field = (BoardField.TYPE_DESERT, 1, 7, Resource.RESOURCE_DESERT)
        else:
          field = (BoardField.TYPE_RESOURCE, 0, numbers.pop(0), resources.pop(0))
      else:
        resource = resources.pop(0)

        if resource == Resource.RESOURCE_DESERT:
          field = (BoardField.TYPE_DESERT, 1, 7, resource)
        else:
          field = (BoardField.TYPE_RESOURCE, 0, numbers.pop(0), resource)

      self.fields.push(BoardField(self.game, field[0], field[1], field[2], field[3]))

    for i in range(1, 55):
      self.nodes.push(BoardNode(self, BoardNode.TYPE_FREE, games.DummyOwner()))

    for i in range(1, 73):
      self.paths.push(BoardPath(self, BoardPath.TYPE_FREE, games.DummyOwner()))

    self.render_preview()

  def __getattr__(self, name):
    if name == 'thief_field':
      for f in self.fields.values():
        if f.thief:
          return f

      raise games.GameError(msg = 'This game has no thief?')

    if name == 'free_numbers_map':
      return dict([(f.id, f.thief != True) for f in self.fields.values()])

    return games.Board.__getattr__(self, name)

  def render_preview(self):
    import PIL.Image
    import ImageDraw

    offset = (59 + 29, 102)

    preview = PIL.Image.new('RGBA', (645, 714), (255, 255, 255, 255))
    preview_draw = ImageDraw.Draw(preview)

    save_info = None

    for field in self.fields.values():
      field_img = PIL.Image.open('../static/images/games/settlers/board/real/field/' + Resource.map_resource2str[field.resource] + '.gif')
      field_img_conv = field_img.convert('RGBA')

      if not save_info:
        save_info = field_img_conv.info

      preview.paste(field_img_conv, (int(board_def.COORS['field'][field.id][0]) + offset[0], int(board_def.COORS['field'][field.id][1]) + offset[1]), field_img_conv)

    for sea in board_def.COORS['sea'].values():
      sea_img = PIL.Image.open('../static/images/games/settlers/board/real/field/sea.gif')
      sea_img_conv = sea_img.convert('RGBA')
      preview.paste(sea_img_conv, (int(sea[0]) + offset[0], int(sea[1]) + offset[1]), sea_img_conv)

    del preview_draw

    preview = preview.resize((161, 178))
    preview.save('../static/images/gamepreview/' + str(self.game.id) + '.gif', 'GIF', transparency = 255)

  def active_nodes_map(self, player = None):
    player = player or self.game.my_player

    if not player or not player.is_on_turn:
      return active_nodes_map_negative

    if self.game.type in [Game.TYPE_USE_KNIGHT,       Game.TYPE_USE_KNIGHT_GAME,   Game.TYPE_FREE,
                          Game.TYPE_FREE_PATHS_FIRST, Game.TYPE_FREE_PATHS_SECOND, Game.TYPE_FINISHED,
                          Game.TYPE_PREPARE_THIEF,    Game.TYPE_PREPARE_DICE,      Game.TYPE_PREPARE_KNIGHT,
                          Game.TYPE_FREE_RESOURCES,   Game.TYPE_MONOPOLY,          Game.TYPE_CANCELED]:
      return active_nodes_map_negative

    if self.game.type in [Game.TYPE_PLACE_FIRST, Game.TYPE_PLACE_SECOND]:
      m = active_nodes_map_positive.copy()

      for nid, node in self.nodes.items():
        if node.type == BoardNode.TYPE_FREE:
          continue

        m[nid] = False

        for neighbour in games.settlers.board_def.NODE_DESCS[nid]['neighbours']:
          m[neighbour] = False

      return m

    if self.game.type in [Game.TYPE_APPLY_THIEF, Game.TYPE_APPLY_KNIGHT, Game.TYPE_APPLY_KNIGHT_GAME]:
      m = active_nodes_map_negative.copy()

      nodes = self.get_nodes_by_field(self.thief_field)
      for node in nodes:
        if node.type != BoardNode.TYPE_FREE and not node.is_owner(player):
          m[node.id] = True

      return m

    if self.game.type == Game.TYPE_GAME:
      m = active_nodes_map_positive.copy()

      for nid, node in self.nodes.items():
        if m[nid] == False:
          continue

        if node.type != BoardNode.TYPE_FREE:
          for neighbour in games.settlers.board_def.NODE_DESCS[nid]['neighbours']:
            m[neighbour] = False

          if node.type != BoardNode.TYPE_VILLAGE or not node.is_owner(player):
            m[nid] = False

          continue

        found = False
        for pid in games.settlers.board_def.NODE_DESCS[nid]['paths']:
          if not self.paths[pid].is_owner(player):
            continue
          found = True
          break
        m[nid] = found

      return m

    return active_nodes_map_negative

  def active_paths_map(self, player = None):
    player = player or self.game.my_player

    if player == None or not player.is_on_turn:
      return active_paths_map_negative

    if self.game.type in [Game.TYPE_FREE, Game.TYPE_PREPARE_THIEF, Game.TYPE_APPLY_THIEF, Game.TYPE_USE_KNIGHT,
                          Game.TYPE_USE_KNIGHT_GAME, Game.TYPE_FINISHED, Game.TYPE_PREPARE_DICE, Game.TYPE_PREPARE_KNIGHT,
                          Game.TYPE_APPLY_KNIGHT, Game.TYPE_FREE_RESOURCES, Game.TYPE_MONOPOLY, Game.TYPE_APPLY_KNIGHT_GAME,
                          Game.TYPE_CANCELED]:
      return active_paths_map_negative

    if self.game.type == Game.TYPE_PLACE_FIRST:
      if not player.first_village:
        return active_paths_map_negative

      return self.get_free_paths_map_by_node(player.first_village)

    if self.game.type == Game.TYPE_PLACE_SECOND:
      if not player.second_village:
        return active_paths_map_negative

      return self.get_free_paths_map_by_node(player.second_village)

    if self.game.type in [Game.TYPE_GAME, Game.TYPE_FREE_PATHS_FIRST, Game.TYPE_FREE_PATHS_SECOND]:
      m = active_paths_map_negative.copy()
      for path in self.paths.values():
        if path.type != BoardPath.TYPE_FREE:
          continue

        node1 = self.nodes[games.settlers.board_def.PATH_DESCS[path.id]['nodes'][0]]
        node2 = self.nodes[games.settlers.board_def.PATH_DESCS[path.id]['nodes'][1]]

        if node1.is_owner(player) or node2.is_owner(player):
          m[path.id] = True
          continue

        sibling1 = None
        for i in range(2):
          sibling1 = self.get_path_sibling_by_node(path, node1, i)
          if sibling1 == None:
            continue
          if sibling1.type == BoardPath.TYPE_OWNED and sibling1.is_owner(player):
            break
          sibling1 = None

        sibling2 = None
        for i in range(2):
          sibling2 = self.get_path_sibling_by_node(path, node2, i)
          if sibling2 == None:
            continue
          if sibling2.type == BoardPath.TYPE_OWNED and sibling2.is_owner(player):
            break
          sibling2 = None

        if (sibling1 and not sibling2 and node1.type != BoardNode.TYPE_FREE) or (sibling2 and not sibling1 and node2.type != BoardNode.TYPE_FREE):
          continue

        if sibling1 or sibling2:
          m[path.id] = True

      return m

    return {}

  def get_used_paths(self, player = None):
    return [p for p in self.paths.values() if (not player and p.type != BoardPath.TYPE_FREE) or (player and p.type != BoardPath.TYPE_FREE and p.is_owner(player))]

  def get_used_nodes(self, player = None):
    return [n for n in self.nodes.values() if (not player and n.type != BoardNode.TYPE_FREE) or (player and n.type != BoardNode.TYPE_FREE and n.is_owner(player))]

  def get_used_ports(self, player, resource):
    r = []

    for p in self.ports.values():
      if p.resource != resource:
        continue

      for n in p.nodes:
        node = self.nodes[n]
        if node.is_owner(player):
          r.append(node)

    return r

  def get_nodes_by_field(self, field):
    return [n for n in self.nodes.values() if field.id in games.settlers.board_def.NODE_DESCS[n.id]['fields']]

  def get_fields_by_node(self, n):
    return [self.fields[i] for i in games.settlers.board_def.NODE_DESCS[n.id]['fields']]

  def get_fields_by_number(self, n):
    return [f for f in self.fields.values() if f.number == n]

  def get_free_paths_map_by_node(self, node):
    return dict([(p.id, node.id in games.settlers.board_def.PATH_DESCS[p.id]['nodes'] and p.type == BoardPath.TYPE_FREE) for p in self.paths.values()])

  def get_node_by_path(self, path, index):
    return self.nodes[games.settlers.board_def.PATH_DESCS[path.id]['nodes'][index]]

  # Longest path search
  def get_path_sibling_by_node(self, path, node, index):
    i = 0
    for pid in games.settlers.board_def.NODE_DESCS[node.id]['paths']:
      if pid == path.id:
        index = index + 1
        i = i + 1
        continue
      if i == index:
        return self.paths[pid]
      i = i + 1

  def lps_init(self):
    self.lps_length = -1
    self.lps_counter = 0
    self.lps_owner = 0
    self.lps_multi = False

  def lps_node_is_traversable(self, node, owner):
    # pylint: disable-msg=R0201
    r = not ((node.type == BoardNode.TYPE_VILLAGE or node.type == BoardNode.TYPE_TOWN) and (not node.is_owner(owner)))
    return r

  def lps_save_result(self, owner):
    if self.lps_counter > self.lps_length:
      self.lps_owner = owner
      self.lps_length = self.lps_counter
      self.lps_multi = False

    elif self.lps_counter == self.lps_length:
      if self.lps_owner != owner:
        self.lps_multi = True

  def lps_traverse_path(self, path, node):
    path._v_mark = True

    self.lps_counter = self.lps_counter + 1

    traversed = False
    nodes_tested = False

    for i in range(2):
      p = self.get_path_sibling_by_node(path, node, i)
      # pylint: disable-msg=W0212
      if not p or p._v_mark or p.type != BoardPath.TYPE_OWNED or p.owner != path.owner:
        continue

      nodes_tested = True

      for j in range(2):
        n = self.get_node_by_path(p, j)
        if n.id == node.id:
          continue

        if not self.lps_node_is_traversable(n, path.owner):
          continue

        self.lps_traverse_path(p, n)
        traversed = True

    if not traversed:
      if nodes_tested == True:
        self.lps_counter = self.lps_counter + 1

      self.lps_save_result(path.owner)

      if nodes_tested == True:
        self.lps_counter = self.lps_counter - 1

    self.lps_counter = self.lps_counter - 1
    path._v_mark = False

  def lps_search(self):
    self.lps_init()

    for path in self.paths.values():
      if path.type != BoardPath.TYPE_OWNED:
        continue

      for i in [0, 1]:
        node = self.get_node_by_path(path, i)

        if not self.lps_node_is_traversable(node, path.owner):
          continue

        self.lps_traverse_path(path, node)

    if self.lps_length < 5:
      return (False, None, self.lps_length)

    if self.lps_multi:
      return (True, None, self.lps_length)

    return (True, self.lps_owner, self.lps_length)

class Game(games.Game):
  TYPE_PLACE_FIRST       = 10
  TYPE_PLACE_SECOND      = 11
  TYPE_PREPARE_KNIGHT    = 12
  TYPE_PREPARE_THIEF     = 13
  TYPE_APPLY_THIEF       = 14
  TYPE_USE_KNIGHT        = 15
  TYPE_APPLY_KNIGHT      = 16
  TYPE_PREPARE_DICE      = 17
  TYPE_MONOPOLY          = 18
  TYPE_USE_KNIGHT_GAME   = 19
  TYPE_APPLY_KNIGHT_GAME = 20
  TYPE_FREE_RESOURCES    = 21
  TYPE_FREE_PATHS_FIRST  = 22
  TYPE_FREE_PATHS_SECOND = 23

  TIMEOUT_BEGIN_TYPES = [0, 10, 11]
  TIMEOUT_TURN_TYPES  = [0, 10, 11, 2, 3]

  RESOURCE_EXCHANGE_FOUR  = 4
  RESOURCE_EXCHANGE_THREE = 3
  RESOURCE_EXCHANGE_TWO   = 2

  RESOURCE_DESCS = {'village': {Resource.RESOURCE_CLAY:  1,
                                Resource.RESOURCE_WOOD:  1,
                                Resource.RESOURCE_SHEEP: 1,
                                Resource.RESOURCE_GRAIN: 1},
                    'town':    {Resource.RESOURCE_GRAIN: 2,
                                Resource.RESOURCE_ROCK:  3},
                    'path':    {Resource.RESOURCE_CLAY:  1,
                                Resource.RESOURCE_WOOD:  1},
                    'card':    {Resource.RESOURCE_SHEEP: 1,
                                Resource.RESOURCE_GRAIN: 1,
                                Resource.RESOURCE_ROCK:  1}}

  def __init__(self, flags):
    games.Game.__init__(self, flags, Player)

    self.card_line		= ''
    self.card_index		= 0
    self.dice_rolls		= hlib.database.SimpleList()
    self.longest_length		= 0
    self.longest_owner		= games.DummyOwner()
    self.dont_shuffle		= flags.dont_shuffle

    cards = {Card.TYPE_KNIGHT:   14,
             Card.TYPE_MONOPOLY:  2,
             Card.TYPE_ROADS:     2,
             Card.TYPE_INVENTION: 2,
             Card.TYPE_POINT:     5}

    # pylint: disable-msg=W0612
    for i in range(25):
      while True:
        n = random.randint(0, 24)

        if 0 <= n and n <= 13:
          n = Card.TYPE_KNIGHT

        elif 14 <= n and n <= 15:
          n = Card.TYPE_MONOPOLY

        elif 16 <= n and n <= 17:
          n = Card.TYPE_ROADS

        elif 18 <= n and n <= 19:
          n = Card.TYPE_INVENTION

        else:
          n = Card.TYPE_POINT

        if cards[n] > 0:
          cards[n] -= 1
          self.card_line += unicode(n)
          break

  def __getattr__(self, name):
    if name == 'winner_player':
      if len(self.players) <= 0:
        return None

      if self.forhont_player.points <= 0:
        return None

      return self.forhont_player

    if name == 'dice_rolls_stats':
      ss = {'with':    {'numbers': {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}},
            'without': {'numbers': {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}}}

      i = 0
      for dr in self.dice_rolls:
        i = i + 1
        if i > self.limit * 3:
          ss['without']['numbers'][dr] += 1

        ss['with']['numbers'][dr] += 1

      ss['with']['sum'] = sum(ss['with']['numbers'])
      ss['without']['sum'] = sum(ss['without']['numbers'])

      return ss

    if name == 'last_numbers':
      if self.round == 0:
        return []

      if self.round < 2:
        return [i for i in reversed(list(self.dice_rolls))]
      else:
        return [i for i in reversed(list(self.dice_rolls[len(self.dice_rolls) - self.limit:]))]

    return games.Game.__getattr__(self, name)

  def to_state(self):
    d = games.Game.to_state(self)

    d.update({
      'last_numbers':		self.last_numbers,
      'board':			ApiBoard(self.board)
    })

    if self.type == games.Game.TYPE_FINISHED:
      drs = self.dice_rolls_stats

      d['dice_rolls'] = {
        'with':			[(k, v) for k, v in drs['with']['numbers'].items()],
        'without':		[(k, v) for k, v in drs['without']['numbers'].items()]
      }

    return d

  def begin(self):
    # pylint: disable-msg=W0201
    self.type = Game.TYPE_PLACE_FIRST

    if self.dont_shuffle != True:
      if self.limit == 3:
        order = [0, 1, 2]
      else:
        order = [0, 1, 2, 3]

      random.shuffle(order)

      new_players = hlib.database.IndexedMapping()
      tmp_players = [p for p in self.players.values()]
      for i in order:
        new_players.push(tmp_players[i])

      self.players = new_players

    games.Game.begin(self)

  def get_next_dice(self):
    while True:
      n = random.randint(1, 6) + random.randint(1, 6)
      if n == 7 and self.round < 4:
        continue

      self.dice_rolls.append(n)
      break

    return n

  def check_game_finalization(self):
    if self.my_player.points >= 10:
      self.finish()

  # pylint: disable-msg=R0201
  def build_object(self, o, player, newtype, resources = None):
    if resources:
      if not player.has_resources_for(Game.RESOURCE_DESCS[resources]):
        raise games.NotEnoughResourcesError()

      player.spend_resources_for(Game.RESOURCE_DESCS[resources])

    o.type = newtype
    o.owner = player

  def apply_monopoly(self, resource):
    # pylint: disable-msg=E1101
    for p in self.players.values():
      if p.id != self.my_player.id:
        p.apply_monopoly(self.my_player, resource)

    self.type = Game.TYPE_GAME

  def apply_invention(self, r1, r2):
    self.my_player.add_resource_raw(r1, 1)
    self.my_player.add_resource_raw(r2, 1)
    self.type = Game.TYPE_GAME

    rc = Resources()
    rc[r1] += 1
    rc[r2] += 1
    hlib.event.trigger('game.settlers.ResourcesReceived', self, hidden = True, game = self, user = self.my_player.user, resources = rc)

  def apply_points(self):
    if not self.type in [Game.TYPE_PREPARE_KNIGHT, Game.TYPE_GAME]:
      raise games.NotYourTurnError()

    if not self.my_player.is_on_turn:
      raise games.NotYourTurnError()

    cards = [c for c in self.my_player.cards.values() if c.type == Card.TYPE_POINT and not c.is_used]
    if self.my_player.points + len(cards) < 10:
      raise NotEnoughPointCardsError()

    i = 10 - self.my_player.points
    for c in cards:
      c.used = self.round
      hlib.event.trigger('game.CardUsed', self, game = self, user = self.my_player.user, card = c)

      i -= 1
      if i == 0:
        self.check_game_finalization()
        return

  def card_clicked(self, cid):
    card = self.my_player.cards[cid]

    if not card.can_be_used:
      raise games.InactiveCardError()

    card.used = self.round

    if card.type == Card.TYPE_KNIGHT:
      if self.type == Game.TYPE_PREPARE_KNIGHT:
        self.type = Game.TYPE_USE_KNIGHT
      else:
        self.type = Game.TYPE_USE_KNIGHT_GAME

      self.check_mightest_chilvary()

    elif card.type == Card.TYPE_POINT:
      self.check_game_finalization()

    elif card.type == Card.TYPE_MONOPOLY:
      self.type = Game.TYPE_MONOPOLY

    elif card.type == Card.TYPE_ROADS:
      if not self.my_player.has_free_path:
        raise TooManyPathsError()

      self.type = Game.TYPE_FREE_PATHS_FIRST

    elif card.type == Card.TYPE_INVENTION:
      self.type = Game.TYPE_FREE_RESOURCES

    hlib.event.trigger('game.CardUsed', self, game = self, user = self.my_player.user, card = card)

  def number_clicked(self, nid):
    if not self.my_player.is_on_turn:
      raise games.NotYourTurnError()

    if not self.type in [Game.TYPE_PREPARE_THIEF, Game.TYPE_USE_KNIGHT, Game.TYPE_USE_KNIGHT_GAME]:
      raise InactiveNumberError()

    if self.board.free_numbers_map[nid] != True:
      raise InactiveNumberError()

    for f in self.board.fields.values():
      f.thief = False

    self.board.fields[nid].thief = True

    hlib.event.trigger('game.settlers.ThiefPlaced', self, game = self, user = self.my_player.user, field = self.board.fields[nid])

    self.pass_turn(check = False)

  def path_clicked(self, pid):
    if not self.my_player.is_on_turn:
      raise games.NotYourTurnError()

    if self.board.active_paths_map()[pid] != True:
      raise InactivePathError()

    path = self.board.paths[pid]

    if self.type in [Game.TYPE_PLACE_FIRST, Game.TYPE_PLACE_SECOND]:
      path.type = BoardPath.TYPE_OWNED
      path.owner = self.my_player
      return

    if self.type == Game.TYPE_FREE_PATHS_FIRST:
      self.build_object(path, self.my_player, BoardPath.TYPE_OWNED)
      hlib.event.trigger('game.settlers.PathBuilt', self, hidden = True, game = self, user = self.my_player.user, path = path)

      if not self.my_player.has_free_path:
        self.type = Game.TYPE_GAME
      else:
        self.type = Game.TYPE_FREE_PATHS_SECOND

      self.check_longest_path()
      return

    if self.type == Game.TYPE_FREE_PATHS_SECOND:
      self.build_object(path, self.my_player, BoardPath.TYPE_OWNED)
      hlib.event.trigger('game.settlers.PathBuilt', self, hidden = True, game = self, user = self.my_player.user, path = path)
      self.type = Game.TYPE_GAME
      self.check_longest_path()
      return

    if self.type == Game.TYPE_GAME:
      if not self.my_player.has_free_path:
        raise TooManyPathsError()

      self.build_object(path, self.my_player, BoardPath.TYPE_OWNED, 'path')
      hlib.event.trigger('game.settlers.PathBuilt', self, hidden = True, game = self, user = self.my_player.user, path = path)
      self.check_longest_path()

  def node_clicked(self, nid):
    if not self.my_player.is_on_turn:
      raise games.NotYourTurnError()

    if self.board.active_nodes_map()[nid] != True:
      raise InactiveNodeError()

    node = self.board.nodes[nid]

    if self.type in [Game.TYPE_PLACE_FIRST, Game.TYPE_PLACE_SECOND]:
      node.type = BoardNode.TYPE_VILLAGE
      node.owner = self.my_player

      if self.my_player.first_village == None:
        self.my_player.first_village = node

      elif self.my_player.second_village == None:
        self.my_player.second_village = node

      return

    if self.type in [Game.TYPE_APPLY_THIEF, Game.TYPE_APPLY_KNIGHT, Game.TYPE_APPLY_KNIGHT_GAME]:
      node.owner.apply_thief_to_one(self.my_player)
      self.pass_turn(check = False)
      return

    if self.type == Game.TYPE_GAME:
      if node.type == BoardNode.TYPE_FREE:
        if not self.my_player.has_free_village:
          raise TooManyVillagesError()

        self.build_object(node, self.my_player, BoardNode.TYPE_VILLAGE, 'village')
        hlib.event.trigger('game.settlers.VillageBuilt', self, hidden = True, game = self, user = self.my_player.user, node = node)
        self.check_longest_path()

      elif node.type == BoardNode.TYPE_VILLAGE:
        if not self.my_player.has_free_town:
          raise TooManyTownsError()

        self.build_object(node, self.my_player, BoardNode.TYPE_TOWN, 'town')
        hlib.event.trigger('game.settlers.TownBuilt', self, hidden = True, game = self, user = self.my_player.user, node = node)
        self.check_game_finalization()

  def buy_card(self):
    # pylint: disable-msg=E0203,W0201

    if not self.my_player.is_on_turn:
      raise games.NotYourTurnError()

    if self.card_index == 25:
      raise games.GameError(msg = 'The deck is empty')

    if not self.my_player.has_resources_for(Game.RESOURCE_DESCS['card']):
      raise games.NotEnoughResourcesError()

    self.my_player.spend_resources_for(Game.RESOURCE_DESCS['card'])

    c = Card(self, self.my_player, int(self.card_line[self.card_index]), self.round)
    self.my_player.cards.push(c)
    self.card_index += 1

    hlib.event.trigger('game.CardBought', self, game = self, user = self.my_player.user, card = c)

  def deal_resources(self, dice):
    per_owner = dict([(i, Resources()) for i in self.players.keys()])

    for field in self.board.get_fields_by_number(dice):
      if field.thief:
        continue

      nodes = [n for n in self.board.get_nodes_by_field(field) if n.type != BoardNode.TYPE_FREE]
      for node in nodes:
        (resource, amount) = node.owner.add_resource(node, field)
        per_owner[node.owner.id].add(Resource.map_resource2str[resource], amount)

    # pylint: disable-msg=E1101
    for p in self.players.values():
      r = per_owner[p.id]
      if r.sum() > 0:
        hlib.event.trigger('game.settlers.ResourcesReceived', self, hidden = True, game = self, user = p.user, resources = per_owner[p.id])

  def roll_dice(self):
    if not self.my_player.can_roll_dice:
      raise games.NotYourTurnError()

    dice = self.get_next_dice()

    hlib.event.trigger('game.settlers.DiceRolled', self, game = self, user = self.my_player.user, dice = dice)

    if dice == 7:
      self.type = Game.TYPE_PREPARE_THIEF

      # pylint: disable-msg=E1101
      for player in self.players.values():
        if player.resources.sum() > 7:
          player.apply_thief_to_full()

    else:
      self.deal_resources(dice)
      self.type = Game.TYPE_GAME

  def can_we_steal(self):
    for node in self.board.get_used_nodes():
      if node.is_owner(self.my_player):
        continue

      if self.board.thief_field.id in games.settlers.board_def.NODE_DESCS[node.id]['fields']:
        return True
    return False

  def do_pass_turn(self, forced = False):
    # pylint: disable-msg=W0201,R0912,R0915
    self.last_pass = hruntime.time

    current_forhont = self.forhont
    next_round = False

    if forced:
      self.type = Game.TYPE_GAME

    if self.type == Game.TYPE_APPLY_THIEF:
      self.type = Game.TYPE_GAME

    elif self.type == Game.TYPE_PREPARE_THIEF:
      if self.can_we_steal():
        self.type = Game.TYPE_APPLY_THIEF
      else:
        self.type = Game.TYPE_GAME

    elif self.type == Game.TYPE_APPLY_KNIGHT:
      self.type = Game.TYPE_PREPARE_DICE

    elif self.type == Game.TYPE_APPLY_KNIGHT_GAME:
      self.type = Game.TYPE_GAME

    elif self.type == Game.TYPE_USE_KNIGHT:
      if self.can_we_steal():
        self.type = Game.TYPE_APPLY_KNIGHT
      else:
        self.type = Game.TYPE_PREPARE_DICE

    elif self.type == Game.TYPE_USE_KNIGHT_GAME:
      if self.can_we_steal():
        self.type = Game.TYPE_APPLY_KNIGHT_GAME
      else:
        self.type = Game.TYPE_GAME

    elif self.type == Game.TYPE_GAME:
      if self.forhont == self.limit - 1:
        self.forhont = 0
        next_round = True
      else:
        self.forhont = self.forhont + 1

      if self.round == 1 and next_round != True:
        self.type = Game.TYPE_PREPARE_DICE
      else:
        self.type = Game.TYPE_PREPARE_KNIGHT

    elif self.type == Game.TYPE_PLACE_SECOND:
      if self.my_player.second_village:
        rc = Resources()
        for field in self.board.get_fields_by_node(self.my_player.second_village):
          rst = self.my_player.add_resource(self.my_player.second_village, field)
          if rst != None:
            rc.add(rst[0], rst[1])

        hlib.event.trigger('game.settlers.ResourcesReceived', self, hidden = False, game = self, user = self.my_player.user, resources = rc)

      if self.forhont == 0:
        next_round = True
        self.type = Game.TYPE_PREPARE_DICE
      else:
        self.forhont = self.forhont - 1

    elif self.type == Game.TYPE_PLACE_FIRST:
      if self.forhont == self.limit - 1:
        self.type = Game.TYPE_PLACE_SECOND
      else:
        self.forhont = self.forhont + 1

    else:
      if self.forhont == self.limit - 1:
        self.forhont = 0
      else:
        self.forhont = self.forhont + 1

    if current_forhont != self.forhont:
      while self.forhont_player.has_too_many_misses():
        next_round = self.do_pass_turn(forced = forced)

      # Check it on entering new player's turn - it is possible to have >10 points and NOT be on turn.
      self.check_game_finalization()

    return next_round

  def pass_turn(self, **kwargs):
    if 'first_village' in kwargs and 'first_path' in kwargs:
      if self.my_player.first_village != None:
        raise games.GameError(msg = 'You have first village already')

      nid = int(kwargs['first_village'])
      pid = int(kwargs['first_path'])

      self.node_clicked(nid)
      self.path_clicked(pid)

      del kwargs['first_village']
      del kwargs['first_path']

    if 'second_village' in kwargs and 'second_path' in kwargs:
      if self.my_player.second_village != None:
        raise games.GameError(msg = 'You have second village already')

      nid = int(kwargs['second_village'])
      pid = int(kwargs['second_path'])

      self.node_clicked(nid)
      self.path_clicked(pid)

      del kwargs['second_village']
      del kwargs['second_path']

    games.Game.pass_turn(self, **kwargs)

  def reset_players_lps(self):
    # pylint: disable-msg=E1101
    for player in self.players.values():
      player.longest_path = False

  def check_longest_path(self):
    linfo = self.board.lps_search()

    if linfo[0] == False:
      # pylint: disable-msg=W0201
      self.reset_players_lps()
      self.longest_length = linfo[2]
      self.longest_owner = games.DummyOwner()

    else:
      if linfo[1] == None:
        self.longest_length = linfo[2]
      else:
        self.reset_players_lps()
        self.longest_length = linfo[2]
        if linfo[1] != self.longest_owner:
          self.longest_owner = linfo[1]
          hlib.event.trigger('game.settlers.LongestPathBonusEarned', self, game = self, user = self.longest_owner.user)
        self.longest_owner.longest_path = True

    self.check_game_finalization()

  def check_mightest_chilvary(self):
    # pylint: disable-msg=E1101

    max_count = 0
    max_player = None
    max_players = 0

    for player in self.players.values():
      cards = [c for c in player.cards.values() if c.type == Card.TYPE_KNIGHT and c.is_used]

      if len(cards) > max_count:
        max_count = len(cards)
        max_player = player
        max_players = 1

      elif len(cards) == max_count:
        max_players += 1

    if max_count < 3:
      return

    if max_players != 1:
      return

    old_owner = None

    for player in self.players.values():
      if player.mightest_chilvary == True:
        old_owner = player

      player.mightest_chilvary = False

    max_player.mightest_chilvary = True

    if max_player != old_owner:
      hlib.event.trigger('game.settlers.MightestChilvaryBonusEarned', self, game = self, user = max_player.user)

    self.check_game_finalization()

  @staticmethod
  def create_game(flags, system_game = False):
    g = games.Game.create_game(Game, flags, system_game = system_game)
    g.board = Board(g)

    return g

class GameCreationFlags(games.GameCreationFlags):
  FLAGS = games.GameCreationFlags.FLAGS + ['floating_desert']

import events.game.settlers

import board_def	# Relative import is required to avoid circular imports
active_nodes_map_negative = dict([(_i, False) for _i in range(1, len(board_def.NODE_DESCS))])
active_nodes_map_positive = dict([(_i, True) for _i in range(1, len(board_def.NODE_DESCS))])
active_paths_map_negative = dict([(_i, False) for _i in range(1, len(board_def.PATH_DESCS))])
