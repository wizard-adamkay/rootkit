import os
import pyinotify


class EventProcessor(pyinotify.ProcessEvent):
    _methods = ["IN_CREATE",
                "IN_CLOSE_WRITE",
                "IN_DELETE",
                "IN_MOVED_FROM",
                "IN_MOVED_TO",
                "default"]


class Watch:
    def __init__(self, directory):
        self.watch_manager = pyinotify.WatchManager()
        self.event_notifier = pyinotify.Notifier(self.watch_manager, EventProcessor())
        watch_this = os.path.relpath(directory)
        self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)

        def process_generator(cls, method):
            def _method_name(self, event):
                if method != "default" and ".part" not in event.pathname and ".kate-swp" not in event.pathname:
                    print("Method name: process_{}()\n"
                          "Path name: {}\n"
                          "Event Name: {}\n".format(method, event.pathname, event.maskname))

            _method_name.__name__ = "process_{}".format(method)
            setattr(cls, _method_name.__name__, _method_name)

        for method in EventProcessor._methods:
            process_generator(EventProcessor, method)

    def start(self):
        self.event_notifier.loop()

    def stop(self):
        self.event_notifier.stop()
