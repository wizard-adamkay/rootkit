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
    def __init__(self):
        self.watch_manager = pyinotify.WatchManager()
        self.event_notifier = pyinotify.Notifier(self.watch_manager, EventProcessor())

        def process_generator(cls, method):
            def _method_name(asdf, event):
                if method != "default" and ".part" not in event.pathname and ".kate-swp" not in event.pathname:
                    target = "Directory" if "IN_ISDIR" in event.maskname else "File"
                    path = os.path.split(event.pathname)[0]
                    name = os.path.split(event.pathname)[-1]
                    if "IN_CREATE" in event.maskname:
                        print(f"{target} {name} created in {path}")
                        if target == "Directory":
                            self.add_watched(event.pathname, True)
                    elif "IN_MOVED_FROM" in event.maskname:
                        print(f"{target} {name} moved from {path}")
                    elif "IN_CLOSE_WRITE" in event.maskname:
                        print(f"{target} {name} changed in {path}")
                    elif "IN_DELETE" in event.maskname:
                        print(f"{target} {name} deleted in {path}")
                    elif "IN_MOVED_TO" in event.maskname:
                        print(f"{target} {name} moved to {path}")
                        if target == "Directory":
                            self.add_watched(event.pathname, True)

            _method_name.__name__ = "process_{}".format(method)
            setattr(cls, _method_name.__name__, _method_name)

        for method in EventProcessor._methods:
            process_generator(EventProcessor, method)

    def add_watched(self, directory, recursive):
        if not os.path.exists(directory):
            print(f"{directory} doesnt exist")
        watch_this = os.path.relpath(directory)
        self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)
        if recursive:
            for roots, dirs, files in os.walk(directory):
                watch_this = os.path.relpath(roots)
                self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)
        else:
            watch_this = os.path.relpath(directory)
            self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)

    def start(self):
        self.event_notifier.loop()

    def stop(self):
        self.event_notifier.stop()
