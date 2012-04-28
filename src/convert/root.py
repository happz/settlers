import convert
import lib

# pylint: disable-msg=F0401
import hruntime

class Convertor(convert.Convertor):
  def __init__(self, *args, **kwargs):
    super(Convertor, self).__init__('root', *args, **kwargs)

  def run(self):
    if 'root' in hruntime.db.root:
      del hruntime.db.root['root']

    hruntime.db.root['root'] = lib.datalayer.Root()
    hruntime.dbroot = hruntime.db.root['root']

convert.CONVERTORS['root'] = Convertor
