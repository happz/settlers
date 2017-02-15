"""
Localization methods

@author:                Milos Prchlik
@contact:               U{happz@happz.cz}
@license:               DPL (U{http://www.php-suit.com/dpl})
"""

import threading

import hlib
import hlib.database
import hlib.locks

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

# hlib.config['i18n.token_coverage'] = True

class TokenCoverage(object):
  def __init__(self):
    super(TokenCoverage, self).__init__()

    self.lock = hlib.locks.RLock(name = 'Token coverage')

    self.hits		= {}
    self.misses		= {}

  def hit(self, name):
    with self.lock:
      self.hits[name] = True

  def miss(self, name):
    with self.lock:
      self.misses[name] = True

  def added(self, name):
    with self.lock:
      if name in self.misses:
        del self.misses[name]

  def removed(self, name):
    with self.lock:
      if name in self.hits:
        del self.hits[name]

  def coverage(self, lang):
    unused = {}

    with self.lock:
      for key in lang.tokens.iterkeys():
        if key in self.hits:
          continue

        unused[key] = True

    return (self.hits.copy(), self.misses.copy(), unused)

COVERAGE = {
}

class Language(hlib.database.DBObject):
  def __init__(self, name):
    hlib.database.DBObject.__init__(self)

    self.name		= name
    self.tokens		= hlib.database.StringMapping()

    self.coverage	= None

  def __getstate__(self):
    d = self.__dict__.copy()
    del d['coverage']
    return d

  def __setstate__(self, d):
    # pylint: disable-msg=W0201
    self.__dict__ = d

    if d['name'] not in COVERAGE:
      COVERAGE[d['name']] = TokenCoverage()

    self.coverage = COVERAGE[d['name']]

  def __getitem__(self, name):
    if name in self.tokens:
      if self.coverage:
        self.coverage.hit(name)

      return self.tokens[name]

    if self.coverage:
      self.coverage.miss(name)

    return name

  def __setitem__(self, name, value):
    self.tokens[name] = value

    if self.coverage:
      self.coverage.added(name)

  def __delitem__(self, name):
    if name in self.tokens:
      del self.tokens[name]

    if self.coverage:
      self.coverage.removed(name)

  def __len__(self):
    return len(self.tokens)

class Localization(hlib.database.DBObject):
  """
  Provides methods for translating tokens to into several languages.

  Instantiate with Localization(languages=[lang1, lang2, ...])
  where 'languages' is list of strings, defining languages to be loaded and enabled.
  """

  def __init__(self, languages = None):
    hlib.database.DBObject.__init__(self)

    languages = languages or []

    self.languages	= hlib.database.StringMapping()

    for l in languages:
      self.languages[l] = Language(l)

def gettext(token, **kwargs):
  """
  Translates one token, and replace parameters in result.

  @param token:			Token to translate.
  @type token:			C{string}
  @param kwargs:		Names and values to replace in translated token.
  @type kwargs:			C{dictionary}
  @return:			Translation of token.
  @rtype:			C{string}
  """

  return hruntime.i18n[token] % kwargs
