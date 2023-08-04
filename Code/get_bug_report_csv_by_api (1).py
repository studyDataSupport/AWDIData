import json
import os
import csv
import codecs
import re
from time import *
from tqdm import *
import requests
import glob
import git


def write_jsonFile(projectName,response_metrics_ordered,path):
    f = open(f"./{path}/{projectName}.json", 'w', encoding='utf-8')
    json.dump(response_metrics_ordered, f, indent=4, ensure_ascii=False)

def mergecsv(gitName,outputBase):
    csv_list = glob.glob(outputBase+'/*.csv')
    print('共发现%s个CSV文件' % len(csv_list))
    print('正在处理............')
    for i in csv_list:
        fr = open(i, 'r', encoding='ISO-8859-1').read()
        with open('./merge_csv/sum_'+gitName+'.csv', 'a', encoding='utf-8') as f:
            f.write(fr)
    print('合并完毕！')

def getBugReportcsv(gitName,bugReportUrl,outputBase,flag):
    if(flag==0):
        i=0
        os.mkdir(outputBase)
        while(1):
            headers={}
            r = requests.get(bugReportUrl+str(i),headers=headers)  # 根据文件的大小，这一步为主要耗时步骤
            if (r.text.split('\n')[0] == ""):
                print('break')
                break

            with open(outputBase+'/'+gitName+str(i)+'.csv', "wb") as c:
                c.write(r.content)
            #print(r.text.split('\n')[0])
            print(i)
            i += 1000
    mergecsv(gitName,outputBase)
    bugReport = []
    bugIdList = []
    with codecs.open('./merge_csv/sum_'+gitName+'.csv', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            if(row['Issue Type']=='Bug'):
                bugReport.append(row)
                bugIdList.append(row['Issue key'])
            # print(row)
    # print(bugReport)
    return bugIdList

#获取commit的hash列表
def get_commit_history(repo: git.Repo, filename:str = None):
    git_ = repo.git
    initial_log = git_.log("--pretty=oneline", None)
    #print(initial_log)
    result=[]
    for line in initial_log.split("\n"):
        result.append(line.split(" ")[0])
    return result

def get_commits(repoLocalPath, writer,commitInfoApi):
    repo = git.Repo(repoLocalPath)
    # 传入仓库，得到hash列表
    hash_list = get_commit_history(repo)
    flg = 0
    print(len(hash_list))
    interval = time()
    for hashValue in tqdm(hash_list):
        Base = commitInfoApi+hashValue
        headers = {"Authorization": "token " + "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"}
        # print(Base)
        ff=1
        while(ff==1):
            try:
                result = requests.get(Base, headers=headers)
                c = result.json()
                if 'message' in c.keys():
                    if 'API rate limit' in c['message']:
                        sleep(600)
                        continue
                ff=0
            except:
                print("requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))")
                sleep(600)
        try:
            authors = c['author']['login']
        except:
            authors = ''

        try:
            committer = c['committer']['login']
        except:
            committer = ''
        try:
            changes_FileNum = len(c['files'])
        except:
            print(c)
            exit(-1)
        changed_files=[]
        for file in c['files']:
            changed_files.append(file['filename'])
        message = c['commit']['message']
        parentNum = c['commit']['message']
        #message格式，不同的项目不一样
        #[FLINK-28556][refactor] Extract header fields of Buffer
        # \[([A-Za-z]*-[0-9]*)\]
        #NIFI-10194: Simplified SendTrapSNMP error handling
        # [A-Za-z]*-[0-9]*
        bug_id = re.match(r"[A-Za-z]*-[0-9]*", message)
        if(bug_id==None):
            b = re.match(r"\[([A-Za-z]*-[0-9]*)\]", message)
            if(b==None):
                bug_id = ""
            else:
                bug_id = str(b.group()).replace('[','').replace(']','')
        else:
            bug_id = str(bug_id.group())
        commit = [hashValue,
                  authors,
                  committer,
                  changes_FileNum,
                  changed_files,
                  message,
                  bug_id
                  ]
        writer.writerow(commit)
        flg = flg+1
        if(flg%4900==0):
            while time()-interval<3600:
                sleep(60)
            interval=time()
        #print(flg)

def get_rawData(AuthorRepoName,repoLocalPath,commitInfoApi):
    # 获取一个项目的commit message 信息
    with open(f"./originCommitListData/{AuthorRepoName}.csv", "w",encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['hash', 'authors', 'committer',
                         'changes_FileNum', 'changed_files',
                         'message','bug_id'])
        get_commits(repoLocalPath, writer,commitInfoApi)


def getApacheItemName():
    burp0_url = "https://projects.apache.org:443/json/foundation/projects.json"
    burp0_headers = {"Sec-Ch-Ua": "\"-Not.A/Brand\";v=\"8\", \"Chromium\";v=\"102\"", "Sec-Ch-Ua-Mobile": "?0",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
                     "Sec-Ch-Ua-Platform": "\"Linux\"", "Accept": "*/*", "Sec-Fetch-Site": "same-origin",
                     "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                     "Referer": "https://projects.apache.org/project.html?zookeeper",
                     "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}
    res = requests.get(burp0_url, headers=burp0_headers).json()
    #print(res)
    key = res.keys()
    success_git_l = []
    error_git_l = []
    success_jira_l = []
    for i in key:
        burp0_url = "https://github.com/apache/"
        burp0_headers = {"Sec-Ch-Ua": "\"-Not.A/Brand\";v=\"8\", \"Chromium\";v=\"102\"", "Sec-Ch-Ua-Mobile": "?0",
                         "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1",
                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
                         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                         "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1",
                         "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate",
                         "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}
        # sleep(0.5)
        # 1.通过url查看是否该项目在github中存在，如果存在，就下载
        if requests.get(burp0_url+i, headers=burp0_headers).status_code == 200:
            try:
                git_name = i
                JIRAUrl = res[i]['bug-database']
            except:
                print(i+'失败')
                continue
            if 'jira' in JIRAUrl:
                JIRAName = JIRAUrl.split('/')[-1]
                success_git_l.append(i)
                success_jira_l.append(JIRAName)
            print(git_name)
        else:
            error_git_l.append(i)
    return success_git_l,success_jira_l,error_git_l


def initItem(gitName,JIRAName):
    outputBase = "./bugReportCsv/" + JIRAName
    repoLocalPath = "./items/"+gitName
    calculateResultPath = "calculateResult"
    commitInfoApi = 'https://api.github.com/repos/apache/' + gitName + '/commits/'
    gitUrl = f'https://github.com/apache/{gitName}.git'
    # Base2 = 'https://api.github.com/repos/'
    # https://api.github.com/repos/mybatis/spring/commits/966fd6563bcb9a641025b160d8c12512ac4c3ea7
    # 从JIRA获得bug report的所有.csv文件的网址
    bugReportUrl1 = 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-csv-current-fields/temp/SearchRequest.csv?jqlQuery=project+%3D+'
    bugReportUrl2 = '+ORDER+BY+priority+DESC%2C+updated+DESC&delimiter=,'
    string = '&tempMax=1000&pager/start='
    JIRAUrl = bugReportUrl1 + JIRAName + bugReportUrl2 + string
    # 1.得到JIRA上获得的所有bug fixing的bug id列表,值为1表示已经从api上获取完毕，现在是从sum_{repoName}.csv的汇总文件中获取；值为0则是从头获取
    #bugIdList = getBugReportcsv(gitName, JIRAUrl, outputBase, 0)
    # 2. 把git下载到本地
    #print("开始clone")
    #git.Repo.clone_from(gitUrl,repoLocalPath)
    # 3.得到所有的commit数据
    get_rawData(gitName, repoLocalPath, commitInfoApi)
    # print(bugIdList)
    print("完成hashList获取，可以准备开始计算")

if __name__ =="__main__":
    #把要运行的项目gitname和jiraname存到文件中
    #success_git_l,success_jira_l,error_git_l = getApacheItemName()
    #读取文件中的项目名
    f = open('git.txt','r')
    success_git_l = f.readlines()
    f.close()
    f = open('jira.txt', 'r')
    success_jira_l = f.readlines()
    f.close()
    success_git_l = success_git_l[0].split('[')[1].split(']')[0].split(',')
    success_jira_l = success_jira_l[0].split('[')[1].split(']')[0].split(',')
    print(success_git_l)
    print(len(success_git_l))
    print(len(success_jira_l))
    print(success_jira_l)

    #success_git_l=["'ant-ivyde'"]
    #success_jira_l = ["'IVYDE'"]
    for i in range(0,41):
        print(i)
        gitName = success_git_l[i].split('\'')[1]
        print(gitName)
        JIRAName = success_jira_l[i].split('\'')[1]
        print(JIRAName)
        initItem(gitName,JIRAName)







