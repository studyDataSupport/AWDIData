
import json
from collections import Counter

import pandas as pd
from numpy import *
import csv
import codecs


csv.field_size_limit(500 * 1024 * 1024)



def output_bugfixing_commit_to_pyszz(git_item):
    bug_reprot_id = []
    fix_commit_hash = []
    repo_name = 'apache/' + git_item
    with codecs.open(bugreport_path+'sum_'+git_item+'.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            if(row['Issue Type']=='Bug'):
                bug_reprot_id.append(row['Issue key'])
    print(len(bug_reprot_id))
    with codecs.open(commit_path+git_item+'.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f, skipinitialspace=True):

            if(row['bug_id'] in bug_reprot_id):
                #print(row['bug_id'])
                fix_commit_hash.append(row['hash'])
    out = []
    #print(fix_commit_hash)
    for commit in fix_commit_hash:
        c = {}
        c['fix_commit_hash'] = commit
        c['repo_name'] = repo_name
        out.append(c)
    print(len(out))
    with open(output_path+git_item+'.json', 'w', encoding="utf-8" ) as f:
        json.dump(out, f, indent=4)

import os
commit_path = './originCommitListData/'
bugreport_path = './merge_csv/'
output_path = './fixing_commit_csv/'
if __name__ =="__main__":

    git_list = os.listdir(commit_path)
    for git_item in git_list:
        git_item=git_item.split('.')[0]
        output_bugfixing_commit_to_pyszz(git_item)
        print(git_item)
