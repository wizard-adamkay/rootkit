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


def current_file_version(tpath):
    i = 0
    while True:
        if not os.path.exists(tpath + str(i)):
            return str(i)
        i += 1


temp_dir = "/var/tmp/.hiding/"
base_dirs = []

# needs fixing
def add_path(path):
    tpath = trim_path(path)
    # name = os.path.split(path)[-1]
    if not os.path.isdir(path):
        if tpath[-1] == "/":
            tpath = tpath[0:-1]
        print(f"adding to {tpath}")
        shutil.copy2(path, tpath + current_file_version(tpath))
    else:
        if os.path.exists(tpath):
            print(f"paths listed for {path}: {os.listdir(path)}")
            for dir in os.listdir(path):
                add_path(path+"/"+dir)
        else:
            shutil.copytree(path, tpath)


def trim_path(path):
    print(f"\ninitial path: {path}")
    path = os.path.normpath(path)
    print(f"norm path: {path}")
    dir_list = path.split(os.sep)
    print(f"dir list: {dir_list}")
    builder = temp_dir
    found = False
    print(f"base dirs: {base_dirs}")
    for i in range(1, len(dir_list)):
        print(f"comparing {dir_list[i]}")
        if dir_list[i] in base_dirs:
            found = True
            print(f"found {dir_list[i]}")
            for j in range(i, len(dir_list)):
                print(f"adding {dir_list[j]} to string builder")
                builder += dir_list[j] + "/"
            break
    if not found:
        builder += os.path.split(path)[-1]

    print(f"builder: {builder}")
    return builder


class Watch:
    def __init__(self):
        self.watch_manager = pyinotify.WatchManager()
        self.event_notifier = pyinotify.Notifier(self.watch_manager, EventProcessor())
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        else:
            for dirs in os.listdir(temp_dir):
                if dirs not in base_dirs:
                    base_dirs.append(dirs)

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
                        else:
                            add_path(event.pathname)
                    elif "IN_MOVED_FROM" in event.maskname:
                        print(f"{target} {name} moved from {path}")
                    elif "IN_CLOSE_WRITE" in event.maskname:
                        print(f"{target} {name} changed in {path}")
                        add_path(event.pathname)
                    elif "IN_DELETE" in event.maskname:
                        print(f"{target} {name} deleted in {path}")
                    elif "IN_MOVED_TO" in event.maskname:
                        print(f"{target} {name} moved to {path}")
                        if target == "Directory":
                            self.add_watched(event.pathname, True)
                        else:
                            add_path(event.pathname)

            _method_name.__name__ = "process_{}".format(method)
            setattr(cls, _method_name.__name__, _method_name)

        for method in EventProcessor._methods:
            process_generator(EventProcessor, method)

    def add_watched(self, path, recursive):
        if temp_dir in path:
            print(f"cannot watch the temp dir")
            return
        if not os.path.exists(path):
            print(f"{path} doesnt exist")
            return
        if recursive:
            for roots, dirs, files in os.walk(path):
                watch_this = os.path.relpath(roots)
                self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)
        else:
            watch_this = os.path.relpath(path)
            self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS)
        print(f"add_watched adding path: {path}")
        add_path(path)
        for dirs in os.listdir(temp_dir):
            if dirs not in base_dirs:
                base_dirs.append(dirs)

    def start(self):
        self.event_notifier.loop()

    def stop(self):
        self.event_notifier.stop()
