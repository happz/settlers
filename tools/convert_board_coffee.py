import games.settlers.board_def as B

N_NODES		= 55
N_PATHS		= 73

active_nodes_map_negative = dict([(i, False) for i in range(1, N_NODES)])
active_nodes_map_positive = dict([(i, True) for i in range(1, N_NODES)])
active_paths_map_negative = dict([(i, False) for i in range(1, 74)])

print 'window.settlers = window.settlers or {}'
print 'window.settlers.board_defs = window.settlers.board_defs or {}'
print 'window.settlers.board_defs.active_nodes_map_negative = { %s }' % ', '.join(['n%s: false' % k for k in active_nodes_map_negative.keys()])
print 'window.settlers.board_defs.active_nodes_map_positive = { %s }' % ', '.join(['n%s: true' % k for k in active_nodes_map_positive.keys()])
print 'window.settlers.board_defs.active_paths_map_negative = { %s }' % ', '.join(['p%s: false' % k for k in active_paths_map_negative.keys()])

print

print 'window.settlers.board_defs.nodes ='

for i in range(1, N_NODES):
  nd = B.NODE_DESCS[i]

  print """  n%i:
    neighbours:			[%s]
    fields:			[%s]
    paths:			[%s]""" % (i, ', '.join([str(n) for n in nd['neighbours']]), ', '.join([str(n) for n in nd['fields']]), ', '.join([str(n) for n in nd['paths']]))

print
print 'window.settlers.board_defs.paths ='

for i in range(1, N_PATHS):
  pd = B.PATH_DESCS[i]
  print """  p%i:
    nodes:			[%s]""" % (i, ', '.join([str(n) for n in pd['nodes']]))
