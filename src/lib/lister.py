import hlib.api

class ApiLister(hlib.api.ApiJSON):
  def __init__(self):
    super(ApiLister, self).__init__(['cnt_total', 'cnt_display', 'records'])

    self.cnt_total		= 0
    self.cnt_display		= 0
    self.records		= []
