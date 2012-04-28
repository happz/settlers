"""
System-wide events.

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

from hlib.events.system import UserEvent

class ChatPost(UserEvent):
  pass

import hlib

hlib.register_event(ChatPost)
