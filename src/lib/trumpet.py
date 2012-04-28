"""
Public and mass texts.

@author:                Milos Prchlik
@contact:               U{happz@happz.cz}
@license:               DPL (U{http://www.php-suit.com/dpl})
"""

# pylint: disable-msg=F0401
import hruntime

class TrumpetObject(object):
  subject		= property(lambda self: getattr(hruntime.dbroot.trumpet, self.__class__.__name__)['subject'], lambda self, subject: getattr(hruntime.dbroot.trumpet, self.__class__.__name__).update({'subject': subject}))
  text			= property(lambda self: getattr(hruntime.dbroot.trumpet, self.__class__.__name__)['text'], lambda self, text: getattr(hruntime.dbroot.trumpet, self.__class__.__name__).update({'text': text}))
  text_splitted		= property(lambda self: self.text.split('\n'))

class PasswordRecoveryMail(TrumpetObject):
  pass

class Board(TrumpetObject):
  pass

class VacationTermination(TrumpetObject):
  pass
