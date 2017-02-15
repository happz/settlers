import datetime
import threading
import time

import hlib.events
import hlib.locks

class __AllMatch(set):
  def __contains__(self, item):
    return True

allMatch = __AllMatch()

class Task(object):
  def __init__(self, name, callback, min = allMatch, hour = allMatch, day = allMatch, month = allMatch, dow = allMatch, *args, **kwargs):
    super(Task, self).__init__()

    self.name = name

    self.callback = callback
    self.args = args
    self.kwargs = kwargs

    def __conv_to_set(obj):
      if isinstance(obj, (int, long)):
        return set([obj])
      if not isinstance(obj, set):
        obj = set(obj)
      return obj

    self.mins = __conv_to_set(min)
    self.hours = __conv_to_set(hour)
    self.days = __conv_to_set(day)
    self.months = __conv_to_set(month)
    self.dow = __conv_to_set(dow)

  def matchtime(self, t):
    return (    (t.minute in self.mins)
            and (t.hour in self.hours)
            and (t.day in self.days)
            and (t.month in self.months)
            and (t.weekday() in self.dow))

  def run(self, engine, app):
    self.callback(*self.args, engine = engine, app = app, **self.kwargs)

class SchedulerThread(threading.Thread):
  def __init__(self, engine, *args, **kwargs):
    threading.Thread.__init__(self, *args, name = 'Scheduler thread "%s"' % engine.name, **kwargs)

    self.daemon = True
    self.engine = engine

    self.lock = hlib.locks.RLock(name = 'Scheduler tasks lock')
    self.tasks = {}

  def add_task(self, task, app = None):
    with self.lock:
      self.tasks[task.name] = (task, app)

  def remove_task(self, task):
    with self.lock:
      del self.tasks[task.name]

  def run(self):
    sleep_until = datetime.datetime.now() + datetime.timedelta(minutes = 1)

    def __run_task(_app):
      hlib.events.trigger('engine.ScheduledTaskTriggered', None, engine = self.engine, app = _app, task = task)
      task.run(self.engine, _app)

    while True:
      while True:
        current_time = datetime.datetime.now()

        if current_time >= sleep_until:
          break

        time.sleep(20)

      with self.lock:
        for task, app in self.tasks.values():
          if not task.matchtime(current_time):
            continue

          if app == None:
            for app in self.engine.apps.values():
              __run_task(app)

          else:
            __run_task(app)

      sleep_until = datetime.datetime.now() + datetime.timedelta(minutes = 1)
