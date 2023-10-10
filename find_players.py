import re
import requests
from threading import Thread
import os
import requests
from selenium import webdriver
import time

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
URL = "https://servers-frontend.fivem.net/api/servers/streamRedir/"

print("Getting all FiveM servers.....\n")

data = requests.get(URL, headers=headers).text

file = open("exported_data.txt", "w+", encoding="utf-8", errors="ignore"); file.write(data); file.close()

print("Written all FiveM servers to: exported_data.txt....\n")

file = open("error_list.txt", "w+"); file.close(); file = open("anomalous_ips.txt", "w+"); file.close()

target_player_name = input("Input target player name (regex lower match): ")

number_of_threads = 300
server_timeout = 5

servers = []
found_users = []
threads = []

re_ip = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}\b")

data = open("exported_data.txt", "r", encoding="utf-8", errors="ignore").readlines()

for line in data:
    ip = re.findall(re_ip, line)
    if ip:
        ip = ip[0].strip()
        if ip not in servers:
            servers.append(ip)


def findPlayers(_serverdata):
    global counter
    for ip in _serverdata:
        if len(ip) > 21:
            file = open("anomalous_ips.txt", "a+")
            file.write(f"{ip}\n")
            file.close()
            continue
            
        try:
            data = requests.get(f"http://{ip}/players.json", timeout=server_timeout).json()
            if data:
                for player in data:
                    _playername = player["name"]
                    if target_player_name.lower() in _playername.lower():
                        print(f"Player ({_playername} on server: [{ip}])")
                        found_users.append(f"Player ({_playername} on server: [{ip}])")

                        # os._exit()
                
                print(f"Checking: {ip}")


        except Exception as error:
            error_file = open("error_list.txt", "a+")
            error_file.write(f"Error on ({ip}) > [{error}]\n")
            error_file.close()

divided_server_number = int(len(servers) / number_of_threads)
previous_server_index = 0
next_server_index = divided_server_number

print(f"\nChecking ({len(servers)}) FiveM servers for user: {target_player_name}\n")

time.sleep(3)

for x in range(0, number_of_threads):
    # print(previous_server_index, next_server_index)
    
    if x == number_of_threads-1:
        t = Thread(target=findPlayers, args=(servers[previous_server_index:],))
    
    else:
        t = Thread(target=findPlayers, args=(servers[previous_server_index:next_server_index],))
    
    threads.append(t)

    previous_server_index += divided_server_number
    next_server_index += divided_server_number

for x in threads:
    x.start()

for x in threads:
    x.join()

if found_users:
    for user in found_users:
        print(user)

else:
    print(f"User: ({target_player_name}) not found")
