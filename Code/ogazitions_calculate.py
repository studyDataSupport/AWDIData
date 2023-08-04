import json
from typing import List
from anyio import sleep
import requests
import os
import glob
import tqdm


def get_orgs_distribute(delelopers: List, file):
    m = {}
    s1 = set()
    s2 = set()
    for i in delelopers:
        s2.add(i)
    access_token = "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"
    headers = {
        "Authorization": f"token {access_token}"
    }
    for username in tqdm.tqdm(developer_username):
        # 发送 API 请求
        response = requests.get(f"https://api.github.com/users/{username}/orgs", headers=headers)

        # 解析响应数据
        if response.status_code == 200:
            user_data = response.json()
            for org in user_data:
                if org['login'] not in m:
                    m[org['login']] = [username]
                    s1.add(username)
                else:
                    m[org['login']].append(username)
        else:
            print(f"Error: {response.status_code}")
    print(s2 - s1)
    # with open(file+"-3.txt", 'w') as f:
    #     json.dump(m, f, indent=4)


files = glob.glob('*.json')
for file in files:
    handle = json.load(open(file))
    developer_username = []
    for i in handle['improved_daily_long_time_error_prone_developer']:
        developer_username.append(i.split('--')[-1])
    print(developer_username)
    get_orgs_distribute(developer_username, file)
    exit(0)



