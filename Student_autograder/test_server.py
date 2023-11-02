import os
import logging
import subprocess
import socket
import pickle
from utils import *
import sys
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()
    ip = socket.gethostbyname(host_name)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = CHAIN_SERVERS[host_name]
    server_socket.bind((ip, port))
    server_socket.listen(1)
    client_socket, client_address = server_socket.accept()
    directory = get_directory(client_socket)
    while True: 
        signal = receive(client_socket)
        if signal == CAN_SET_UP_STEPPING_STONES_TEST:
            run_can_set_up_stepping_stone_test(directory,client_socket)
        elif signal == ALL_STONES_HIT_DURING_AWGET:
            all_chains_hit_correctly(directory, client_socket)
        elif signal == KILL:
            server_socket.close()
            exit()

def all_chains_hit_correctly(directory, client_socket):
    host_name = socket.gethostname()
    port_of_stone = get_port_of_stone(host_name,directory)
    ip = socket.gethostbyname(host_name)
    process = subprocess.Popen(f'python3 {directory}/{SS} -p {port_of_stone}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,shell=True)
    stdout_fd = process.stdout.fileno()
    stderr_fd = process.stderr.fileno()
    make_non_blocking(stdout_fd)
    make_non_blocking(stderr_fd)
    was_hit, all_lines = get_strings_after_timeout(process,['starting connection to', 'Waiting for file...','Relaying file ...','Goodbye!'],6)
    was_list_chain = any('chainlist is empty' in line for line in all_lines)
    if was_list_chain:
        client_socket.send(SUCCESS_LAST_CHAIN.encode())
    elif was_hit:
        client_socket.send(SUCCESS.encode())
    else:
        client_socket.send(FAIL.encode())
    process.kill()

def run_can_set_up_stepping_stone_test(directory, client_socket):
    host_name = socket.gethostname()
    port_of_stone = get_port_of_stone(host_name,directory)
    ip = socket.gethostbyname(host_name)
    process = subprocess.Popen(f'python3 {directory}/{SS} -p {port_of_stone}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,shell=True)
    stdout_fd = process.stdout.fileno()
    stderr_fd = process.stderr.fileno()
    make_non_blocking(stdout_fd)
    make_non_blocking(stderr_fd)
    start_up_correctly,_ = get_strings_after_timeout(process,['listening on',str(ip),str(port_of_stone)],1)
    if start_up_correctly:
        client_socket.send(SUCCESS.encode())
    else:
        client_socket.send(FAIL.encode())
    process.kill() 
    

def get_directory(client_socket):
    data = client_socket.recv(1024)
    if(data):
        directory = data.decode("utf-8")
        return directory
    
if __name__ == "__main__":
    main()