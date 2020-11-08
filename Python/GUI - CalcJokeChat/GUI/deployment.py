import os
import time
import requests
from config import Config

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def deploy_new_exe_file():
    # exe_file_name = "Casio_fx-85_CE_X.exe"
    # exe_file_path = os.path.join(WORKING_DIRECTORY, exe_file_name)
    exe_file_path = "Casio_fx-85_CE_X.exe"
    if not os.path.isfile(exe_file_path):
        print("file not there - ", exe_file_path)
        exit(1)

    scp_port = Config.scp_port
    server_ip = Config.server_ip
    server_user = Config.server_user

    server_folder = Config.server_folder

    scp_sending_command = f"scp -P {scp_port} {exe_file_path} {server_user}@{server_ip}:{server_folder}"

    print(scp_sending_command)
    os.system(scp_sending_command)


def announce_new_version_old():
    key_to_save = "last_update"
    timestamp = int(time.time())
    data = {"key_to_save": key_to_save, "data": {"timestamp": timestamp}}
    response = requests.post(Config.OLD_API_URL, json=data)
    print(response)


def announce_new_version():
    version_identifier = "0.1"
    timestamp = time.time()
    details = ""

    data = {
        "version_identifier": version_identifier,
        "timestamp": timestamp,
        "details": details,
    }

    data_to_send = {"data": data}
    response = requests.post(Config.API_URL_LAST_UPDATE, json=data_to_send)
    print(response)


if __name__ == "__main__":
    # deploy_new_exe_file()
    announce_new_version_old()
    announce_new_version()
