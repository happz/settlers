from collections import defaultdict

class Bus(object):
    def __init__(self, name, logger):
        self._name = name
        self._logger = logger

        self.reset()

    def subscribe(self, event, callback):
        self._logger.debug('%s.subscribe: event=%s, callback=%s' % (self._name, event, callback.func_name))

        self._subscriptions[event].append(callback)

        return self

    def unsubscribe(self, event, callback):
        if not is_subscribed(event, callback):
            return self

        self._logger.debug('%s.unsubscribe: event=%s, callback=%s' % (self._name, event, callback.func_name))

        self._subscriptions[event].remove(callback)
        return self

    def unsubscribe_all(self, event):
        self._subscriptions[event] = list()

    def is_subscribed(self, event, callback):
        return callback is self._subscriptions[event]

    def has_any_subscriptions(self, event):
        return bool(self._subscriptions[event])

    def publish(self, event, *args, **kwargs):
        self._logger.debug('%s.publish: event=%s' % (self._name, event))

        if not self.has_any_subscriptions(event):
            return self

        for callback in self._subscriptions[event]:
            self._logger.debug('%s.callback: callback=%s' % (self._name, callback.func_name))

            callback(self, *args, **kwargs)

    def reset(self):
        self._subscriptions = defaultdict(list)
