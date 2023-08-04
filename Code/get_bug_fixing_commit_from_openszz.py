import json
import os
import csv
import codecs
import re
from time import sleep
from tqdm import *
import requests
import glob
import git

#读取apache网站上不同分类的项目json，并保存到字典中，以便后续使用
def get_project_list_in_apache_json(apache_project_json_path):
    with open(apache_project_json_path,'r') as f:
        apache_projects = eval(f.read())
    for cate in apache_projects.keys():
        num = len(apache_projects[cate])
        for i in range(0,num):
            item = apache_projects[cate][i].split(' ')
            length = len(item)
            if(item[length-1]=='(in the Attic)'):
                del apache_projects[cate][i]
                continue
            apache_projects[cate][i] = item[1].lower()
    return apache_projects

def get_bug_fixing_commit_by_openszz(ItemName,git_url,JIRA_url):
    burp0_url = "http://localhost:8081/doAnalysis"
    burp0_cookies = {"Pycharm-5f7bd205": "62a0d717-6bff-44cc-acb8-43fae6eed084",
                     ""
                     "Idea-c2ce355b": "4855567c-1810-44d8-9162-25ba0c40482e",
                     "Phpstorm-7d2b997e": "b0017601-96f8-4de8-b761-bc4bcfbeec09"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                     "Accept-Language": "zh-CN,en;q=0.5", "Accept-Encoding": "gzip, deflate",
                     "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://localhost:8081",
                     "Connection": "close", "Referer": "http://localhost:8081/", "Upgrade-Insecure-Requests": "1",
                     "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin",
                     "Sec-Fetch-User": "?1"}
    burp0_data = {"projectName": "1", "gitUrl": "http:a.github", "jiraUrl": "http:a.github",
                  "email": "1191117394@qq.com"}
    requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)


if __name__ =="__main__":
    #存所有项目名称和分类的json文件
    apache_project_json_path = './apacheProject.txt'
    apache_github_url_base = 'https://github.com/apache/commons-bcel.git'
    JIRA_url_base = 'https://issues.apache.org/jira/projects/BCEL/'
    #读取apache网站上不同分类的项目json，并保存到字典中，以便后续使用
    # 所有项目的列表
    apache_project = get_project_list_in_apache_json(apache_project_json_path)
    print(apache_project)
    sum = 0
    for x in apache_project.keys():
        list =  apache_project[x]
        sum = sum + len(list)
    print(sum)
    apache_project = {'#sql': ['calcite', 'ignite']}
    for cate in apache_project.keys():
        list = apache_project[cate]
        for item in list:
            ItemNameUp = item.upper()
            ItemName = item
            git_url = apache_github_url_base + ItemName + '.git'
            JIRA_url = JIRA_url_base + ItemNameUp + '/'
            get_bug_fixing_commit_by_openszz(ItemNameUp,git_url,JIRA_url)







