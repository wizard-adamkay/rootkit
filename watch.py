import os
import pyinotify
import shutil

class EventProcessor(pyinotify.ProcessEvent):
    _methods = ["IN_CREATE",
                "IN_CLOSE_WRITE",
                "IN_DELETE",
                "IN_MOVED_FROM",
                "IN_MOVED_TO",
                "default"]


def current_file_version(file):
    i = 0
    while True:
        if not os.path.exists(temp_dir + file + str(i)):
            return str(i)
        i += 1


temp_dir = "/var/tmp/.hiding/"
base_dirs = []


def add_path(path):
    tpath = trim_path(path)
    name = os.path.split(path)[-1]
    if os.path.isdir(path):
        shutil.copy2(path, tpath + name + current_file_version(tpath + name))
    else:
        print("do this later")

def trim_path(path):
    path = os.path.normpath(path)
    dir_list = path.split(os.sep)
    print(f"dirlist:{dir_list}")
    builder = temp_dir
    for i in range(1, len(dir_list)):
        if dir_list[i] in base_dirs:
            for j in range(i, len(dir_list)):
                builder += dir_list[j] + "/"
    print(f"builder:{builder}")
    return builder


class Watch:
    def __init__(self):
        self.watch_manager = pyinotify.WatchManager()
        self.event_notifier = pyinotify.Notifier(self.watch_manager, EventProcessor())

        def process_generator(cls, method):
            def _method_name(asdf, event):
                if method != "default" and ".part" not in event.pathname and ".kate-swp" not in event.pathname:
                    target = "Directory" if "IN_ISDIR" in event.maskname else "File"
                    path = os.path.split(event.pathname)[0]
                    tpath = trim_path(path)
                    name = os.path.split(event.pathname)[-1]
                    if "IN_CREATE" in event.maskname:
                        print(f"{target} {name} created in {path}")
                        if target == "Directory":
                            self.add_watched(event.pathname, True)
                        else:
                            print(f"tpath:{tpath + name + current_file_version(tpath + name)}")
                            shutil.copy2(event.pathname, tpath + name + current_file_version(tpath + name))
                    elif "IN_MOVED_FROM" in event.maskname:
                        print(f"{target} {name} moved from {path}")
                    elif "IN_CLOSE_WRITE" in event.maskname:
                        print(f"{target} {name} changed in {path}")
                        shutil.copy2(event.pathname, tpath + name + current_file_version(tpath + name))
                    elif "IN_DELETE" in event.maskname:
                        print(f"{target} {name} deleted in {path}")
                    elif "IN_MOVED_TO" in event.maskname:
                        print(f"{target} {name} moved to {path}")
                        if target == "Directory":
                            self.add_watched(event.pathname, True)
                        else:
                            shutil.copy2(event.pathname, tpath + name + current_file_version(tpath + name))

            _method_name.__name__ = "process_{}".format(method)
            setattr(cls, _method_name.__name__, _method_name)

        for method in EventProcessor._methods:
            process_generator(EventProcessor, method)

    def add_watched(self, path, recursive):
        if not os.path.exists(path):
            print(f"{path} doesnt exist")
            return
        name = str(os.path.split(path)[-1])
        if os.path.isdir(path):
            shutil.copytree(path, trim_path(path) + name)
        else:
            shutil.copy2(path, temp_dir + name + current_file_version(name))
        watch_this = os.path.relpath(path)
        self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)
        if recursive:
            for roots, dirs, files in os.walk(path):
                watch_this = os.path.relpath(roots)
                self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)
        else:
            watch_this = os.path.relpath(path)
            self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)
        for dirs in os.listdir(temp_dir):
            if dirs not in base_dirs:
                base_dirs.append(dirs)


    def start(self):
        self.event_notifier.loop()

    def stop(self):
        self.event_notifier.stop()
