import pprint
import sys

import games.settlers.board_def as B

offset = (59 + 29, 102)

#
# settlers-board-<piece>-<board type>-<piece type>-<color>[-active]
#

s = """
.settlers-board-field-{board}-{resource} {po}
  background-image:		url(/static/images/games/settlers/board/{board}/field/{resource}.gif);
{pc}"""

for b in ['simple', 'real']:
  for r in ['clay', 'grain', 'rock', 'wood', 'sheep', 'desert']:
    print s.format(board = b, resource = r, po = '{', pc = '}')

s = """
.settlers-board-field-%i {
  left:		%ipx;
  top:		%ipx;
}"""
for k, v in B.COORS['field'].iteritems():
  print s % (k, v[0] + 59 + 29, v[1] + 102)

s = """
.settlers-board-thief-{number} {po}
  left:			{left}px;
  top:			{top}px;
{pc}"""

for k, v in B.COORS['thief'].iteritems():
  print s.format(po = '{', pc = '}', number = k, left = v[0] + offset[0], top = v[1] + offset[1])

s = """
.settlers-board-number-field-{fid} {po}
  left:			{left}px;
  top:			{top}px;
{pc}"""

for k, v in B.COORS['number'].iteritems():
  print s.format(fid = k, left = v[0] + offset[0], top = v[1] + offset[1], po = '{', pc = '}')

s = """
.settlers-board-number-{number} {po}
  background-image:		url(/static/images/games/settlers/board/simple/numbers/{number}.gif);
{pc}"""

for i in range(2, 13):
  print s.format(number = i, po = '{', pc = '}')

s = """
.settlers-board-node-{board}-{type}-{color} {po}
  background-image:             url(/static/images/games/settlers/board/{board}/players/{color}/node/{type}.gif);
{pc}

.settlers-board-node-{board}-{type}-{color}-active {po}
  background-image:		url(/static/images/games/settlers/board/{board}/players/{color}/node/{type}_active.gif);
{pc}"""

for b in ['simple', 'real']:
  for t in ['village', 'town']:
    for c in ['black', 'brown', 'dark_blue', 'dark_green', 'green', 'light_blue', 'orange', 'pink', 'purple', 'red']:
      print s.format(board = b, type = t, color = c, po = '{', pc = '}')

s = """
.settlers-board-node-simple-free {po}
  background-image:		url(/static/images/games/settlers/board/simple/players/free/node/free.gif);
{pc}

.settlers-board-node-simple-free-active {po}
  background-image:		url(/static/images/games/settlers/board/simple/players/free/node/free_active.gif);
{pc}

.settlers-board-node-real-free {po}
  background-image:		url(/static/images/games/settlers/board/real/players/free/node/free.gif);
{pc}

.settlers-board-node-real-free-active {po}
  background-image:		url(/static/images/games/settlers/board/real/players/free/node/free_active.gif);
{pc}"""

print s.format(po = '{', pc = '}')

s = """
.settlers-board-node-free-{nid} {po}
  left:			{left_free}px;
  top:			{top_free}px;
{pc}

.settlers-board-node-owned-{nid} {po}
  left:			{left_owned}px;
  top:			{top_owned}px;
{pc}
"""

for k, v in B.COORS['node'].iteritems():
  print s.format(po = '{', pc = '}',
                 nid = k,
                 left_free = v[1][0] + offset[0], top_free = v[1][1] + offset[1],
                 left_owned = v[2][0] + offset[0], top_owned = v[2][1] + offset[1])

s = """
.settlers-board-sea-{sid} {po}
  left:			{left}px;
  top:			{top}px;
{pc}
"""

for k, v in B.COORS['sea'].iteritems():
  print s.format(po = '{', pc = '}', sid = k,
                 left = v[0] + offset[0], top = v[1] + offset[1])

s = """
.settlers-board-port-{resource}-{clock}-real {po}
  background-image:		url(/static/images/games/settlers/board/real/field/ports/{resource}/{clock}.gif);
{pc}

.settlers-board-port-{resource}-{clock}-simple {po}
  background-image:		url(/static/images/games/settlers/board/simple/field/ports/{resource}/{clock}.gif);
{pc}
"""

for r in ['wood', 'clay', 'sheep', 'grain', 'rock', 'free']:
  for c in range(1, 7):
    print s.format(po = '{', pc = '}', resource = r, clock = c)

s = """
.settlers-board-path-{board}-{color}-{type} {po}
  background-image:             url(/static/images/games/settlers/board/{board}/players/{color}/path/{type}.gif);
{pc}"""

for b in ['simple', 'real']:
  for c in ['black', 'brown', 'dark_blue', 'dark_green', 'green', 'light_blue', 'orange', 'pink', 'purple', 'red']:
    for t in ['t', 'lt', 'rt']:
      print s.format(board = b, type = t, color = c, po = '{', pc = '}')

s = """
.settlers-board-path-{pid} {po}
  left:				{left}px;
  top:				{top}px;
{pc}"""

for k, v in B.COORS['path'].iteritems():
  print s.format(po = '{', pc = '}',
                 pid = k,
                 left = v[0] + offset[0],
                 top = v[1] + offset[1])

map_pos2str = {
  1: 'lt',
  2:  't',
  3: 'rt',
  4: 'lt',
  5:  't',
  6: 'rt'
}

#print >> sys.stderr, 'map_pathid_to_position = [\'undefined\', ' + ', '.join(['\'' + map_pos2str[B.PATH_DESCS[k]['position']]+ '\''  for k in range(1, 73)]) + ']'
