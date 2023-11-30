import os
import subprocess
import time


import sys
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)

from utils import *

def check_files_for_string(file_list, search_string):
    for file_name in file_list:
        try:
            with open(file_name, 'r') as file:
                file_contents = file.read()
                if search_string not in file_contents:
                    return False
        except FileNotFoundError:
            # Handle the case where the file doesn't exist
            return False
    return True

def awget_error_chaingang(directory):
    args = f"www.google.com -c {directory}/{DEFAULT_CHAIN_FILE}"
    if DEBUG:
        print(f'Running: python3 {directory}/{AWGET} {args}')
    process = subprocess.Popen(f'python3 {directory}/{AWGET} {args}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    stdout_fd = process.stdout.fileno()
    stderr_fd = process.stderr.fileno()
    make_non_blocking(stdout_fd)
    make_non_blocking(stderr_fd)
    time.sleep(2)
    stdout = process.stdout.readlines()
    stderr = process.stderr.readlines()
    if DEBUG:
        print(f'[DEBUG]: STDOUT: {stdout}')
        print(f'[DEBUG]: STDERR: {stderr}')
    return seen_stones(stdout)

def can_set_up_stepping_stones(test_servers):
    send_to_all_test_servers(test_servers, CAN_SET_UP_STEPPING_STONES_TEST)
    time.sleep(1)
    results_from_test = read_from_test_servers(test_servers)
    return all(result == SUCCESS for result in results_from_test)


def correct_return_for_all_chains_hit(lst):
    return lst.count(SUCCESS_LAST_CHAIN) == 1 and all(item == SUCCESS for item in lst if item != SUCCESS_LAST_CHAIN)

def all_stones_hit_during_awget(directory,test_servers):
    send_to_all_test_servers(test_servers, ALL_STONES_HIT_DURING_AWGET)
    time.sleep(3)
    # need to run awget 
    args = f"www.google.com -c {directory}/{DEFAULT_CHAIN_FILE}"
    if DEBUG:
        print(f'Running: python3 {directory}/{AWGET} {args}')
    process = subprocess.Popen(f'python3 {directory}/{AWGET} {args}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    results_from_test = read_from_test_servers(test_servers)
    most_recent_file = get_most_recently_modified_file('.')
    stdout_fd = process.stdout.fileno()
    stderr_fd = process.stderr.fileno()
    make_non_blocking(stdout_fd)
    make_non_blocking(stderr_fd)
    time.sleep(2)
    stdout = process.stdout.readlines()
    stderr = process.stderr.readlines()
    if DEBUG:
        print(f'[DEBUG]: STDOUT: {stdout}')
        print(f'[DEBUG]: STDERR: {stderr}')
    if not any(word in most_recent_file for word in SAFE_FILES) :
        os.remove(most_recent_file)
    return correct_return_for_all_chains_hit(results_from_test)
