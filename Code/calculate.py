import json
from collections import Counter
from time import strftime

import scipy.stats
import pandas as pd
from numpy import *
import csv
import codecs
import numpy as np
import re
import os
import math
from git import Repo
import git
import datetime
import json
import time
import requests
import os
import datetime

csv.field_size_limit(500 * 1024 * 1024)
start = time.perf_counter()

def request_get_json(url,query, headers):
    ret_code = 0
    while ret_code != 200 and ret_code != 404:
        try:
            res = requests.post(url=url, json={"query": query}, headers=headers)
            ret_code = res.status_code
            #print(ret_code)
            #print(res.text)
            while ret_code == 403:
                nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                #print('sleeping now. from '+ nowtime)
                datetime.time.sleep(1800) #sleap a half an hour
                res = requests.get(url=url, headers=headers)
                ret_code = res.status_code

            # if ret_code != 200:  # ret_code != 200表明http请求失败，可以考虑进行处理
                # print(ret_code)
                # pass
        except Exception as e:
            print("except:",e)
            pass
    return res.json()


def query_user(token, name, api):
    header = {'Authorization': f'token {token}', 'Accept': f'application/vnd.github.starfox-preview+json'}
    query = """{\n""" + f"""user(login:"{name}")""" + """{
            login
            createdAt
            repositoriesContributedTo(first:100,includeUserRepositories:true){
                totalCount
                nodes{
                    nameWithOwner
                    isFork
                    url
                    languages(first:100){
                        nodes{
                            name
                        }
                    }
                    stargazerCount
                    watchers{
                      totalCount
                    }
                    forkCount
                }
            }
        }
    }"""
    # print(query)
    response = request_get_json(api, query, headers=header)
    if(response['data']['user'] == None):
        return ''
    json_data = response['data']['user']
    # print(json_data)
    # json_data['totalPublicContributions'] = json_data['contributionsCollection']['totalRepositoryContributions'] + \
    #                                   json_data['contributionsCollection']['totalCommitContributions'] + \
    #                                   json_data['contributionsCollection']['totalIssueContributions'] + \
    #                                   json_data['contributionsCollection']['totalPullRequestContributions'] + \
    #                                   json_data['contributionsCollection']['totalPullRequestReviewContributions']
    # json_data['totalPrivateContributions'] = json_data['contributionsCollection']['contributionCalendar']['totalContributions'] - json_data['totalPublicContributions']
    return json_data


def request_language(user_info, token):
    header = {'Authorization': f'token {token}'}
    api_url = 'https://api.github.com/repos/'
    for repo in user_info['nodes']:
        repo_owner = repo['url'].split('/')[3]
        repo_name = repo['url'].split('/')[4]
        url = api_url + repo_owner + '/' + repo_name + '/languages'
        language_info = requests.get(url=url, headers=header).json()
        sum_codeLine = sum(language_info.values())
        for node in repo['languages']['nodes']:
            language = node['name']
            node['codeLine'] = language_info[language]
            node['proportion'] = format(node['codeLine'] / sum_codeLine, '.2%')

    for repo in user_info['nodes']:
        repo_owner = repo['url'].split('/')[3]
        repo_name = repo['url'].split('/')[4]
        url = api_url + repo_owner + '/' + repo_name + '/languages'
        language_info = requests.get(url=url, headers=header).json()
        sum_codeLine = sum(language_info.values())
        for node in repo['languages']['nodes']:
            language = node['name']
            node['codeLine'] = language_info[language]
            node['proportion'] = format(node['codeLine'] / sum_codeLine, '.2%')

    return user_info


def get_error(Github_token):
    api = "https://api.github.com/graphql"
    url_list = ['https://github.com/metaswirl']
    for input_user_url in url_list:
        user_name = input_user_url.split('/')[3]
        user_info = query_user(Github_token, user_name, api)
        if (user_info == ''):
            continue
        user_info = request_language(user_info, Github_token)
        user_info['user_url'] = input_user_url
        json_fn = './user_info/' + user_name + '.json'
        with open(json_fn, 'w') as f:
            json.dump(user_info, f, indent=4)
        print("Saved user information to " + json_fn)


def get_origin_commit(item_commit_path,git,cate,item_name):
    csvFile = open(item_commit_path, 'r', encoding="ISO-8859-1")
    csv_reader = csv.DictReader(csvFile)

    repo = Repo(git)
    global hash_file_list,commiter_start_time,commiter_end_time,changeFiles_hashList,changeFiles_commiter,commiter_commit_number,commiter_hashList,hashList_commiter
    print("开始获取本地所有commit相关信息：")

    # 计算每个commit中修改的文件
    hash_file_list = {}

    # 项目开始时间
    item_start_time = ''

    # 每个开发者最开始贡献时间和最后贡献时间
    commiter_start_time = {}
    commiter_end_time = {}

    # 计算出修改过该文件的hashList和commmiters
    changeFiles_hashList = {}
    changeFiles_commiter = {}

    # 每个开发者所有author的commit数量
    commiter_commit_number = {}
    commiter_hashList = {}
    hashList_commiter = {}

    for c in csv_reader:
        committer = cate+'--'+item_name+'--'+c['authors']
        hashValue = c['hash']

        git_c = repo.commit(hashValue)
        if (len(git_c.parents) > 1):
            continue

        if(committer in commiter_commit_number.keys()):
            commiter_commit_number[committer] += 1
        else:
            commiter_commit_number[committer] = 1

        hashList_commiter[hashValue] = committer
        if (committer in commiter_hashList.keys()):
            commiter_hashList[committer].append(hashValue)
        else:
            commiter_hashList[committer] = [hashValue]
        #print("是否相等：")
        #print(len(commiter_hashList[committer]))
        #print(commiter_commit_number[committer])
        # 获得完成commit的时间
        commit_time = git_c.authored_datetime.strftime('%Y-%m-%d').split('-')
        year = commit_time[0]
        mon = commit_time[1]
        day = commit_time[2]
        year_month = datetime.datetime(int(year), int(mon), int(day), 0, 0, 0)

        hashList_time[hashValue] = year_month

        if (item_start_time == ''):
            item_start_time = year_month
        elif (item_start_time > year_month):
            item_start_time = year_month

        if (committer in commiter_start_time.keys()):
            if (year_month < commiter_start_time[committer]):
                commiter_start_time[committer] = year_month
        else:
            commiter_start_time[committer] = year_month

        if (committer in commiter_end_time.keys()):
            if (year_month > commiter_end_time[committer]):
                commiter_end_time[committer] = year_month
        else:
            commiter_end_time[committer] = year_month


        # 计算每个commit中修改的文件
        List_files = str(c['changed_files']). \
            replace("[", "").replace("]", "") \
            .split(",")
        List_changed_files = []
        for file in List_files:
            file = file.strip()
            List_changed_files.append(file)
        hash_file_list[hashValue] = List_changed_files

        # 计算出修改过该文件的hashList和commmiters
        for fileName in List_changed_files:
            if (fileName in changeFiles_hashList.keys()):
                changeFiles_hashList[fileName].append(c['hash'])
            else:
                changeFiles_hashList[fileName] = [c['hash']]
            if (fileName in changeFiles_commiter.keys()):
                changeFiles_commiter[fileName].append(committer)
            else:
                changeFiles_commiter[fileName] = [committer]


def get_number_of_introduce_bugs_per_commit(inducing_commits):
    global commiter_bug_number,number_of_introduce_bugs_per_commit,hashList_commiter,commiter_commit_number,commiter_bug_hash
    # 每个开发者引入bug的数量
    commiter_bug_number = {}
    # 开发者平均每个commit中引入bug的数量
    number_of_introduce_bugs_per_commit = {}
    # x：引入同一个bug的所有inducing commit hash列表
    for x in inducing_commits:
        commiter_l = []
        for hash in x:
            try:
                commiter = hashList_commiter[hash]
            except:
                continue
            # 如果这个commiter对这个bug的引入commit已经被记录，那么不重复记录
            if(commiter in commiter_l):
                continue
            if(commiter in commiter_bug_number.keys()):
                commiter_bug_number[commiter] += 1
                commiter_bug_hash[commiter].append(hash)
            else:
                commiter_bug_number[commiter] = 1
                commiter_bug_hash[commiter] = [hash]
            commiter_l.append(commiter)

    for cer in commiter_commit_number.keys():
        # 如果该开发者引入bug
        if(cer in commiter_bug_number.keys()):
            number_of_introduce_bugs_per_commit[cer] = 1.0 * commiter_bug_number[cer]/commiter_commit_number[cer]
        else:
            number_of_introduce_bugs_per_commit[cer] = 0

    #print(number_of_introduce_bugs_per_commit)
    #print(commiter_bug_number)


def get_bug_introducing_commit_rate():
    global bug_introducing_commit_rate,number_inducing_commit,inducing_commits,hashList_commiter,commiter_commit_number,commiter_bug_number,commiter_bug_commit_hash
    # 引入bug的commit比例
    bug_introducing_commit_rate = {}
    # 引入bug的commit数量
    number_inducing_commit = {}
    #print(inducing_commits)
    c_list = []

    for i in inducing_commits:
        for hash in i:
            # 如果一个commit induce了好几个bug，他也还是一个引入bug的commit，不重复计算，保存一下，RQ4要用
            if(hash in c_list):
                continue
            try:
                commiter = hashList_commiter[hash]
            except:
                continue
            if (commiter in number_inducing_commit.keys()):
                number_inducing_commit[commiter] += 1
                commiter_bug_commit_hash[commiter].append(hash)
            else:
                number_inducing_commit[commiter] = 1
                commiter_bug_commit_hash[commiter]=[hash]
            c_list.append(hash)

    for cer in commiter_commit_number.keys():
        if (cer in commiter_bug_number.keys()):
            bug_introducing_commit_rate[cer] = 1.0 * number_inducing_commit[cer] / commiter_commit_number[cer]
        else:
            bug_introducing_commit_rate[cer] = 0
    #print(bug_introducing_commit_rate)

def outputRQ1(output_path):
    global changeFiles_commiter,number_of_introduce_bugs_per_commit,bug_introducing_commit_rate,commiter_bug_number,number_inducing_commit,commiter_commit_number
    commit_metrics = {}
    commiter_files = {}
    for file in changeFiles_commiter.keys():
        l = changeFiles_commiter[file]
        for c in l:
            if(c not in commiter_files.keys()):
                commiter_files[c] = [file]
            else:
                if(file not in commiter_files[c]):
                    commiter_files[c].append(file)

    commit_metrics['item_start_time'] = item_start_time
    commit_metrics['commiter_files'] = commiter_files
    commit_metrics['number_of_introduce_bugs_per_commit'] = dict(sorted(number_of_introduce_bugs_per_commit.items(),key = lambda x :x[1],reverse=True))
    commit_metrics['bug_introducing_commit_rate'] = dict(sorted(bug_introducing_commit_rate.items(),key = lambda x :x[1],reverse=True))
    commit_metrics['commiter_bug_number'] = dict(sorted(commiter_bug_number.items(),key = lambda x :x[1],reverse=True))
    commit_metrics['number_inducing_commit'] = dict(sorted(number_inducing_commit.items(),key = lambda x :x[1],reverse=True))
    commit_metrics['commiter_commit_number'] = dict(sorted(commiter_commit_number.items(),key = lambda x :x[1],reverse=True))
    commit_metrics['team_developer_num'] = len(commiter_commit_number)
    print("RQ1指标计算完毕，输出文件")
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(commit_metrics, f, indent=4)
    print("RQ1指标输出文件完毕")


def get_yuzhi_bug_rate_and_commit_rate(cate):
    global all_cate_dict,number_of_introduce_bugs_per_commit,bug_introducing_commit_rate,commiter_bug_number,number_inducing_commit,commiter_commit_number
    sum_bug_rate = 0
    sum_bug_commit_rate = 0
    len_bug_rate = 0
    len_bug_commit_rate = 0
    # 计算阈值的数值列表
    number_of_introduce_bugs_per_commit_yuzhi_list = []
    bug_introducing_commit_rate_yuzhi_list = []
    for item_name in all_cate_dict[cate]:
        RQ1_path = './RQ1/' + cate + '/' + item_name + "_metrics.json"
        with open(RQ1_path, 'r', encoding='utf8') as fp:
            json_data = json.load(fp)  # 读取json文件
        number_of_introduce_bugs_per_commit=json_data['number_of_introduce_bugs_per_commit']
        bug_introducing_commit_rate=json_data['bug_introducing_commit_rate']
        commiter_bug_number=json_data['commiter_bug_number']
        number_inducing_commit=json_data['number_inducing_commit']
        commiter_commit_number=json_data['commiter_commit_number']


        for c in json_data['number_of_introduce_bugs_per_commit'].keys():
            sum_bug_rate += json_data['number_of_introduce_bugs_per_commit'][c]
            number_of_introduce_bugs_per_commit_yuzhi_list.append(json_data['number_of_introduce_bugs_per_commit'][c])

        len_bug_rate+=len(json_data['number_of_introduce_bugs_per_commit'])

        for c in json_data['bug_introducing_commit_rate'].keys():
            sum_bug_commit_rate += json_data['bug_introducing_commit_rate'][c]
            bug_introducing_commit_rate_yuzhi_list.append(json_data['bug_introducing_commit_rate'][c])

        len_bug_commit_rate+=len(json_data['bug_introducing_commit_rate'])
    print(all_cate_dict[cate])
    cate_aver_bug_rate = sum_bug_rate / len_bug_rate
    cate_aver_bug_commit_rate = sum_bug_commit_rate / len_bug_commit_rate

    #计算90%的阈值是多少
    q_percent = 50
    number_of_introduce_bugs_per_commit_yuzhi_list = [x for x in number_of_introduce_bugs_per_commit_yuzhi_list if x != 0]
    bug_introducing_commit_rate_yuzhi_list = [x for x in bug_introducing_commit_rate_yuzhi_list if x != 0]
    if(len(number_of_introduce_bugs_per_commit_yuzhi_list)==0):
        number_of_introduce_bugs_per_commit_yuzhi=100
    else:
        number_of_introduce_bugs_per_commit_yuzhi = np.percentile(number_of_introduce_bugs_per_commit_yuzhi_list, q_percent)
    if (len(bug_introducing_commit_rate_yuzhi_list) == 0):
        bug_introducing_commit_rate_yuzhi = 100
    else:
        bug_introducing_commit_rate_yuzhi = np.percentile(bug_introducing_commit_rate_yuzhi_list, q_percent)

    return number_of_introduce_bugs_per_commit_yuzhi,bug_introducing_commit_rate_yuzhi

def get_error_prone_developer(cate_aver_bug_rate, cate_aver_bug_commit_rate):
    global number_of_introduce_bugs_per_commit,bug_introducing_commit_rate,high_bug_rate_error_prone_developer,high_bug_commit_rate_error_prone_developer
    high_bug_rate_error_prone_developer = {}
    high_bug_commit_rate_error_prone_developer = {}

    for c in number_of_introduce_bugs_per_commit.keys():
        if number_of_introduce_bugs_per_commit[c]>=cate_aver_bug_rate:
            high_bug_rate_error_prone_developer[c] = number_of_introduce_bugs_per_commit[c]

    for c in bug_introducing_commit_rate.keys():
        if bug_introducing_commit_rate[c] >= cate_aver_bug_commit_rate:
            high_bug_commit_rate_error_prone_developer[c] = bug_introducing_commit_rate[c]

def RQ2(cate_aver_bug_rate, cate_aver_bug_commit_rate):
    get_error_prone_developer(cate_aver_bug_rate, cate_aver_bug_commit_rate)


def outputRQ2(item_name,output_path,cate_aver_bug_rate,cate_aver_bug_commit_rate,cate):
    global RQ5_error_prone_developer,error_prone_developer,high_bug_rate_error_prone_developer,high_bug_commit_rate_error_prone_developer,commiter_commit_number,number_of_introduce_bugs_per_commit,bug_introducing_commit_rate
    bug_rate_path = './number_of_introduce_bugs_per_commit/'+cate+'/'+item_name+'.csv'
    bug_commit_rate_path = './bug_introducing_commit_rate/'+cate+'/'+item_name+'.csv'
    commit_metrics = {}
    error_prone_developer = []
    commit_metrics['cate'] = cate
    commit_metrics[cate+'-cate_aver_bug_rate'] = cate_aver_bug_rate
    commit_metrics[cate+'-cate_aver_bug_commit_rate'] = cate_aver_bug_commit_rate
    commit_metrics['high_bug_rate_error_prone_developer_number'] = len(high_bug_rate_error_prone_developer)
    commit_metrics['high_bug_commit_rate_error_prone_developer_number'] = len(high_bug_commit_rate_error_prone_developer)
    commit_metrics['high_bug_rate_error_prone_developer'] = high_bug_rate_error_prone_developer
    commit_metrics['high_bug_commit_rate_error_prone_developer'] = high_bug_commit_rate_error_prone_developer
    for d in high_bug_rate_error_prone_developer.keys():
        if d in high_bug_commit_rate_error_prone_developer.keys():
            error_prone_developer.append(d)
    commit_metrics['error_prone_developer_num'] = len(error_prone_developer)
    commit_metrics['error_prone_developer'] = error_prone_developer
    RQ5_error_prone_developer[cate][item_name] = error_prone_developer
    #print(item_name)
    try:
        commit_metrics['error_prone_developer_team_rate'] = len(error_prone_developer)/len(commiter_commit_number)
    except:
        print(item_name)
    commit_metrics['team_developer_num'] = len(commiter_commit_number)
    print("RQ2指标计算完毕，输出文件")
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(commit_metrics, f, indent=4)

    # 输出csv，用来画图
    with open(bug_rate_path, 'w', newline='') as csvfile:
        didi = dict(sorted(number_of_introduce_bugs_per_commit.items(), key=lambda x: x[1]))
        fieldnames = list(didi.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(didi)

    with open(bug_commit_rate_path, 'w', newline='') as csvfile:
        mimi = dict(sorted(bug_introducing_commit_rate.items(), key=lambda x: x[1]))
        fieldnames = list(mimi.keys())
        # print(fieldnames)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(mimi)
    print("RQ2输出文件完毕")


def RQ3():
    global changeFiles_hashList,changeFiles_commiter,error_prone_developer
    all_file_num = len(changeFiles_hashList)
    error_developer_file_rate = {}
    for file in changeFiles_commiter.keys():
        ll = set(changeFiles_commiter[file])
        for c in ll:
            if c not in error_prone_developer:
                continue
            if c in error_developer_file_rate.keys():
                error_developer_file_rate[c] += 1
            else:
                error_developer_file_rate[c] = 1

    for x in error_developer_file_rate.keys():
        if (error_developer_file_rate[x] / all_file_num < 1):
            error_developer_file_rate[x] = error_developer_file_rate[x] / all_file_num
            continue
        error_developer_file_rate[x] = error_developer_file_rate[x]/all_file_num
    return all_file_num, error_developer_file_rate

def outputRQ3(item_name,output_path,all_file_num,error_developer_file_rate,cate):
    global error_prone_developer,high_bug_rate_error_prone_developer,high_bug_commit_rate_error_prone_developer,commiter_commit_number,daily_error_prone_developer,high_bug_rate_error_prone_developer

    file_bug_path = './file_bug_paint_RQ3/'+cate+'/'+item_name+'.csv'
    real_file_bug_path = './real_file_bug_paint_RQ3/'+cate+'/'+item_name+'.csv'

    print('输出错误倾向开发者负责文件的比例和那两个bug相关的值')
    # 输出csv，用来画图
    with open(file_bug_path, 'w', newline='') as csvfile:
        error_developer_file_rate = dict(sorted(error_developer_file_rate.items(),key = lambda x :x[1]))
        fieldnames = list(error_developer_file_rate.keys())
        #print(fieldnames)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(error_developer_file_rate)
        o = {}
        for a in error_developer_file_rate.keys():
            if a in error_prone_developer:
                o[a] = high_bug_rate_error_prone_developer[a]
        writer.writerow(o)
        #print(o.keys())
        o = {}
        for a in error_developer_file_rate.keys():
            if a in error_prone_developer:
                o[a] = high_bug_commit_rate_error_prone_developer[a]
        writer.writerow(o)
        #print(o.keys())

    # 输出真正对项目维护的人员，以commit数量是否大于5个来判断
    with open(real_file_bug_path, 'w', newline='') as csvfile:
        error_developer_file_rate = dict(sorted(error_developer_file_rate.items(),key = lambda x :x[1]))
        listt = {}
        for ii in error_developer_file_rate.keys():
            if(commiter_commit_number[ii]>5):
                listt[ii]=error_developer_file_rate[ii]
        fieldnames = listt.keys()
        daily_error_prone_developer = []
        daily_error_prone_developer = listt.keys()
        #print(fieldnames)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(listt)
        o = {}
        for a in listt.keys():
            o[a] = high_bug_rate_error_prone_developer[a]
        writer.writerow(o)
        #print(o.keys())
        o = {}
        for a in listt.keys():
            o[a] = high_bug_commit_rate_error_prone_developer[a]
        writer.writerow(o)
        #print(o.keys())

    commit_metrics = {}
    commit_metrics['all_file_num'] = all_file_num
    commit_metrics['error_developer_file_rate'] = error_developer_file_rate
    commit_metrics['daily_error_prone_developer'] = list(daily_error_prone_developer)
    commit_metrics['number_daily_error_prone_developer'] = len(list(daily_error_prone_developer))
    print("RQ3指标计算完毕，输出文件")
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(commit_metrics, f, indent=4)


def RQ4():
    pass

def outputRQ4(cate,item_name, output_path):
    global commiter_time_bug_commit_num,commiter_time_bug_num,commiter_hashList,hashList_time
    global commiter_contribute_time,commiter_start_time,commiter_end_time,item_start_time,daily_error_prone_developer,high_bug_rate_error_prone_developer
    global RQ5_daily_long_time_error_prone_developer,daily_long_time_error_prone_developer,high_bug_commit_rate_error_prone_developer,commiter_time_commit_num
    commiter_contribute_time = {}
    for cc in commiter_start_time.keys():
        if (cc in commiter_end_time.keys()):
            zzz1=commiter_end_time[cc]
            zzz2=commiter_start_time[cc]
            ss = str(zzz1 - zzz2)
            #print(ss)
            if(ss=='0:00:00'):
                commiter_contribute_time[cc]=0
                continue
            commiter_contribute_time[cc] = int(ss.split(' ')[0])
    commit_metrics = {}
    commit_metrics['item_start_time'] = item_start_time
    commit_metrics['commiter_start_time'] = commiter_start_time
    commit_metrics['commiter_end_time'] = commiter_end_time
    commit_metrics['commiter_contribute_time'] = commiter_contribute_time


    real_RQ4_time_bug_path = './real_RQ4_time_bug/'+item_name+'.csv'
    with open(real_RQ4_time_bug_path, 'w', newline='') as csvfile:
        commiter_contribute_time = dict(sorted(commiter_contribute_time.items(),key = lambda x :x[1]))
        listt = {}
        for ii in daily_error_prone_developer:
            if(commiter_contribute_time[ii]>90):
                listt[ii]=high_bug_rate_error_prone_developer[ii]
        fieldnames = listt
        daily_long_time_error_prone_developer = []
        daily_long_time_error_prone_developer = list(listt.keys())
        RQ5_daily_long_time_error_prone_developer[cate][item_name]=daily_long_time_error_prone_developer
        #print(fieldnames)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(listt)
        o = {}
        for a in listt.keys():
            o[a] = high_bug_commit_rate_error_prone_developer[a]
        writer.writerow(o)
        #print(o.keys())

    # 把两个筛选条件筛选过的开发者贡献时间分成四段，找出长时间没有提升的开发者
    commiter_contribute_time1 = {}
    commiter_contribute_time2 = {}
    commiter_contribute_time3 = {}
    commiter_contribute_time4 = {}
    for x in daily_long_time_error_prone_developer:
        jiange = commiter_contribute_time[x]//4
        time1 = (commiter_start_time[x] + datetime.timedelta(days=jiange)).strftime("%Y-%m-%d").split('-')
        year = time1[0]
        mon = time1[1]
        day = time1[2]
        year_month1 = datetime.datetime(int(year), int(mon), int(day), 0, 0, 0)
        time2 = (commiter_start_time[x] + datetime.timedelta(days=jiange*2)).strftime("%Y-%m-%d").split('-')
        year = time2[0]
        mon = time2[1]
        day = time2[2]
        year_month2 = datetime.datetime(int(year), int(mon), int(day), 0, 0, 0)
        time3 = (commiter_start_time[x] + datetime.timedelta(days=jiange*3)).strftime("%Y-%m-%d").split('-')
        year = time3[0]
        mon = time3[1]
        day = time3[2]
        year_month3 = datetime.datetime(int(year), int(mon), int(day), 0, 0, 0)
        commiter_time_commit_num = {
            'time1': 0,
            'time2': 0,
            'time3': 0,
            'time4': 0,
        }
        commiter_time_bug_commit_num = {
            'time1': 0,
            'time2': 0,
            'time3': 0,
            'time4': 0,
        }
        commiter_time_bug_num = {
            'time1': 0,
            'time2': 0,
            'time3': 0,
            'time4': 0,
        }
        for hash in commiter_hashList[x]:
            tt = hashList_time[hash]
            if(commiter_start_time[x] <= tt <= year_month1):
                commiter_time_commit_num['time1'] += 1
            elif(year_month1 < tt <= year_month2):
                commiter_time_commit_num['time2'] += 1
            elif (year_month2 < tt <= year_month3):
                commiter_time_commit_num['time3'] += 1
            elif (year_month3 < tt <= commiter_end_time[x]):
                commiter_time_commit_num['time4'] += 1
        for bug in inducing_commits:
            count1 = 0
            count2 = 0
            count3 = 0
            count4 = 0
            for inducecommit in bug:
                tt = hashList_time[inducecommit]
                if (commiter_start_time[x] <= tt <= year_month1):
                    count1 += 1
                    commiter_time_bug_commit_num['time1'] += 1
                elif (year_month1 < tt <= year_month2):
                    count2 += 1
                    commiter_time_bug_commit_num['time2'] += 1
                elif (year_month2 < tt <= year_month3):
                    count3 += 1
                    commiter_time_bug_commit_num['time3'] += 1
                elif (year_month3 < tt <= commiter_end_time[x]):
                    commiter_time_bug_commit_num['time4'] += 1
                    count4 += 1
            if(count1 != 0):
                commiter_time_bug_num['time1'] += 1
            elif (count2 != 0):
                commiter_time_bug_num['time2'] += 1
            elif (count3 != 0):
                commiter_time_bug_num['time3'] += 1
            elif (count4 != 0):
                commiter_time_bug_num['time4'] += 1
        commiter_contribute_time1[x] = {}
        commiter_contribute_time1[x]['start'] = commiter_start_time[x].strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time1[x]['end'] = year_month1.strftime("%Y-%m-%d %H:%M:%S")
        if(commiter_time_commit_num['time1']==0):
            commiter_contribute_time1[x]['bug_num_per_commit'] = -1
            commiter_contribute_time1[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time1[x]['bug_num_per_commit'] = commiter_time_bug_num['time1']/commiter_time_commit_num['time1']
            commiter_contribute_time1[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time1']/commiter_time_commit_num['time1']

        commiter_contribute_time2[x] = {}
        commiter_contribute_time2[x]['start'] = year_month1.strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time2[x]['end'] = year_month2.strftime("%Y-%m-%d %H:%M:%S")
        if (commiter_time_commit_num['time2'] == 0):
            commiter_contribute_time2[x]['bug_num_per_commit'] = -1
            commiter_contribute_time2[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time2[x]['bug_num_per_commit'] = commiter_time_bug_num['time2'] / commiter_time_commit_num['time2']
            commiter_contribute_time2[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time2'] /commiter_time_commit_num['time2']

        commiter_contribute_time3[x] = {}
        commiter_contribute_time3[x]['start'] = year_month2.strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time3[x]['end'] = year_month3.strftime("%Y-%m-%d %H:%M:%S")
        if (commiter_time_commit_num['time3'] == 0):
            commiter_contribute_time3[x]['bug_num_per_commit'] = -1
            commiter_contribute_time3[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time3[x]['bug_num_per_commit'] = commiter_time_bug_num['time3'] / commiter_time_commit_num['time3']
            commiter_contribute_time3[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time3'] / commiter_time_commit_num['time3']

        commiter_contribute_time4[x] = {}
        commiter_contribute_time4[x]['start'] = year_month3.strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time4[x]['end'] = commiter_end_time[x].strftime("%Y-%m-%d %H:%M:%S")
        if (commiter_time_commit_num['time4'] == 0):
            commiter_contribute_time4[x]['bug_num_per_commit'] = -1
            commiter_contribute_time4[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time4[x]['bug_num_per_commit'] = commiter_time_bug_num['time4'] / commiter_time_commit_num['time4']
            commiter_contribute_time4[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time4'] / commiter_time_commit_num['time4']

    commit_metrics['commiter_contribute_time1'] = commiter_contribute_time1
    commit_metrics['commiter_contribute_time2'] = commiter_contribute_time2
    commit_metrics['commiter_contribute_time3'] = commiter_contribute_time3
    commit_metrics['commiter_contribute_time4'] = commiter_contribute_time4
    for i in commit_metrics['commiter_start_time']:
        commit_metrics['commiter_start_time'][i]=str(commit_metrics['commiter_start_time'][i])
    for i in commit_metrics['commiter_end_time']:
        commit_metrics['commiter_end_time'][i]=str(commit_metrics['commiter_end_time'][i])
    commiter_time_trend = {}

    for y in commiter_contribute_time1.keys():
        commiter_time_trend[y] = {}
        commiter_time_trend[y]['bug_num_per_commit'] = {}
        commiter_time_trend[y]['bug_num_per_commit']['time1'] = commiter_contribute_time1[x]['bug_num_per_commit']
        commiter_time_trend[y]['bug_num_per_commit']['time2'] = commiter_contribute_time2[x]['bug_num_per_commit']
        commiter_time_trend[y]['bug_num_per_commit']['time3'] = commiter_contribute_time3[x]['bug_num_per_commit']
        commiter_time_trend[y]['bug_num_per_commit']['time4'] = commiter_contribute_time4[x]['bug_num_per_commit']
        commiter_time_trend[y]['bug_commit_num_rate'] = {}
        commiter_time_trend[y]['bug_commit_num_rate']['time1'] = commiter_contribute_time1[x]['bug_commit_num_rate']
        commiter_time_trend[y]['bug_commit_num_rate']['time2'] = commiter_contribute_time2[x]['bug_commit_num_rate']
        commiter_time_trend[y]['bug_commit_num_rate']['time3'] = commiter_contribute_time3[x]['bug_commit_num_rate']
        commiter_time_trend[y]['bug_commit_num_rate']['time4'] = commiter_contribute_time4[x]['bug_commit_num_rate']

    commit_metrics['commiter_time_trend'] = commiter_time_trend
    commit_metrics['daily_long_time_error_prone_developer'] = daily_long_time_error_prone_developer


    print("RQ4指标计算完毕，输出文件")
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(commit_metrics, f, indent=4)

    print("RQ4结束")

def outputRQ4_new(cate,item_name, output_path):
    global commiter_time_bug_commit_num,commiter_time_bug_num,commiter_hashList,hashList_time,commiter_commit_number,commiter_bug_hash,commiter_bug_commit_hash
    global commiter_contribute_time,commiter_start_time,commiter_end_time,item_start_time,daily_error_prone_developer,high_bug_rate_error_prone_developer
    global RQ5_daily_long_time_error_prone_developer,daily_long_time_error_prone_developer,high_bug_commit_rate_error_prone_developer,commiter_time_commit_num
    commiter_contribute_time = {}
    for cc in commiter_start_time.keys():
        if (cc in commiter_end_time.keys()):
            zzz1=commiter_end_time[cc]
            zzz2=commiter_start_time[cc]
            ss = str(zzz1 - zzz2)
            #print(ss)
            if(ss=='0:00:00'):
                commiter_contribute_time[cc]=0
                continue
            commiter_contribute_time[cc] = int(ss.split(' ')[0])


    real_RQ4_time_bug_path = './real_RQ4_time_bug/'+cate+'/'+item_name+'.csv'
    with open(real_RQ4_time_bug_path, 'w', newline='') as csvfile:
        commiter_contribute_time = dict(sorted(commiter_contribute_time.items(),key = lambda x :x[1]))
        listt = {}
        nn = {}
        for ii in daily_error_prone_developer:
            if(commiter_contribute_time[ii]>90):
                yy = ii.split('--')
                # print(yy)
                if (yy[2] == ''):
                    # print(111)
                    #xx_dict1.pop(ii)
                    continue
                listt[ii]=commiter_contribute_time[ii]
        fieldnames = listt
        daily_long_time_error_prone_developer = []
        daily_long_time_error_prone_developer = list(listt.keys())
        RQ5_daily_long_time_error_prone_developer[cate][item_name]=daily_long_time_error_prone_developer
        #print(fieldnames)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(listt)
        o = {}
        for a in listt.keys():
            o[a] = high_bug_rate_error_prone_developer[a]
        writer.writerow(o)
        o = {}
        for a in listt.keys():
            o[a] = high_bug_commit_rate_error_prone_developer[a]
        writer.writerow(o)
        #print(o.keys())

    # 把两个筛选条件筛选过的开发者按commit的数量分成四段，找出长时间没有提升的开发者
    commiter_contribute_time1 = {}
    commiter_contribute_time2 = {}
    commiter_contribute_time3 = {}
    commiter_contribute_time4 = {}
    commiter_time_trend = {}
    for x in daily_long_time_error_prone_developer:
        jiange = commiter_commit_number[x]//4
        time1 = jiange
        time2 = jiange*2
        time3 = jiange*3
        time4 = commiter_commit_number[x]
        commiter_time_commit_num = {
            'time1': 0,
            'time2': 0,
            'time3': 0,
            'time4': 0,
        }
        commiter_time_bug_commit_num = {
            'time1': 0,
            'time2': 0,
            'time3': 0,
            'time4': 0,
        }
        commiter_time_bug_num = {
            'time1': 0,
            'time2': 0,
            'time3': 0,
            'time4': 0,
        }
        commiter_hash_list = commiter_hashList[x]
        if(x in commiter_bug_hash.keys()):
            commiter_bug_hash_list = commiter_bug_hash[x]
        else:
            commiter_bug_hash_list = []
        commiter_bug_hash_list=set(commiter_bug_hash_list)
        for i in range(0,len(commiter_hash_list)):
            print(111)
            if(0 <= i < time1):
                commiter_time_commit_num['time1'] += 1
            elif(time1 <= i < time2):
                commiter_time_commit_num['time2'] += 1
            elif (time2 <= i < time3):
                commiter_time_commit_num['time3'] += 1
            elif (time3 < i <= time4):
                commiter_time_commit_num['time4'] += 1

        for bug in commiter_bug_hash_list:
            indexx = commiter_hash_list.index(bug)
            #print(indexx)
            if (0 <= indexx < time1):
                commiter_time_bug_num['time1'] += 1
            elif (time1 <= indexx < time2):
                commiter_time_bug_num['time2'] += 1
            elif (time2 <= indexx < time3):
                commiter_time_bug_num['time3'] += 1
            elif (time3 <= indexx < time4):
                commiter_time_bug_num['time4'] += 1
        if (x in commiter_bug_commit_hash.keys()):
            commiter_bug_hash_list111 = commiter_bug_commit_hash[x]
        else:
            commiter_bug_hash_list111 = []
        for bug_commit in commiter_bug_hash_list111:
            indexx = commiter_bug_hash_list111.index(bug_commit)
            if (0 <= indexx < time1):
                commiter_time_bug_commit_num['time1'] += 1
            elif (time1 <= indexx < time2):
                commiter_time_bug_commit_num['time2'] += 1
            elif (time2 <= indexx < time3):
                commiter_time_bug_commit_num['time3'] += 1
            elif (time3 <= indexx < time4):
                commiter_time_bug_commit_num['time4'] += 1

        commiter_contribute_time1[x] = {}
        commiter_contribute_time1[x]['start'] = commiter_start_time[x].strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time1[x]['end'] = hashList_time[commiter_hash_list[time1-1]].strftime("%Y-%m-%d %H:%M:%S")
        if(commiter_time_commit_num['time1']==0):
            commiter_contribute_time1[x]['bug_num_per_commit'] = -1
            commiter_contribute_time1[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time1[x]['bug_num_per_commit'] = commiter_time_bug_num['time1']/commiter_time_commit_num['time1']
            commiter_contribute_time1[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time1']/commiter_time_commit_num['time1']

        commiter_contribute_time2[x] = {}
        commiter_contribute_time2[x]['start'] = hashList_time[commiter_hash_list[time1]].strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time2[x]['end'] = hashList_time[commiter_hash_list[time2-1]].strftime("%Y-%m-%d %H:%M:%S")
        if (commiter_time_commit_num['time2'] == 0):
            commiter_contribute_time2[x]['bug_num_per_commit'] = -1
            commiter_contribute_time2[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time2[x]['bug_num_per_commit'] = commiter_time_bug_num['time2'] / commiter_time_commit_num['time2']
            commiter_contribute_time2[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time2'] /commiter_time_commit_num['time2']

        commiter_contribute_time3[x] = {}
        commiter_contribute_time3[x]['start'] = hashList_time[commiter_hash_list[time2]].strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time3[x]['end'] = hashList_time[commiter_hash_list[time3-1]].strftime("%Y-%m-%d %H:%M:%S")
        if (commiter_time_commit_num['time3'] == 0):
            commiter_contribute_time3[x]['bug_num_per_commit'] = -1
            commiter_contribute_time3[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time3[x]['bug_num_per_commit'] = commiter_time_bug_num['time3'] / commiter_time_commit_num['time3']
            commiter_contribute_time3[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time3'] / commiter_time_commit_num['time3']

        commiter_contribute_time4[x] = {}
        commiter_contribute_time4[x]['start'] = hashList_time[commiter_hash_list[time3]].strftime("%Y-%m-%d %H:%M:%S")
        commiter_contribute_time4[x]['end'] = hashList_time[commiter_hash_list[time4-1]].strftime("%Y-%m-%d %H:%M:%S")
        if (commiter_time_commit_num['time4'] == 0):
            commiter_contribute_time4[x]['bug_num_per_commit'] = -1
            commiter_contribute_time4[x]['bug_commit_num_rate'] = -1
        else:
            commiter_contribute_time4[x]['bug_num_per_commit'] = commiter_time_bug_num['time4'] / commiter_time_commit_num['time4']
            commiter_contribute_time4[x]['bug_commit_num_rate'] = commiter_time_bug_commit_num['time4'] / commiter_time_commit_num['time4']

    commit_metrics = {}
    commit_metrics['item_start_time'] = item_start_time
    commit_metrics['commiter_start_time'] = commiter_start_time
    commit_metrics['commiter_end_time'] = commiter_end_time
    commit_metrics['commiter_contribute_time'] = commiter_contribute_time
    commit_metrics['commiter_contribute_time1'] = commiter_contribute_time1
    commit_metrics['commiter_contribute_time2'] = commiter_contribute_time2
    commit_metrics['commiter_contribute_time3'] = commiter_contribute_time3
    commit_metrics['commiter_contribute_time4'] = commiter_contribute_time4
    for i in commit_metrics['commiter_start_time']:
        commit_metrics['commiter_start_time'][i]=str(commit_metrics['commiter_start_time'][i])
    for i in commit_metrics['commiter_end_time']:
        commit_metrics['commiter_end_time'][i]=str(commit_metrics['commiter_end_time'][i])


    for y in commiter_contribute_time1.keys():
        commiter_time_trend[y] = {}
        commiter_time_trend[y]['bug_num_per_commit'] = {}
        commiter_time_trend[y]['bug_num_per_commit']['time1'] = commiter_contribute_time1[y]['bug_num_per_commit']
        commiter_time_trend[y]['bug_num_per_commit']['time2'] = commiter_contribute_time2[y]['bug_num_per_commit']
        commiter_time_trend[y]['bug_num_per_commit']['time3'] = commiter_contribute_time3[y]['bug_num_per_commit']
        commiter_time_trend[y]['bug_num_per_commit']['time4'] = commiter_contribute_time4[y]['bug_num_per_commit']
        commiter_time_trend[y]['bug_commit_num_rate'] = {}
        commiter_time_trend[y]['bug_commit_num_rate']['time1'] = commiter_contribute_time1[y]['bug_commit_num_rate']
        commiter_time_trend[y]['bug_commit_num_rate']['time2'] = commiter_contribute_time2[y]['bug_commit_num_rate']
        commiter_time_trend[y]['bug_commit_num_rate']['time3'] = commiter_contribute_time3[y]['bug_commit_num_rate']
        commiter_time_trend[y]['bug_commit_num_rate']['time4'] = commiter_contribute_time4[y]['bug_commit_num_rate']

    commit_metrics['commiter_time_trend'] = commiter_time_trend
    commit_metrics['daily_long_time_error_prone_developer'] = daily_long_time_error_prone_developer
    commit_metrics['number_daily_long_time_error_prone_developer'] = len(daily_long_time_error_prone_developer)


    improved_daily_long_time_error_prone_developer = []
    for y in commiter_time_trend.keys():
        x = commiter_time_trend[y]['bug_num_per_commit']
        xx = commiter_time_trend[y]['bug_commit_num_rate']
        if(x['time1']<=x['time2'] and x['time2']<=x['time3'] and x['time3']<=x['time4']):
            if (y in daily_long_time_error_prone_developer):
                improved_daily_long_time_error_prone_developer.append(y)
                continue
        if(xx['time1']<=xx['time2'] and xx['time2']<=xx['time3'] and xx['time3']<=xx['time4']):
            if (y in daily_long_time_error_prone_developer):
                improved_daily_long_time_error_prone_developer.append(y)
    commit_metrics['improved_daily_long_time_error_prone_developer'] = improved_daily_long_time_error_prone_developer
    number = len(improved_daily_long_time_error_prone_developer)
    commit_metrics['number_improved_daily_long_time_error_prone_developer'] = number
    print(number)

    print("RQ4指标计算完毕，输出文件")
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(commit_metrics, f, indent=4)

    print("RQ4结束")


# 初始化
# 计算每个commit中修改的文件
hash_file_list = {}

# 项目开始时间
item_start_time = ''

# 每个开发者最开始贡献时间和最后贡献时间
commiter_start_time = {}
commiter_end_time = {}
commiter_contribute_time = {}

# 计算出修改过该文件的hashList和commmiters
changeFiles_hashList = {}
changeFiles_commiter = {}

# 某个commit的时间
hashList_time = {}

# 引入bug的commits
inducing_commits = []
# 引入bug的commit数量
number_inducing_commit = {}

# 每个开发者引入bug的数量
commiter_bug_number = {}
commiter_bug_hash = {}
commiter_bug_commit_hash = {}
commiter_hashList = {}
hashList_commiter = {}

# 每个开发者所有author的commit数量
commiter_commit_number = {}

# 开发者平均每个commit中引入bug的数量
number_of_introduce_bugs_per_commit = {}

# 引入bug的commit比例
bug_introducing_commit_rate = {}

# 平均每个commit上引入bug多的开发者人数
high_bug_rate_error_prone_developer= {}
# bug introducing commit比例高的开发者人数
high_bug_commit_rate_error_prone_developer = {}

# 错误倾向开发者
error_prone_developer = []

# 错误倾向开发者中的日常维护人员
daily_error_prone_developer = []
# 错误倾向日常维护人员中贡献时间不是很短的人
daily_long_time_error_prone_developer = []

RQ5_daily_long_time_error_prone_developer = {}
RQ5_error_prone_developer = {}

global all_cate_dict,all_item_dict
#所有分析的项目列表
all_cate_dict = {}
all_item_dict = {}

def RQ5(output_path,cate,item_name):
    global RQ5_daily_long_time_error_prone_developer,RQ5_error_prone_developer
    Github_token = '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'
    api = "https://api.github.com/graphql"
    userBase = 'https://github.com/'
    global all_item_dict,daily_long_time_error_prone_developer
    error_developer_list = RQ5_daily_long_time_error_prone_developer[cate][item_name]
    item_info = {}
    item_info['developer'] = {}
    number_developer_mul_apache_item_error = 0
    developer_mul_apache_item_error = {}
    list = []
    for d in error_developer_list:
        xxxx = d
        d=d.split('--')[2]
        if (d == ''):
            continue
        url = userBase + d
        #print(url)
        user_info = query_user(Github_token, d, api)
        if (user_info == ''):
            continue
        #user_info = request_language(user_info, Github_token)
        #user_info['user_url'] = url
        #json_fn = './user_info/' + itemName + '/' + user_name + '.json'
        #    try:
        #        os.mkdir('./user_info/' + itemName)
        #    except:
        #        pass
        attribute_apache_item_count = 0
        attribute_apache_item_list = [item_name]
        try:
            uuu = user_info['repositoriesContributedTo']['nodes']
        except:
            continue
        is_error_developer_apache_item_count = 0
        for iii in user_info['repositoriesContributedTo']['nodes']:
            i_name = iii['nameWithOwner']
            ll = i_name.split('/')
            if(ll[0]=='apache' and ll[1] in all_item_dict.keys()):
                attribute_apache_item_list.append(ll[1])

        for ccc in RQ5_daily_long_time_error_prone_developer.keys():
            for iii in RQ5_daily_long_time_error_prone_developer[ccc].keys():
                llllist = RQ5_daily_long_time_error_prone_developer[ccc][iii]
                for mm in llllist:
                    dd = mm.split('--')[2]
                    if(d == dd ):
                        if(iii not in attribute_apache_item_list):
                            attribute_apache_item_list.append(iii)
                        is_error_developer_apache_item_count = is_error_developer_apache_item_count+1
                        if(is_error_developer_apache_item_count==1):
                            developer_mul_apache_item_error[xxxx] = [iii]
                        else:
                            if(iii not in developer_mul_apache_item_error[xxxx]):
                                developer_mul_apache_item_error[xxxx].append(iii)
                        #print(123)
        if(item_name not in attribute_apache_item_list):
            attribute_apache_item_list.append(item_name)
        if (item_name not in developer_mul_apache_item_error[xxxx] and xxxx in developer_mul_apache_item_error.keys()):
            developer_mul_apache_item_error[xxxx].append(item_name)
        attribute_apache_item_count = len(attribute_apache_item_list)
        if(attribute_apache_item_count>1):
            print(d)


        info = {}
        info['attribute_apache_item_count'] = attribute_apache_item_count
        info['attribute_apache_item_list'] = attribute_apache_item_list
        info['is_error_developer_apache_item_count'] = len(developer_mul_apache_item_error[xxxx])
        if (info['is_error_developer_apache_item_count'] > 1):
            number_developer_mul_apache_item_error += 1
            print(d + '多个项目错误倾向开发者')
        info['item_info'] = user_info
        item_info['developer'][xxxx] = info

    item_info['number_developer_mul_apache_item_error'] = number_developer_mul_apache_item_error
    item_info['deveper_mul_apache_item_error'] = developer_mul_apache_item_error
    user_path = './RQ5/' + cate + '/' + item_name + '.json'
    with open(user_path, 'w+') as f:
        json.dump(item_info, f, indent=4)
    print("Saved user information to " + user_path)


def merge_RQ5_json():
    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['developer']={}
        xx_dict['number_developer_mul_apache_item_error']=0
        xx_dict['developer_mul_apache_item_error']={}
        for itemname in all_cate_dict[c]:
            rq5_path = './RQ5/' + c + '/' + itemname + '.json'
            print(rq5_path)
            with open(rq5_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)  # 读取json文件
            Merge(json_data['developer'], xx_dict['developer'])
            # print(json_data['deveper_mul_apache_item_error'])
            xx_dict['number_developer_mul_apache_item_error'] += json_data['number_developer_mul_apache_item_error']
            Merge(json_data['deveper_mul_apache_item_error'], xx_dict['developer_mul_apache_item_error'])
        path = './RQ5/' + c + '.json'
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(xx_dict, f, indent=4)
        #print(111)

def Merge(dict1, dict2):
    return(dict2.update(dict1))


def analize_RQ4_from_item():
    rate = {}
    for c in all_cate_dict.keys():
        xx_dict = {}
        for itemname in all_cate_dict[c]:
            rq5_path = './RQ4/' + c + '/' + itemname + '_metrics.json'
            with open(rq5_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)  # 读取json文件
            print(itemname)
            try:
                rate[itemname] = json_data['number_improved_daily_long_time_error_prone_developer']/json_data['number_daily_long_time_error_prone_developer']
            except:
                rate[itemname] = 0
    sum = 0
    count50 = 0
    count0 = 0
    count20=0
    count40 = 0
    count30 = 0
    sum = len(rate)
    for iii in rate.keys():
        if (rate[iii] <= 0.3):
            count30 += 1
        if(rate[iii]<=0.4):
            count40+=1
        if(rate[iii]>=0.5):
            count50 += 1
        if(rate[iii]==0):
            count0 += 1
        if(rate[iii]<=0.2):
            count20+=1
    path = './RQ4/item.csv'
    with open(path, 'w', newline='') as csvfile:
        didi = dict(sorted(rate.items(), key=lambda x: x[1], reverse=True))
        fieldnames = list(didi.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(didi)

def analize_RQ3_is_important_developer():
    dict = {}
    result_path = './result_tf.csv'
    with codecs.open(result_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            if not dict:
                dict[row['reponame']] = {}
                dict[row['reponame']][row['author']] = row
                #print(111)
            else:
                if(row['reponame'] not in dict.keys()):
                    dict[row['reponame']] = {}
                dict[row['reponame']][row['author']] = row

    #print(dict)
    #dict['avro']['cutting'] = {'value': 1}
    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['error_developer_file_rate']={}
        rq3_path = './RQ3/' + c + '.json'
        with open(rq3_path, 'r', encoding='utf8') as fp:
            json_data = json.load(fp)  # 读取json文件
        # print(json_data)
        file_more_developer_list = json_data['daily_error_prone_developer']
        num1 = len(file_more_developer_list)
        num2 = 0
        num3 = 0
        for dd in file_more_developer_list:
            if(float(json_data['error_developer_file_rate'][dd])>=0.3):
                i = dd.split('--')[1]
                name = dd.split('--')[2]
                if(name == ''):
                    continue
                # if (name == 'cutting'):
                #     print(2323)
                #     print(222)
                num2 += 1
                if(dict[i][name]['value']==1):
                    num3 += 1
        print(num3)

def analize_RQ5_from_item():
    rate = {}
    sum1 = 0
    sum2 = 0
    sum = 0
    all = {}
    for c in all_cate_dict.keys():
        xx_dict = {}
        for itemname in all_cate_dict[c]:
            rq5_path = './RQ5/' + c + '/' + itemname + '.json'
            with open(rq5_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)  # 读取json文件
            #print(itemname)
            try:
                rate[itemname] = json_data['number_developer_mul_apache_item_error']/len(json_data['developer'])
            except:
                rate[itemname] = 0
            if(float(rate[itemname])>0):
                sum1 += int(json_data['number_developer_mul_apache_item_error'])
                sum2 += len(json_data['developer'])
    sum = len(rate)
    count50 = 0
    count0 = 0
    count20_30=0
    count40 = 0
    count100 = 0
    count60 = 0

    for iii in rate.keys():
        if (rate[iii] >= 0.6):
            count60 += 1
        if(rate[iii]>=0.4):
            count40+=1
        if(rate[iii]>=0.5):
            count50 += 1
        if(rate[iii]==0):
            count0 += 1
        if(rate[iii]>=0.2 and rate[iii]<=0.3):
            count20_30+=1
        if(rate[iii] == 1):
            count100 += 1
    path = './RQ5/item.csv'
    with open(path, 'w', newline='') as csvfile:
        didi = dict(sorted(rate.items(), key=lambda x: x[1], reverse=True))
        fieldnames = list(didi.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(didi)
    return


def analize_RQ3_error_developer_file_rate():
    all = {}
    for c in all_cate_dict.keys():
        xx_dict1 = {}
        xx_dict2 = {}
        xx_dict3 = {}
        bug_rate_path = './real_file_bug_paint_RQ3/' + c + '.csv'
        with codecs.open(bug_rate_path, encoding='utf-8-sig') as f:
            i = 1
            for row in csv.DictReader(f, skipinitialspace=True):
                if (i == 1):
                    i = i + 1
                    if not xx_dict1:
                        xx_dict1 = row
                    else:
                        Merge(row, xx_dict1)
                elif (i == 2):
                    i = i + 1
                    if not xx_dict2:
                        xx_dict2 = row
                    else:
                        Merge(row, xx_dict2)
                else:
                    i = i + 1
                    if not xx_dict3:
                        xx_dict3 = row
                    else:
                        Merge(row, xx_dict3)
        if(len(xx_dict3)==0 and len(xx_dict2)==0 and len(xx_dict1)==0):
            continue
        sum_bug = 0
        for xx in xx_dict2.keys():
            sum_bug += float(xx_dict2[xx])
        all[c] = {}
        all[c]['num_bug_per_commit'] = sum_bug/len(xx_dict2)
        sum_bug = 0
        for xx in xx_dict3.keys():
            sum_bug += float(xx_dict3[xx])
        all[c]['bug_commit_rate'] = sum_bug/len(xx_dict3)
        nn1 = 0
        nn2 = 0
        for xx in xx_dict2.keys():
            if(float(xx_dict2[xx])>=all[c]['num_bug_per_commit']):
                nn1 += 1
            if(float(xx_dict3[xx])>=all[c]['bug_commit_rate']):
                nn2 += 1
        all[c]['num_bug_per_commit_baifenbi'] = nn1/len(xx_dict3)
        all[c]['bug_commit_rate_baifenbi'] = nn2 / len(xx_dict3)
    print(all)
    #从项目的角度
    all = {}
    for c in all_cate_dict.keys():
        for itemname in all_cate_dict[c]:
            xx_dict = {}
            bug_rate_path = './real_file_bug_paint_RQ3/' + c + '/' + itemname + '.csv'
            with codecs.open(bug_rate_path, encoding='utf-8-sig') as f:
                for row in csv.DictReader(f, skipinitialspace=True):
                    if not xx_dict :
                        xx_dict = row
                        break
            print(xx_dict)
            sum_30_up = 0
            sum_30_down = 0
            for yyy in xx_dict.keys():
                if(float(xx_dict[yyy])>=0.3):
                    sum_30_up += 1
                else:
                    sum_30_down += 1
            try:
                z = sum_30_up/(sum_30_down+sum_30_up)
                if(z<=0.2):
                    all[itemname] =z
            except:
                pass
    print(all)

    # 从类别的角度
    all = {}
    for c in all_cate_dict.keys():
        xx_dict = {}
        bug_rate_path = './real_file_bug_paint_RQ3/' + c  + '.csv'
        with codecs.open(bug_rate_path, encoding='utf-8-sig') as f:
            for row in csv.DictReader(f, skipinitialspace=True):
                if not xx_dict:
                    xx_dict = row
                    break
        # print(xx_dict)
        sum_30_up = 0
        sum_30_down = 0
        for yyy in xx_dict.keys():
            if (float(xx_dict[yyy]) >= 0.3):
                sum_30_up += 1
            else:
                sum_30_down += 1
        try:
            z = sum_30_up / (sum_30_down + sum_30_up)
            if (z <= 0.35):
                all[c] = z
            else:
                print(c)

        except:
            pass
    print(all)


def merge_RQ1_json():
    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['number_of_introduce_bugs_per_commit']={}
        xx_dict['bug_introducing_commit_rate']={}
        xx_dict['commiter_bug_number']={}
        xx_dict['number_inducing_commit']={}
        xx_dict['commiter_commit_number']={}
        xx_dict['team_developer_num'] = 0
        for itemname in all_cate_dict[c]:
            rq1_path = './RQ1/' + c + '/' + itemname + '_metrics.json'
            with open(rq1_path, 'r', encoding='gbk') as fp:
                json_data = json.load(fp)  # 读取json文件
            Merge(json_data['number_of_introduce_bugs_per_commit'], xx_dict['number_of_introduce_bugs_per_commit'])
            Merge(json_data['bug_introducing_commit_rate'],xx_dict['bug_introducing_commit_rate'])
            Merge(json_data['commiter_bug_number'], xx_dict['commiter_bug_number'])
            Merge(json_data['number_inducing_commit'],xx_dict['number_inducing_commit'])
            Merge(json_data['commiter_commit_number'],xx_dict['commiter_commit_number'])
            xx_dict['commiter_bug_number'] = dict(sorted(xx_dict['commiter_bug_number'].items(), key=lambda x: x[1], reverse=True))
            xx_dict['team_developer_num'] += json_data['team_developer_num']
        path = './RQ1/' + c + '.json'
        with open(path, 'w', encoding="gbk") as f:
            json.dump(xx_dict, f, indent=4)
def merge_RQ2_csv():
    for c in all_cate_dict.keys():
        xx_dict = {}
        for itemname in all_cate_dict[c]:
            bug_rate_path = './number_of_introduce_bugs_per_commit/' + c + '/' + itemname + '.csv'
            print(bug_rate_path)
            with codecs.open(bug_rate_path,encoding='gbk') as f:
                for row in csv.DictReader(f, skipinitialspace=True):
                    if not xx_dict :
                        xx_dict = row
                    else:
                        Merge(row, xx_dict)
            # print(xx_dict)
        #print(222)
        path = './number_of_introduce_bugs_per_commit/' + c + '.csv'
        with open(path, 'w', newline='') as csvfile:
            didi = dict(sorted(xx_dict.items(), key=lambda x: x[1],reverse=True))
            fieldnames = list(didi.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(didi)

    for c in all_cate_dict.keys():
        xx_dict = {}
        for itemname in all_cate_dict[c]:
            bug_rate_path = './bug_introducing_commit_rate/' + c + '/' + itemname + '.csv'
            with codecs.open(bug_rate_path, encoding='gbk') as f:
                for row in csv.DictReader(f, skipinitialspace=True):
                    #print(row)
                    #print(xx_dict)
                    if not xx_dict :
                        xx_dict = row
                        #print(1)
                    else:
                        Merge(row, xx_dict)
            # print(xx_dict)
        #print(222)
        path = './bug_introducing_commit_rate/' + c + '.csv'
        with open(path, 'w', newline='') as csvfile:
            didi = dict(sorted(xx_dict.items(), key=lambda x: x[1],reverse=True))
            fieldnames = list(didi.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(didi)

def merge_RQ2_json():
    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['high_bug_rate_error_prone_developer_number']=0
        xx_dict['high_bug_rate_error_prone_developer']={}
        xx_dict['high_bug_commit_rate_error_prone_developer']={}
        xx_dict['error_prone_developer_num']=0
        xx_dict['error_prone_developer']=[]
        xx_dict['team_developer_num']=0
        for itemname in all_cate_dict[c]:
            rq2_path = './RQ2/' + c + '/' + itemname + '_metrics.json'
            with open(rq2_path, 'r', encoding='gbk') as fp:
                json_data = json.load(fp)  # 读取json文件
            xx_dict[c+'-'+'aver_bug_rate'] = json_data[c+'-'+'cate_aver_bug_rate']
            xx_dict[c + '-' + 'aver_bug_commit_rate'] = json_data[c + '-' + 'cate_aver_bug_commit_rate']
            xx_dict['high_bug_rate_error_prone_developer_number']+=json_data['high_bug_rate_error_prone_developer_number']
            Merge(json_data['high_bug_rate_error_prone_developer'],xx_dict['high_bug_rate_error_prone_developer'])
            Merge(json_data['high_bug_commit_rate_error_prone_developer'],xx_dict['high_bug_commit_rate_error_prone_developer'])
            xx_dict['error_prone_developer_num'] += json_data['error_prone_developer_num']
            xx_dict['error_prone_developer'].extend(json_data['error_prone_developer'])
            xx_dict['team_developer_num'] += json_data['team_developer_num']
        xx_dict['error_prone_developer_team_rate'] = 1.0*xx_dict['error_prone_developer_num']/xx_dict['team_developer_num']
        xx_dict['high_bug_commit_rate_error_prone_developer_number'] = len(xx_dict['high_bug_commit_rate_error_prone_developer'])
        path = './RQ2/' + c + '.json'
        with open(path, 'w', encoding="gbk") as f:
            json.dump(xx_dict, f, indent=4)

def merge_RQ3_csv():
    for c in all_cate_dict.keys():
        xx_dict1 = {}
        xx_dict2 = {}
        xx_dict3 = {}
        for itemname in all_cate_dict[c]:
            bug_rate_path = './file_bug_paint_RQ3/' + c + '/' + itemname + '.csv'
            with codecs.open(bug_rate_path, encoding='gbk') as f:
                i = 1
                for row in csv.DictReader(f, skipinitialspace=True):
                    #print(row)
                    #print(xx_dict)
                    if(i==1):
                        i=i+1
                        if not xx_dict1 :
                            xx_dict1 = row
                            #print(1)
                        else:
                            Merge(row, xx_dict1)
                    elif(i == 2):
                        i=i+1
                        if not xx_dict2:
                            xx_dict2 = row
                            # print(1)
                        else:
                            Merge(row, xx_dict2)
                    else:
                        i = i + 1
                        if not xx_dict3:
                            xx_dict3 = row
                            # print(1)
                        else:
                            Merge(row, xx_dict3)
            # print(xx_dict)
        #print(222)
        path = './file_bug_paint_RQ3/' + c + '.csv'
        with open(path, 'w', newline='') as csvfile:
            for ii in xx_dict1.keys():
                xx_dict1[ii] = float(xx_dict1[ii])
            didi = dict(sorted(xx_dict1.items(), key=lambda x: x[1]))
            fieldnames = list(didi.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(didi)
            oo={}
            oo2={}
            for x in fieldnames:
                oo[x]=xx_dict2[x]
                oo2[x]=xx_dict3[x]
            writer.writerow(oo)
            writer.writerow(oo2)

    for c in all_cate_dict.keys():
        xx_dict1 = {}
        xx_dict2 = {}
        xx_dict3 = {}
        for itemname in all_cate_dict[c]:
            bug_rate_path = './real_file_bug_paint_RQ3/' + c + '/' + itemname + '.csv'
            with codecs.open(bug_rate_path, encoding='gbk') as f:
                i = 1
                for row in csv.DictReader(f, skipinitialspace=True):
                    #print(row)
                    # print(xx_dict)
                    if (i == 1):
                        i = i + 1
                        if not xx_dict1:
                            xx_dict1 = row
                            # print(1)
                        else:
                            Merge(row, xx_dict1)
                    elif (i == 2):
                        i = i + 1
                        if not xx_dict2:
                            xx_dict2 = row
                            # print(1)
                        else:
                            Merge(row, xx_dict2)
                    else:
                        i = i + 1
                        if not xx_dict3:
                            xx_dict3 = row
                            # print(1)
                        else:
                            Merge(row, xx_dict3)
        path = './real_file_bug_paint_RQ3/' + c + '.csv'
        output_xx_dict = {}
        for ii in xx_dict1.keys():
            output_xx_dict[ii]=xx_dict1[ii]
        with open(path, 'w', newline='') as csvfile:
            for ii in output_xx_dict.keys():
                yy = ii.split('--')
                #print(yy)
                if(yy[2]==''):
                    #print(111)
                    xx_dict1.pop(ii)
                    continue
                xx_dict1[ii] = float(xx_dict1[ii])
            didi = dict(sorted(xx_dict1.items(), key=lambda x: x[1]))
            fieldnames = list(didi.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(didi)
            oo = {}
            oo2 = {}
            for x in fieldnames:
                oo[x] = xx_dict2[x]
                oo2[x] = xx_dict3[x]
            writer.writerow(oo)
            writer.writerow(oo2)

def merge_RQ3_json():
    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['all_file_num']=0
        xx_dict['error_developer_file_rate']={}
        xx_dict['daily_error_prone_developer']=[]
        xx_dict['number_daily_error_prone_developer'] = 0
        for itemname in all_cate_dict[c]:
            rq2_path = './RQ3/' + c + '/' + itemname + '_metrics.json'
            with open(rq2_path, 'r', encoding='gbk') as fp:
                json_data = json.load(fp)  # 读取json文件
            Merge(json_data['error_developer_file_rate'],xx_dict['error_developer_file_rate'])
            xx_dict['daily_error_prone_developer'].extend(json_data['daily_error_prone_developer'])
            xx_dict['number_daily_error_prone_developer'] = len(xx_dict['daily_error_prone_developer'])
            xx_dict['all_file_num'] += json_data['all_file_num']
        path = './RQ3/' + c + '.json'
        with open(path, 'w', encoding="gbk") as f:
            json.dump(xx_dict, f, indent=4)

def merge_RQ4_csv():
    for c in all_cate_dict.keys():
        xx_dict1 = {}
        xx_dict2 = {}
        xx_dict3 = {}
        for itemname in all_cate_dict[c]:
            bug_rate_path = './real_RQ4_time_bug/' + c + '/' + itemname + '.csv'
            with codecs.open(bug_rate_path, encoding='gbk') as f:
                i = 1
                for row in csv.DictReader(f, skipinitialspace=True):
                    #print(row)
                    #print(xx_dict)
                    if(i==1):
                        i=i+1
                        if not xx_dict1 :
                            xx_dict1 = row
                            #print(1)
                        else:
                            Merge(row, xx_dict1)
                    elif(i == 2):
                        i=i+1
                        if not xx_dict2:
                            xx_dict2 = row
                            # print(1)
                        else:
                            Merge(row, xx_dict2)
                    else:
                        i = i + 1
                        if not xx_dict3:
                            xx_dict3 = row
                            # print(1)
                        else:
                            Merge(row, xx_dict3)
            # print(xx_dict)
        #print(222)
        path = './real_RQ4_time_bug/' + c + '.csv'
        with open(path, 'w', newline='') as csvfile:
            for ii in xx_dict1.keys():
                xx_dict1[ii] = float(xx_dict1[ii])
            didi = dict(sorted(xx_dict1.items(), key=lambda x: x[1]))
            fieldnames = list(didi.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(didi)
            oo={}
            oo2={}
            for x in fieldnames:
                oo[x]=xx_dict2[x]
                oo2[x]=xx_dict3[x]
            writer.writerow(oo)
            writer.writerow(oo2)

def merge_RQ4_json():
    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['commiter_start_time']={}
        xx_dict['commiter_end_time']={}
        xx_dict['commiter_contribute_time']={}
        xx_dict['commiter_contribute_time1']={}
        xx_dict['commiter_contribute_time2'] = {}
        xx_dict['commiter_contribute_time3'] = {}
        xx_dict['commiter_contribute_time4'] = {}
        xx_dict['commiter_time_trend'] = {}
        xx_dict['daily_long_time_error_prone_developer']=[]
        xx_dict['improved_daily_long_time_error_prone_developer'] = []
        xx_dict['number_improved_daily_long_time_error_prone_developer'] = 0
        xx_dict['number_daily_long_time_error_prone_developer'] = 0
        for itemname in all_cate_dict[c]:
            rq2_path = './RQ4/' + c + '/' + itemname + '_metrics.json'
            with open(rq2_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)  # 读取json文件
            Merge(json_data['commiter_start_time'],xx_dict['commiter_start_time'])
            Merge(json_data['commiter_end_time'],xx_dict['commiter_end_time'])
            Merge(json_data['commiter_contribute_time'],xx_dict['commiter_contribute_time'])
            Merge(json_data['commiter_contribute_time1'],xx_dict['commiter_contribute_time1'])
            Merge(json_data['commiter_contribute_time2'], xx_dict['commiter_contribute_time2'])
            Merge(json_data['commiter_contribute_time3'], xx_dict['commiter_contribute_time3'])
            Merge(json_data['commiter_contribute_time4'], xx_dict['commiter_contribute_time4'])
            Merge(json_data['commiter_time_trend'], xx_dict['commiter_time_trend'])
            xx_dict['daily_long_time_error_prone_developer'].extend(json_data['daily_long_time_error_prone_developer'])
            xx_dict['improved_daily_long_time_error_prone_developer'].extend(json_data['improved_daily_long_time_error_prone_developer'])
            xx_dict['number_improved_daily_long_time_error_prone_developer'] += json_data['number_improved_daily_long_time_error_prone_developer']
            xx_dict['number_daily_long_time_error_prone_developer'] += json_data['number_daily_long_time_error_prone_developer']
            #for dd in xx_dict[]
        path = './RQ4/' + c + '.json'
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(xx_dict, f, indent=4)


def paint_file_relitu():
    pass


if __name__ =="__main__":
    induce_path = './bug_inducing_commit/'
    origin_commit_path = "./originCommitListData/"
    git_path = './items/'
    RQ1Path = './RQ1/'
    RQ2Path = './RQ2/'
    RQ3Path = './RQ3/'
    RQ4Path = './RQ4/'
    RQ5Path = './RQ5/'

    cate_dir_list = os.listdir(induce_path)
    # cate_dir_list = ['#cloud']
    print(cate_dir_list)
    for cate in cate_dir_list:
        induce_file_list = os.listdir(induce_path + cate)
        all_cate_dict[cate] = []
        for induce_file in induce_file_list:
            item_name = induce_file.split('_')[2].split('.')[0]
            all_item_dict[item_name] = cate
            all_cate_dict[cate].append(item_name)
    # analize_RQ3_is_important_developer()
    # analize_RQ3_error_developer_file_rate()
    # analize_RQ4_from_item()
    # analize_RQ5_from_item()
    #merge_RQ2_csv()
    for cate in cate_dir_list:
        induce_file_list = os.listdir(induce_path+cate)
        all_cate_dict[cate]=[]
        # induce_file_list = ['bic_ra_beam.json'..]
        for induce_file in induce_file_list:
            #item_name = beam
            item_name = induce_file.split('_')[2].split('.')[0]
            # git = './items/beam'
            git = git_path+item_name

            induce_file_path = induce_path+cate+'/'+induce_file
            with open(induce_file_path, 'r', encoding='gbk') as fp:
                json_data = json.load(fp)  # 读取json文件
            #print(json_data)
            print('开始计算'+item_name)
            all_item_dict[item_name] = cate
            all_cate_dict[cate].append(item_name)
            # 获取该项目的所有commit信息:./originCommitListData/beam.csv
            item_commit_path = origin_commit_path + item_name + '.csv'
            get_origin_commit(item_commit_path, git,cate,item_name)

            inducing_commits = []
            for i in json_data:
                x = i['inducing_commit_hash']
                if(x != []):
                    inducing_commits.append(x)
            #print(inducing_commits)
            # 开发者平均每个commit中引入bug的数量
            get_number_of_introduce_bugs_per_commit(inducing_commits)

            # 开发者引入bug的commit比例
            get_bug_introducing_commit_rate()

            output_path = RQ1Path + cate + '/' + item_name + "_metrics.json"
            outputRQ1(output_path)
    merge_RQ1_json()
    paint_file_relitu()

    for cate in cate_dir_list:
        yuzhi_cate_bug_rate, yuzhi_cate_bug_commit_rate = get_yuzhi_bug_rate_and_commit_rate(cate)
        cate_aver_bug_rate = yuzhi_cate_bug_rate
        cate_aver_bug_commit_rate = yuzhi_cate_bug_commit_rate
        RQ5_daily_long_time_error_prone_developer[cate]={}
        RQ5_error_prone_developer[cate] = {}
        for item_name in all_cate_dict[cate]:
            git = git_path + item_name
            item_commit_path = origin_commit_path + item_name + '.csv'
            get_origin_commit(item_commit_path, git, cate, item_name)

            RQ1_path = './RQ1/' + cate + '/' + item_name + "_metrics.json"
            with open(RQ1_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)  # 读取json文件
            number_of_introduce_bugs_per_commit = json_data['number_of_introduce_bugs_per_commit']
            bug_introducing_commit_rate = json_data['bug_introducing_commit_rate']
            commiter_bug_number = json_data['commiter_bug_number']
            number_inducing_commit = json_data['number_inducing_commit']
            commiter_commit_number = json_data['commiter_commit_number']

            RQ2(cate_aver_bug_rate, cate_aver_bug_commit_rate)
            output_path = RQ2Path + cate + '/' + item_name + "_metrics.json"
            outputRQ2(item_name, output_path, cate_aver_bug_rate, cate_aver_bug_commit_rate, cate)

           # print(111)
            all_file_num, error_developer_file_rate = RQ3()
            output_path = RQ3Path + cate + '/' + item_name + "_metrics.json"
            outputRQ3(item_name, output_path, all_file_num, error_developer_file_rate, cate)

            #RQ4()
            output_path = RQ4Path + cate + '/' + item_name + "_metrics.json"
            outputRQ4_new(cate,item_name, output_path)
    merge_RQ2_csv()
    merge_RQ2_json()
    merge_RQ3_csv()
    merge_RQ3_json()
    merge_RQ4_json()
    merge_RQ4_csv()
    #exit(0)
    for cate in cate_dir_list:
        for item_name in all_cate_dict[cate]:
            output_path = RQ5Path + cate + '/' + item_name + "_metrics.json"
            RQ5(output_path,cate,item_name)
    merge_RQ5_json()
    print(item_name+"全部计算完成")

