import games.settlers.board_def as B

N_NODES		= 55
N_PATHS		= 73

active_nodes_map_negative = dict([(i, False) for i in range(1, N_NODES)])
active_nodes_map_positive = dict([(i, True) for i in range(1, N_NODES)])
active_paths_map_negative = dict([(i, False) for i in range(1, 74)])

print 'window.settlers = window.settlers or {}'
print 'window.settlers.board_defs = window.settlers.board_defs or {}'
print 'window.settlers.board_defs.active_nodes_map_negative = [ null, %s ]' % ', '.join(['false' for k in active_nodes_map_negative.keys()])
print 'window.settlers.board_defs.active_nodes_map_positive = [ null, %s ]' % ', '.join(['true' for k in active_nodes_map_positive.keys()])
print 'window.settlers.board_defs.active_paths_map_negative = [ null, %s ]' % ', '.join(['false' for k in active_paths_map_negative.keys()])

print

print """window.settlers.board_defs.nodes = [
  null,"""

for i in range(1, N_NODES):
  nd = B.NODE_DESCS[i]

  print """  {
    neighbours:			[%s]
    fields:			[%s]
    paths:			[%s]
  },""" % (', '.join([str(n) for n in nd['neighbours']]), ', '.join([str(n) for n in nd['fields']]), ', '.join([str(n) for n in nd['paths']]))

print """]

window.settlers.board_defs.paths = [
  null,"""

for i in range(1, N_PATHS):
  pd = B.PATH_DESCS[i]
  print """  {
    nodes:			[%s]
  },""" % (', '.join([str(n) for n in pd['nodes']]))

print """]
"""
