import os
import subprocess
from the_tests import *
from utils import *

def main():
    grade_files("..")

def write_report(text, file_path):
    try:
        with open(f'{file_path}/awget_project_report.txt', "w") as file:
            file.write(text)
    except Exception as e:
        print(f"An error occurred: {e}")

def grade_files(directory_path):
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return
    for filename in os.listdir(directory_path):
        item_path = os.path.abspath(os.path.join(directory_path, filename))
        if os.path.isdir(item_path):
           report = run_tests(item_path)
           write_report(report,item_path)
           break

def set_up_test_servers():
    chains = get_chains()
    servers = []
    for ip, host_name, _ in chains:
        test_server=os.path.abspath("test_server.py")
        test_server_process = None
        if not DEBUG:
            test_server_process = subprocess.Popen(f'ssh {host_name} \"python3 {test_server}\"',stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            time.sleep(3)
        test_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = CHAIN_SERVERS[host_name]
        test_server_socket.connect((ip, port))
        servers.append((test_server_socket,test_server_process,ip))
    time.sleep(3)
    return servers
    
def run_tests(directory):
    report = ""
    if not DEBUG:
        # Want to keep current File to debug with 
        generate_chain_file()

    printing_not_buffered = check_files_for_string([SS,AWGET], "sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)")
    if printing_not_buffered:
        report += f"[Buffered Prinitng] Buffer for prints set to 1: PASSED \n\n"
    else:
        report += f"[Buffered Prinitng] Buffer for prints set to 1: FAIL\n\n"


    able_to_reuse_port = check_files_for_string([SS,AWGET], "socket.SO_REUSEADDR")
    if able_to_reuse_port:
        report += f"[Can reuse Port] SO_REUSEADDR is seen (does not check if used correctly): PASSED \n\n"
    else:
        report += f"[Can reuse Port] need to be able to reuse port in case of restart: FAIL\n\n"

    passed_awget_error_chaingang_arg = awget_error_chaingang(directory)

    if passed_awget_error_chaingang_arg:
        report += f"[Chaingang] Stepping stones are all listed out, meaning read in correctly: PASSED \n\n"
    else:
        report += f"[Chaingang] Stepping stones not printed/read correctly: FAIL\n\n"
    
    # TESTS SETUP 
    test_servers = set_up_test_servers()
    try:
        send_to_all_test_servers(test_servers,directory)
        time.sleep(2)
        passed_can_set_up_stepping_stones = can_set_up_stepping_stones(test_servers)
        if passed_can_set_up_stepping_stones:
            report += f"[Set up Chains] All chains set up listening correctly: PASSED\n\n"
        else:
            report += f"[Set up Chains] Not all chains set up listening correctly: FAIL\n\n"

        passed_can_set_up_stepping_stones = all_stones_hit_during_awget(directory,test_servers)
        if passed_can_set_up_stepping_stones:
            report += f"[Chains Hit] All chains hit correctly: PASSED\n\n"
        else:
            report += f"[Chains Hit] Not all chains hit correctly:  FAIL\n\n"
    except Exception as e:
        print(f'Got exceptions: {e}')
    kill_test_severs(test_servers)
    print('Finished Running tests: Find results at: "awget_project_report.txt"')
    print('killed test_servers')
    # set up chains correctly 
    # set up test servers, 



    return report 
if __name__ == "__main__":
    main()