from ..timeline import Timeline
from ..utils.prefix import names_with_prefix, strip_prefix


class EventManager(object):
    def __init__(self, events):
        self._timeline = Timeline(events)
        self._initializing = False
        self._initialized = False
        self._running = False
        self._finalizing = False

        self._order = list(events)

    def initialize(self):
        if not self._initializing:
            self._initializing = True
            #for event in self._timeline.events:
            for (event, _) in self._order:
                try:
                    event.initialize()
                except Exception as error:
                    print 'error initializing'
                    print event
                    raise
            self._initialized = True

    def run(self, stop_time):
        self.initialize()
        if not self._running:
            self._running = True
            for event in self._timeline.iter_until(stop_time):
                try:
                    event.run(self._timeline.time)
                except AttributeError:
                    event.update(self._timeline.time)
            self._running = False

    def finalize(self):
        if self._initialized:
            if not self._finalizing:
                self._finalizing = True
                #for event in self._timeline.events:
                for (event, _) in self._order[::-1]:
                    event.finalize()
            self._initialized = False

    def add_recurring_event(self, event, interval):
        self._timeline.add_recurring_event(event, interval)
        self._order.append((event, interval))

    @property
    def time(self):
        return self._timeline.time

    @classmethod
    def from_string(cls, source, prefix=''):
        config = ConfigParser()
        config.readfp(StringIO(source))
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def from_path(cls, path, prefix=''):
        config = ConfigParser()
        config.read(path)
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def _from_config(cls, config, prefix=''):
        event_names = names_with_prefix(config.sections(), prefix)
        events = []
        for name in event_names:
            events.append((name, config.get(name, 'interval')))
        return cls(events)

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, type, value, traceback):
        self.finalize()
