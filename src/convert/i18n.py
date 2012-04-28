import convert

import hlib.i18n

# pylint: disable-msg=F0401
import hruntime

class Convertor(convert.Convertor):
  def __init__(self, *args, **kwargs):
    super(Convertor, self).__init__('i18n', *args, **kwargs)

  def convert_item(self, record):
    if record.language not in hruntime.dbroot.localization.languages:
      hruntime.dbroot.localization.languages[record.language] = hlib.i18n.Language(record.language)

    hruntime.dbroot.localization.languages[record.language].tokens[record.name] = record.value

  def run(self):
    hruntime.dbroot.localization = hlib.i18n.Localization(languages = ['cz'])

    super(Convertor, self).run('SELECT %s FROM `localization`', ['language', 'name', 'value'])

convert.CONVERTORS['i18n'] = Convertor
