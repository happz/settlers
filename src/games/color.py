import lib.datalayer

class Color(object):
  def __init__(self, name, label, color):
    super(Color, self).__init__()

    self.name		= name
    self.label		= label
    self.color		= color

  def to_api(self):
    return {
      'name':		self.name,
      'color':		self.color
    }

class ColorSpace(object):
  DEFAULT_COLOR_NAME	= 'dark_green'
  FREE_COLOR_NAME	= 'free'

  def __init__(self, kind, colors = None):
    super(ColorSpace, self).__init__()

    self.kind		= kind
    self.colors		= colors or {}

  def unused_colors(self, user):
    return [color_name for color_name in self.colors.keys() if color_name != self.FREE_COLOR_NAME and color_name not in user.used_colors(self)]

  def colorize_player(self, player, viewer):
    if player == viewer:
      return player.user.color(self)

    if self.kind in viewer.user.colors and player.user.name in viewer.user.colors[self.kind]:
      return self.colors[viewer.user.colors[self.kind][player.user.name]]

    i = player.id
    if viewer.id < player.id:
      i = i - 1

    return self.colors[self.unused_colors(viewer.user)[i]]
