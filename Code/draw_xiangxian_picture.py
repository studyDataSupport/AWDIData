import json
import os
import statistics

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import csv
import codecs


def Merge(dict1, dict2):
    return(dict2.update(dict1))


def draw_3_1_a():
    induce_path = './bug_inducing_commit/'
    RQ1Path = './RQ1/'
    #cate_dir_list = os.listdir(induce_path)
    catetory = '#big-data'
    cate_dir_list = [catetory]
    print(cate_dir_list)

    all_cate_dict={}
    for cate in cate_dir_list:
        induce_file_list = os.listdir(induce_path + cate)
        all_cate_dict[cate] = []
        for induce_file in induce_file_list:
            item_name = induce_file.split('_')[2].split('.')[0]
            all_cate_dict[cate].append(item_name)



    q_percent = 50
    item_index = 1
    shangxian=5

    iiitem = all_cate_dict[catetory][item_index-1]
    print(iiitem)


    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['number_of_introduce_bugs_per_commit_total'] = {}
        xx_dict['bug_introducing_commit_rate_total'] = {}
        xx_dict['number_of_introduce_bugs_per_commit_item'] = {}
        xx_dict['bug_introducing_commit_rate_item'] = {}
        for itemname in all_cate_dict[c]:
            rq1_path = './RQ1/' + c + '/' + itemname + '_metrics.json'
            with open(rq1_path, 'r', encoding='gbk') as fp:
                json_data = json.load(fp)  # 读取json文件
            Merge(json_data['number_of_introduce_bugs_per_commit'], xx_dict['number_of_introduce_bugs_per_commit_total'])
            Merge(json_data['bug_introducing_commit_rate'], xx_dict['bug_introducing_commit_rate_total'])
            xx_dict['number_of_introduce_bugs_per_commit_item'][itemname] = json_data['number_of_introduce_bugs_per_commit']
            xx_dict['bug_introducing_commit_rate_item'][itemname] = json_data['bug_introducing_commit_rate']

    bar_num = len(xx_dict['bug_introducing_commit_rate_item'])+1

    # 定义两个指标分别的四分之一值是多少
    number_of_introduce_bugs_per_commit_i6_25 = 0
    developer1=[]
    bug_introducing_commit_rate_i6_25 = 0
    developer2=[]



    #绘制 number_of_introduce_bugs_per_commit
    datas = []
    for itemname in all_cate_dict[catetory]:
        data = list(xx_dict['number_of_introduce_bugs_per_commit_item'][itemname].values())
        data = [x for x in data if x != 0]
        datas.append(data)
    number_of_introduce_bugs_per_commit_i6_25 = np.percentile(datas[item_index-1], q_percent)

    for d in xx_dict['number_of_introduce_bugs_per_commit_item'][iiitem]:
        if(xx_dict['number_of_introduce_bugs_per_commit_item'][iiitem][d]>=number_of_introduce_bugs_per_commit_i6_25):
            developer1.append(d)

    data=list(xx_dict['number_of_introduce_bugs_per_commit_total'].values())
    data = [x for x in data if x != 0]
    datas.append(data)

    # plt.figure(figsize=(6, 4))
    # plt.rcParams["font.family"] = "Arial"
    # plt.rcParams["font.size"] = 12


    labels_len = len(datas)-1
    labels=[f"#{i+1}" for i in range(labels_len)]
    labels.append('total')

    # 设置全局字体大小
    plt.rcParams['font.size'] = 26

    # create boxplot with blue filled boxes, black outlier points, and normal (non-notched) box representation
    plt.figure(figsize=(20, 12))

    # Boxplot
    bplot = plt.boxplot(datas, patch_artist=True, medianprops=dict(color=(255/255,0/255,0/255,0.5), linewidth=2),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=3, linestyle='none'))

    # Set edge color and fill color
    for patch in bplot['boxes']:
        patch.set(facecolor=(225 / 255, 129 / 255, 44 / 255,0.4))  # fill with light blue
        patch.set(edgecolor='black')  # black border
#(225 / 255, 129 / 255, 44 / 255,0.4) (31 / 255, 119 / 255, 180 / 255,0.3)(152 / 255, 185 / 255, 208 / 255,0.5)
    plt.xticks([1, 2, 3, 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], labels)
    plt.ylabel("BIRC\n")
    plt.xlabel("\nProjects")
    plt.title("Bug-Inducing Ratio per Commit\n")
    # 添加坐标轴刻度线与盒图之间的虚线
    # for i in range(len(datas)):
    #     plt.plot([i + 1, i + 1], [min(datas[i]), max(datas[i])], 'k--', lw=1)

    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性



    plt.show()


    # fig, ax = plt.subplots()
    # bp = ax.boxplot(datas, sym='.',  # 设置异常值的标记方式
    #                 labels=labels,  # x轴标记
    #                 boxprops={'color': (177 / 255, 204 / 255, 220 / 255), 'edgecolor': (72 / 255, 72 / 255, 72 / 255)},
    #                 # 箱线图箱部参数设置（填充颜色和边框颜色）
    #                 patch_artist=True,  # 填充箱子部分
    #                 capprops={'color': 'k'},  # 箱线图顶部横线设置
    #                 whiskerprops={'linestyle': '-'},  # 箱线图须部参数设置
    #                 medianprops={'color': 'white'},  # 中位数线参数设置（颜色为白色）
    #                 flierprops={'markerfacecolor': 'k', 'markeredgecolor': 'None'})  # 异常值标记参数设置
    # ax.set_title('Bug-Inducing Ratio per Commit')
    # ax.set_xlabel('Projects')
    # ax.set_ylabel('BIRC')
    # for box in bp['boxes']:
    #     box.set_facecolor((31 / 255, 119 / 255, 180 / 255))
    #     box.set_edgecolor((72 / 255, 72 / 255, 72 / 255))
    # plt.show()


    # bp = plt.boxplot(datas, labels=labels, notch=True, patch_artist=True)
    #
    # plt.ylim(0, 2)
    #
    # colors = [f"#ADD8E6" for i in range(labels_len+1)]
    # rgba_colors = [mcolors.to_rgba(color) for color in colors]
    #
    # for box, color in zip(bp['boxes'], rgba_colors):
    #     box.set(color='black', linewidth=0.85)  # 调整边框线的宽度为0.5
    #     box.set(facecolor=color)
    #
    # plt.gca().spines['top'].set_visible(False)
    # plt.gca().spines['right'].set_visible(False)
    #
    # plt.xlabel("Projects")
    # plt.ylabel("BIRC")
    # plt.title("Bug-Inducing Ratio per Commit")
    # plt.grid(False)
    # plt.tight_layout()
    # plt.savefig("BIRC.png", dpi=300)
    # plt.show()



    # 绘制 bug_introducing_commit_rate
    datas = []
    for itemname in all_cate_dict[catetory]:
        data = list(xx_dict['bug_introducing_commit_rate_item'][itemname].values())
        data = [x for x in data if x != 0]
        datas.append(data)

    bug_introducing_commit_rate_i6_25 = np.percentile(datas[item_index-1], q_percent)
    for d in xx_dict['bug_introducing_commit_rate_item'][iiitem]:
        if(xx_dict['bug_introducing_commit_rate_item'][iiitem][d]>=bug_introducing_commit_rate_i6_25):
            developer2.append(d)

    data = list(xx_dict['bug_introducing_commit_rate_total'].values())
    data = [x for x in data if x != 0]
    datas.append(data)
    #
    # plt.figure(figsize=(6, 4))
    # plt.rcParams["font.family"] = "Arial"
    # plt.rcParams["font.size"] = 12

    labels_len = len(datas) - 1
    labels = [f"#{i + 1}" for i in range(labels_len)]
    labels.append('total')

    # 设置全局字体大小
    plt.rcParams['font.size'] = 26

    # create boxplot with blue filled boxes, black outlier points, and normal (non-notched) box representation
    plt.figure(figsize=(20, 12))

    # Boxplot
    bplot = plt.boxplot(datas, patch_artist=True, medianprops=dict(color=(255 / 255, 0 / 255, 0 / 255,0.5), linewidth=2),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=3, linestyle='none'))

    # Set edge color and fill color
    for patch in bplot['boxes']:
        patch.set(facecolor=(31 / 255, 119 / 255, 180 / 255,0.3))  # fill with light blue
        patch.set(edgecolor='black')  # black border
    # (225 / 255, 129 / 255, 44 / 255,0.4) (31 / 255, 119 / 255, 180 / 255,0.3)(152 / 255, 185 / 255, 208 / 255,0.5)
    plt.xticks([1, 2, 3, 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], labels)
    plt.ylabel("PBIC\n")
    plt.xlabel("\nProjects")
    plt.title("Percentage of Bug-Inducing Commits\n")
    # 添加坐标轴刻度线与盒图之间的虚线
    # for i in range(len(datas)):
    #     plt.plot([i + 1, i + 1], [min(datas[i]), max(datas[i])], 'k--', lw=1)

    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性

    plt.show()


    # fig, ax = plt.subplots()
    # bp = ax.boxplot(datas, sym='.',  # 设置异常值的标记方式
    #                 labels=labels,  # x轴标记
    #                 boxprops={'color': (177 / 255, 204 / 255, 220 / 255), 'edgecolor': (72 / 255, 72 / 255, 72 / 255)},
    #                 # 箱线图箱部参数设置（填充颜色和边框颜色）
    #                 patch_artist=True,  # 填充箱子部分
    #                 capprops={'color': 'k'},  # 箱线图顶部横线设置
    #                 whiskerprops={'linestyle': '-'},  # 箱线图须部参数设置
    #                 medianprops={'color': 'white'},  # 中位数线参数设置（颜色为白色）
    #                 flierprops={'markerfacecolor': 'k', 'markeredgecolor': 'None'})  # 异常值标记参数设置
    # ax.set_title('Percentage of Bug-Inducing Commits')
    # ax.set_xlabel('Projects')
    # ax.set_ylabel('PBIC')
    # for box in bp['boxes']:
    #     box.set_facecolor((31 / 255, 119 / 255, 180 / 255))
    #     box.set_edgecolor((72 / 255, 72 / 255, 72 / 255))
    # plt.show()



    # bp = plt.boxplot(datas, labels=labels, notch=True, patch_artist=True)
    #
    # # plt.ylim(0, 13)
    #
    # colors = [f"#ADD8E6" for i in range(labels_len + 1)]
    # rgba_colors = [mcolors.to_rgba(color) for color in colors]
    #
    # for box, color in zip(bp['boxes'], rgba_colors):
    #     box.set(color='black', linewidth=0.85)  # 调整边框线的宽度为0.5
    #     box.set(facecolor=color)
    #
    # plt.gca().spines['top'].set_visible(False)
    # plt.gca().spines['right'].set_visible(False)
    #
    # plt.xlabel("Projects")
    # plt.ylabel("PBIC")
    # plt.title("Percentage of Bug-Inducing Commits")
    # plt.grid(False)
    # plt.tight_layout()
    # plt.savefig("PBIC.png", dpi=300)
    # plt.show()

    count=0
    for developer in developer1:
        if(developer in developer2):
            count+=1
    print(count)


def collect_3_2():
    #bug fixing commit count
    folder_path = "fixing_commit"
    count=0
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                content = json.load(file)
                count+=len(content)
    #print(count)

    #bug inducing commit count
    folder_path = "bug_inducing_commit"
    count = 0
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r") as file:
                    content = json.load(file)
                    count += len(content)

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)

    #print(count)


    #潜在的易引入bug的开发者，也就是引入过bug的开发者
    folder_path = "RQ1"
    count=0
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                content = json.load(file)
                co = list(content['number_inducing_commit'].keys())
                count+=len(co)
    print(count)

def draw_4_1():
    folder_path = "RQ2"
    cate_num_dict = {}
    cate_rate_dict = {}
    all_developer = 0
    all_BP=0
    count = 0
    list = []
    datas_num = []
    datas_rate = []
    for root, dirs, files in os.walk(folder_path):
        for dirname in dirs:
            dir_path = os.path.join(folder_path, dirname)
            data1 = []
            data2 = []
            for file_name in os.listdir(dir_path):
                file_path=os.path.join(dir_path, file_name)
                with open(file_path, "r") as file:
                    content = json.load(file)
                    data1.append(content['error_prone_developer_num'])
                    if (content['error_prone_developer_num'] != 0 and file_name not in list):
                        count += 1
                        list.append(file_name)
                    if(content['team_developer_num']==0):
                        data2.append(0)
                        continue
                    data2.append(content['error_prone_developer_num']/content['team_developer_num'])
                    # total = content['team_developer_num']
                    # all_developer+=total
                    # file=filename.split('.json')[0]
                    # num_dict[file]=content['error_prone_developer_num']
                    # rate_dict[file] = content['error_prone_developer_num']/total
                    # all_BP += num_dict[file]
            datas_num.append(data1)
            datas_rate.append(data2)
    # data_num=list(num_dict.values())
    # data_num.append(all_BP)
    #
    # data_rate = list(rate_dict.values())
    # data_rate.append(all_BP/all_developer)

    print(111)

    #data_num
    labels_len = len(datas_num)
    labels = cate_labels

    sorted_data, sorted_labels = zip(*sorted(zip(datas_num, labels), key=lambda x: -np.median(x[0])))

    # 设置全局字体大小
    plt.rcParams['font.size'] = 26

    # create boxplot with blue filled boxes, black outlier points, and normal (non-notched) box representation
    plt.figure(figsize=(20, 18))

    # Boxplot
    bplot = plt.boxplot(sorted_data, patch_artist=True,
                        medianprops=dict(color=(255 / 255, 0 / 255, 0 / 255, 0.5), linewidth=2),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=3, linestyle='none'))

    # Set edge color and fill color
    for patch in bplot['boxes']:
        patch.set(facecolor=(225 / 255, 129 / 255, 44 / 255,0.4))  # fill with light blue
        patch.set(edgecolor='black')  # black border
    # (225 / 255, 129 / 255, 44 / 255,0.4) (31 / 255, 119 / 255, 180 / 255,0.3)(152 / 255, 185 / 255, 208 / 255,0.5)
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], sorted_labels, rotation=45)
    plt.ylabel("Number\n")
    plt.xlabel("\nCategory")
    plt.title("Number of Attention-Worthy Developers\n")
    # 添加坐标轴刻度线与盒图之间的虚线
    # for i in range(len(datas)):
    #     plt.plot([i + 1, i + 1], [min(datas[i]), max(datas[i])], 'k--', lw=1)

    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.savefig("rq1-1.pdf")
    plt.show()


    # fig, ax = plt.subplots()
    # bp = ax.boxplot(datas_num, sym='.',  # 设置异常值的标记方式
    #                 labels=labels,  # x轴标记
    #                 boxprops={'color': (177 / 255, 204 / 255, 220 / 255), 'edgecolor': (72 / 255, 72 / 255, 72 / 255)},
    #                 # 箱线图箱部参数设置（填充颜色和边框颜色）
    #                 patch_artist=True,  # 填充箱子部分
    #                 capprops={'color': 'k'},  # 箱线图顶部横线设置
    #                 whiskerprops={'linestyle': '-'},  # 箱线图须部参数设置
    #                 medianprops={'color': 'white'},  # 中位数线参数设置（颜色为白色）
    #                 flierprops={'markerfacecolor': 'k', 'markeredgecolor': 'None'})  # 异常值标记参数设置
    # ax.set_title('Number of Required Extra Attention Developer')
    # ax.set_xlabel('Category')
    # ax.set_ylabel('Number')
    # for box in bp['boxes']:
    #     box.set_facecolor((31 / 255, 119 / 255, 180 / 255))
    #     box.set_edgecolor((72 / 255, 72 / 255, 72 / 255))
    # plt.show()



    # plt.figure(figsize=(6, 4))
    # plt.rcParams["font.family"] = "Arial"
    # plt.rcParams["font.size"] = 12
    #
    # labels_len = len(datas_num)
    # labels = [f"@{i + 1}" for i in range(labels_len)]
    # # labels.append('total')
    # bp = plt.boxplot(datas_num, labels=labels, notch=True, patch_artist=True)
    #
    # # plt.ylim(0, 100)
    #
    # colors = [f"#ADD8E6" for i in range(labels_len)]
    # rgba_colors = [mcolors.to_rgba(color) for color in colors]
    #
    # for box, color in zip(bp['boxes'], rgba_colors):
    #     box.set(color='black', linewidth=0.85)  # 调整边框线的宽度为0.5
    #     box.set(facecolor=color)
    #
    # plt.gca().spines['top'].set_visible(False)
    # plt.gca().spines['right'].set_visible(False)
    #
    # plt.xlabel("Category")
    # plt.ylabel("Number")
    # plt.title("Number of Required Extra Attention Developer")
    # plt.grid(False)
    # plt.tight_layout()
    # plt.savefig("READ N.png", dpi=300)
    # plt.show()

    # data_rate
    labels_len = len(datas_rate)
    labels = cate_labels

    sorted_data, sorted_labels = zip(*sorted(zip(datas_rate, labels), key=lambda x: -np.median(x[0])))


    # 设置全局字体大小
    plt.rcParams['font.size'] = 26

    # create boxplot with blue filled boxes, black outlier points, and normal (non-notched) box representation
    plt.figure(figsize=(20, 18))

    # Boxplot
    bplot = plt.boxplot(sorted_data, patch_artist=True,
                        medianprops=dict(color=(255 / 255, 0 / 255, 0 / 255, 0.5), linewidth=2),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=3, linestyle='none'))

    # Set edge color and fill color
    for patch in bplot['boxes']:
        patch.set(facecolor=(31 / 255, 119 / 255, 180 / 255,0.3))  # fill with light blue
        patch.set(edgecolor='black')  # black border
    # (225 / 255, 129 / 255, 44 / 255,0.4) (31 / 255, 119 / 255, 180 / 255,0.3)(152 / 255, 185 / 255, 208 / 255,0.5)
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], sorted_labels, rotation=45)
    plt.ylabel("Percentage\n")
    plt.xlabel("\nCategory")
    plt.title("Percentage of Attention-Worthy Developers\n")
    # 添加坐标轴刻度线与盒图之间的虚线
    # for i in range(len(datas)):
    #     plt.plot([i + 1, i + 1], [min(datas[i]), max(datas[i])], 'k--', lw=1)

    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.savefig("rq1-2.pdf")
    plt.show()
    pr = []
    for k in datas_rate:
        dada = []
        for v in k:
            dada.append(round(v, 4))
        pr.append(dada)

    print(111)

    # fig, ax = plt.subplots()
    # bp = ax.boxplot(datas_rate, sym='.',  # 设置异常值的标记方式
    #                 labels=labels,  # x轴标记
    #                 boxprops={'color': (177 / 255, 204 / 255, 220 / 255), 'edgecolor': (72 / 255, 72 / 255, 72 / 255)},
    #                 # 箱线图箱部参数设置（填充颜色和边框颜色）
    #                 patch_artist=True,  # 填充箱子部分
    #                 capprops={'color': 'k'},  # 箱线图顶部横线设置
    #                 whiskerprops={'linestyle': '-'},  # 箱线图须部参数设置
    #                 medianprops={'color': 'white'},  # 中位数线参数设置（颜色为白色）
    #                 flierprops={'markerfacecolor': 'k', 'markeredgecolor': 'None'})  # 异常值标记参数设置
    # ax.set_title('Percentage of Required Extra Attention Developer')
    # ax.set_xlabel('Category')
    # ax.set_ylabel('Percentage')
    # for box in bp['boxes']:
    #     box.set_facecolor((31 / 255, 119 / 255, 180 / 255))
    #     box.set_edgecolor((72 / 255, 72 / 255, 72 / 255))
    # plt.show()


    # plt.figure(figsize=(6, 4))
    # plt.rcParams["font.family"] = "Arial"
    # plt.rcParams["font.size"] = 12
    #
    # labels_len = len(datas_rate)
    # labels = [f"@{i + 1}" for i in range(labels_len)]
    # # labels.append('total')
    # bp = plt.boxplot(datas_rate, labels=labels, notch=True, patch_artist=True)
    #
    # # plt.ylim(0, 100)
    #
    # colors = [f"#ADD8E6" for i in range(labels_len)]
    # rgba_colors = [mcolors.to_rgba(color) for color in colors]
    #
    # for box, color in zip(bp['boxes'], rgba_colors):
    #     box.set(color='black', linewidth=0.85)  # 调整边框线的宽度为0.5
    #     box.set(facecolor=color)
    #
    # plt.gca().spines['top'].set_visible(False)
    # plt.gca().spines['right'].set_visible(False)
    #
    # plt.xlabel("Category")
    # plt.ylabel("Percentage")
    # plt.title("Percentage of Required Extra Attention Developer")
    # plt.grid(False)
    # plt.tight_layout()
    # plt.savefig("READ P.png", dpi=300)
    # plt.show()


cate_labels = []

def draw_4_2():

    #获取所有项目的总文件数量
    folder_path = "RQ3"
    item_file_count = {}
    for root, dirs, files in os.walk(folder_path):
        for dirname in dirs:
            dir_path = os.path.join(folder_path, dirname)
            for file_name in os.listdir(dir_path):
                file_path=os.path.join(dir_path, file_name)
                with open(file_path, "r") as file:
                    content = json.load(file)
                    item_file_count[file_name.split('.json')[0].split('_')[0]]=content['all_file_num']

    folder_path = "real_file_bug_paint_RQ3"
    datas_num = []
    datas_rate = []
    median_dict = {}
    median_dict_rate = {}
    for root, dirs, files in os.walk(folder_path):
        for dirname in dirs:
            dir_path = os.path.join(folder_path, dirname)
            data1 = []
            data2 = []

            for file_name in os.listdir(dir_path):
                xx_dict1 = {}
                xx_dict2 = {}
                xx_dict3 = {}
                file_path = os.path.join(dir_path, file_name)
                with codecs.open(file_path, encoding='utf-8-sig') as f:
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
                    d = list(xx_dict1.values())
                    float_list = [float(item) for item in d]
                    data1.extend(float_list)
                    file_num = item_file_count[file_name.split('.csv')[0]]
                    for i in list(xx_dict1.values()):
                        data2.append(round(file_num*float(i)))
            datas_num.append(data2)
            datas_rate.append(data1)
            median_dict[dirname]=np.median(data2)
            median_dict_rate[dirname]=np.median(data1)
            # print(111)

    print(111)
    labels_len = len(datas_num)
    labels = cate_labels

    sorted_data, sorted_labels = zip(*sorted(zip(datas_num, labels), key=lambda x: -np.median(x[0])))


    # 设置全局字体大小
    plt.rcParams['font.size'] = 26

    # create boxplot with blue filled boxes, black outlier points, and normal (non-notched) box representation
    plt.figure(figsize=(20, 18))

    # Boxplot
    bplot = plt.boxplot(sorted_data, patch_artist=True,
                        medianprops=dict(color=(255 / 255, 0 / 255, 0 / 255, 0.5), linewidth=2),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=3, linestyle='none'))

    # Set edge color and fill color
    for patch in bplot['boxes']:
        patch.set(facecolor=(225 / 255, 129 / 255, 44 / 255, 0.4))  # fill with light blue
        patch.set(edgecolor='black')  # black border
    # (225 / 255, 129 / 255, 44 / 255,0.4) (31 / 255, 119 / 255, 180 / 255,0.3)(152 / 255, 185 / 255, 208 / 255,0.5)
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], sorted_labels, rotation=45)
    plt.ylabel("Number of Files")
    plt.xlabel("\nCategory")
    plt.title("Number of Files Participated by AWD\n")
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.savefig("rq2-1.pdf")
    plt.show()


    count2000=0
    for k in datas_num[9]:
        if(k>2000):
            count2000+=1
    print(111)

    # data_rate
    # plt.figure(figsize=(6, 4))
    # plt.rcParams["font.family"] = "Arial"
    # plt.rcParams["font.size"] = 12
    #
    # labels_len = len(datas_rate)
    # labels = [f"@{i + 1}" for i in range(labels_len)]
    # # labels.append('total')
    # bp = plt.boxplot(datas_rate, labels=labels, notch=True, patch_artist=True,whis=None)
    #
    # # plt.ylim(0, 100)
    #
    # colors = [f"#ADD8E6" for i in range(labels_len)]
    # rgba_colors = [mcolors.to_rgba(color) for color in colors]
    #
    # for box, color in zip(bp['boxes'], rgba_colors):
    #     box.set(color='black', linewidth=0.85)  # 调整边框线的宽度为0.5
    #     box.set(facecolor=color)
    #
    # plt.gca().spines['top'].set_visible(False)
    # plt.gca().spines['right'].set_visible(False)
    #
    # plt.xlabel("Category")
    # plt.ylabel("Percentage of Files")
    # plt.title("Percentage of Files Participated by READ")
    # plt.grid(False)
    # plt.tight_layout()
    # plt.savefig("READ P.png", dpi=300)
    # plt.show()
    # print(111)
    labels_len = len(datas_rate)
    labels = cate_labels

    sorted_data, sorted_labels = zip(*sorted(zip(datas_rate, labels), key=lambda x: -np.median(x[0])))


    # 设置全局字体大小
    plt.rcParams['font.size'] = 26

    # create boxplot with blue filled boxes, black outlier points, and normal (non-notched) box representation
    plt.figure(figsize=(20, 18))

    # Boxplot
    bplot = plt.boxplot(sorted_data, patch_artist=True,
                        medianprops=dict(color=(255 / 255, 0 / 255, 0 / 255, 0.5), linewidth=2),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=3, linestyle='none'))

    # Set edge color and fill color
    for patch in bplot['boxes']:
        patch.set(facecolor= (31 / 255, 119 / 255, 180 / 255,0.3))  # fill with light blue
        patch.set(edgecolor='black')  # black border
    # (225 / 255, 129 / 255, 44 / 255,0.4) (31 / 255, 119 / 255, 180 / 255,0.3)(152 / 255, 185 / 255, 208 / 255,0.5)
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], sorted_labels, rotation=45)
    plt.ylabel("Percentage of Files\n")
    plt.xlabel("\nCategory")
    plt.title("Percentage of Files Participated by AWD\n")
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.savefig("rq2-2.pdf")
    plt.show()

    # fig, ax = plt.subplots()
    # bp = ax.boxplot(datas_rate, sym='.',  # 设置异常值的标记方式
    #                 labels=labels,  # x轴标记
    #                 boxprops={'color': (177 / 255, 204 / 255, 220 / 255), 'edgecolor': (72 / 255, 72 / 255, 72 / 255)},
    #                 # 箱线图箱部参数设置（填充颜色和边框颜色）
    #                 patch_artist=True,  # 填充箱子部分
    #                 capprops={'color': 'k'},  # 箱线图顶部横线设置
    #                 whiskerprops={'linestyle': '-'},  # 箱线图须部参数设置
    #                 medianprops={'color': 'white'},  # 中位数线参数设置（颜色为白色）
    #                 flierprops={'markerfacecolor': 'k', 'markeredgecolor': 'None'})  # 异常值标记参数设置
    # ax.set_title('Percentage of Files Participated by READ')
    # ax.set_xlabel('Category')
    # ax.set_ylabel('Percentage of Files')
    # for box in bp['boxes']:
    #     box.set_facecolor((31 / 255, 119 / 255, 180 / 255))
    #     box.set_edgecolor((72 / 255, 72 / 255, 72 / 255))
    # # 旋转 x 轴标签 45 度以提高可读性
    # plt.xticks(rotation=90, ha='right')
    #
    # plt.tight_layout()  # 可选的，调整布局以防止标签被截断
    # plt.show()
    # print(111)

def draw_4_3():
        # 假设每个小图有三个类别，每个类别有两个子类别的数据
        categories = ['5 commit', '10 commit', '15commit']
        sub_categories = ['Number of LTAWDs with no improvement', 'Number of LTAWDs with improvement']
        data = np.array([
            [[90, 34], [66, 15], [21, 14]],
            [[7, 4], [6, 1], [6, 1]],
            [[14, 5], [9, 1], [5, 0]],
            [[5, 1], [5, 1], [5, 1]],
            [[48, 9], [44, 7], [41, 7]],
            [[5, 2], [5, 2], [5, 1]],
            [[6, 4], [5, 3], [3, 2]],
            [[32, 7], [27, 4], [23, 3]],
            [[7, 9], [6, 9], [6, 9]],
            [[94, 21], [77, 13], [64, 12]],
            [[12, 4], [11, 3], [9, 3]],
            [[31, 6], [30, 4], [29, 4]],
            [[24, 16], [20, 7], [15, 7]],
            [[17, 3], [16, 3], [14, 3]],
            [[9, 3], [8, 2], [7, 2]],
        ])
        fig, axs = plt.subplots(2, 8, figsize=(22, 6))
        l = ['big-data', 'build-management', 'cloud', 'content', 'database', 'graphics', 'http', 'java', 'javaee', 'library',
             'network-client', 'network-server', 'other', 'web-framework', 'xml']
        bar_width = 0.4  # 设置较细的柱子宽度

        # 设置柱子的颜色
        colors = [(31 / 255, 119 / 255, 180 / 255), (177 / 255, 204 / 255, 220 / 255)]
        for i, ax in enumerate(axs.flat):
            if i == 15:
                break
            x = np.arange(len(categories))
            bottom = np.zeros(len(categories))
            for j in range(len(sub_categories)):
                ax.bar(x, data[i][:, j], label=sub_categories[j], bottom=bottom, width=bar_width, color=colors[j])
                bottom += data[i][:, j]

            ax.set_title(l[i])
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend()
            # 让小图不显示图例
            ax.legend([])
        # plt.tight_layout()
        # 创建一个位于子图外的共同图例
        handles, labels = axs[0, 0].get_legend_handles_labels()
        lgd = fig.legend(handles, labels, loc='upper left', prop={'size': 7}, bbox_to_anchor=(0.9, 1.05))  #
        plt.delaxes(axs[1, 7])
        plt.tight_layout()
        plt.savefig('4_3.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.show()
    #
    # # 假设每个小图有三个类别，每个类别有两个子类别的数据
    # categories = ['5 commit', '10 commit', '15commit']
    # sub_categories = ['Number of Not Continuous Improved READ', 'Number of Continuous Improved READ']
    # data = np.array([
    #     [[37, 22], [28, 7], [20, 7]],
    #     [[0, 2], [0, 0], [0, 0]],
    #     [[3, 0], [3, 0], [3, 0]],
    #     [[38, 7], [34, 6], [31, 6]],
    #     [[1, 1], [1, 1], [1, 1]],
    #     [[5, 2], [4, 2], [2, 2]],
    #     [[28, 5], [26, 4], [22, 3]],
    #     [[3, 3], [3, 3], [3, 3]],
    #     [[4, 2], [2, 1], [2, 1]],
    #     [[27, 7], [25, 6], [21, 6]],
    #     [[70, 27], [67, 22], [62, 21]],
    #     [[13, 12], [12, 4], [9, 4]],
    #     [[9, 1], [8, 1], [8, 1]],
    #     [[31, 6], [23, 5], [21, 5]],
    #     [[31, 6], [23, 5], [21, 5]],
    # ])
    # fig, axs = plt.subplots(2, 7, figsize=(22, 8))
    # l = ['big-data','build-management','content','database','graphics','http','java','javaee','library','network-client','network-server','other','web-framework','xml']
    # bar_width = 0.4  # 设置较细的柱子宽度
    #
    # # 设置柱子的颜色
    # colors = [(31 / 255, 119 / 255, 180 / 255), (177 / 255, 204 / 255, 220 / 255)]
    # for i, ax in enumerate(axs.flat):
    #     x = np.arange(len(categories))
    #     bottom = np.zeros(len(categories))
    #     for j in range(len(sub_categories)):
    #         ax.bar(x, data[i][:, j], label=sub_categories[j], bottom=bottom, width=bar_width, color=colors[j])
    #         bottom += data[i][:, j]
    #
    #     ax.set_title(l[i])
    #     ax.set_xticks(x)
    #     ax.set_xticklabels(categories)
    #     ax.legend()
    #     # 让小图不显示图例
    #     ax.legend([])
    # # 创建一个位于子图外的共同图例
    # handles, labels = axs[0, 0].get_legend_handles_labels()
    # fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.83, 1.0))
    # plt.tight_layout()
    # plt.show()


def draw_4_4():
    induce_path = './bug_inducing_commit/'
    cate_dir_list = os.listdir(induce_path)
    # cate_dir_list = ['#big-data']
    print(cate_dir_list)
    all_cate_dict = {}
    all_item_dict={}
    for cate in cate_dir_list:
        induce_file_list = os.listdir(induce_path + cate)
        all_cate_dict[cate] = []
        for induce_file in induce_file_list:
            item_name = induce_file.split('_')[2].split('.')[0]
            all_item_dict[item_name] = cate
            all_cate_dict[cate].append(item_name)
    datas=[]
    for c in all_cate_dict.keys():
        xx_dict = {}
        data=[]
        for itemname in all_cate_dict[c]:
            rq5_path = './RQ5/' + c + '/' + itemname + '.json'
            with open(rq5_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)  # 读取json文件
                de = json_data['developer']
                for k in de.keys():
                    if (de[k]['is_error_developer_apache_item_count']>1):
                        data.append(de[k]['is_error_developer_apache_item_count'])
        datas.append(data)
    labels = cate_labels

    # 设置全局字体大小
    plt.rcParams['font.size'] = 26

    # create boxplot with blue filled boxes, black outlier points, and normal (non-notched) box representation
    plt.figure(figsize=(20, 18))

    # Boxplot
    bplot = plt.boxplot(datas, patch_artist=True,
                        medianprops=dict(color=(255 / 255, 0 / 255, 0 / 255, 0.5), linewidth=2),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=3, linestyle='none'))

    # Set edge color and fill color
    for patch in bplot['boxes']:
        patch.set(facecolor=(31 / 255, 119 / 255, 180 / 255, 0.3))  # fill with light blue
        patch.set(edgecolor='black')  # black border
    # (225 / 255, 129 / 255, 44 / 255,0.4) (31 / 255, 119 / 255, 180 / 255,0.3)(152 / 255, 185 / 255, 208 / 255,0.5)
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], labels, rotation=45)
    plt.ylabel("Number of Projects to Attention\n")
    plt.xlabel("\nCategory")
    plt.title("Performance of AWD in Multiple Projects\n")
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # 添加y轴的网格线，增强可读性
    plt.show()

    # fig, ax = plt.subplots()
    # bp = ax.boxplot(datas, sym='.',  # 设置异常值的标记方式
    #                 labels=labels,  # x轴标记
    #                 boxprops={'color': (177 / 255, 204 / 255, 220 / 255), 'edgecolor': (72 / 255, 72 / 255, 72 / 255)},
    #                 # 箱线图箱部参数设置（填充颜色和边框颜色）
    #                 patch_artist=True,  # 填充箱子部分
    #                 capprops={'color': 'k'},  # 箱线图顶部横线设置
    #                 whiskerprops={'linestyle': '-'},  # 箱线图须部参数设置
    #                 medianprops={'color': 'white'},  # 中位数线参数设置（颜色为白色）
    #                 flierprops={'markerfacecolor': 'k', 'markeredgecolor': 'None'})  # 异常值标记参数设置
    # ax.set_title('Performance of READ in Multiple Projects')
    # ax.set_xlabel('Category')
    # ax.set_ylabel('Number of Projects to Attention')
    # for box in bp['boxes']:
    #     box.set_facecolor((31 / 255, 119 / 255, 180 / 255))
    #     box.set_edgecolor((72 / 255, 72 / 255, 72 / 255))
    # # 旋转 x 轴标签 45 度以提高可读性
    # plt.xticks(rotation=90, ha='right')
    #
    # plt.tight_layout()  # 可选的，调整布局以防止标签被截断
    # plt.show()

def calculate_long_time_no_promote():
    # 获取所有项目的总文件数量
    folder_path = "RQ4"
    dict = {}
    for files in os.listdir(folder_path):
        if(files.endswith('.json')):
            dir_path = os.path.join(folder_path, files)
            with open(dir_path, "r") as file:
                content = json.load(file)
                developer_list = []
                developer_time = content['commiter_contribute_time']
                for d in developer_time.keys():
                    if(developer_time[d]>=180 and d in content['daily_long_time_error_prone_developer']):
                        developer_list.append(d)
                no_imporve_d_count = 0
                for d in developer_list:
                    if(content['commiter_contribute_time1'][d]['bug_num_per_commit']>=content['commiter_contribute_time2'][d]['bug_num_per_commit']):
                        if (content['commiter_contribute_time2'][d]['bug_num_per_commit'] >=content['commiter_contribute_time3'][d]['bug_num_per_commit']):
                            if (content['commiter_contribute_time3'][d]['bug_num_per_commit'] >=content['commiter_contribute_time4'][d]['bug_num_per_commit']):
                                if(content['commiter_contribute_time4'][d]['bug_num_per_commit']==0):
                                    continue
                                no_imporve_d_count+=1
                                continue
                    if (content['commiter_contribute_time1'][d]['bug_commit_num_rate'] >=
                            content['commiter_contribute_time2'][d]['bug_commit_num_rate']):
                        if (content['commiter_contribute_time2'][d]['bug_commit_num_rate'] >=
                                content['commiter_contribute_time3'][d]['bug_commit_num_rate']):
                            if (content['commiter_contribute_time3'][d]['bug_commit_num_rate'] >=
                                    content['commiter_contribute_time4'][d]['bug_commit_num_rate']):
                                if (content['commiter_contribute_time4'][d]['bug_commit_num_rate'] == 0):
                                    continue
                                no_imporve_d_count += 1
                # for d in developer_list:
                #     if(content['commiter_contribute_time1'][d]['bug_num_per_commit']>=content['commiter_contribute_time2'][d]['bug_num_per_commit'] and content['commiter_contribute_time1'][d]['bug_commit_num_rate'] >=
                #             content['commiter_contribute_time2'][d]['bug_commit_num_rate']):
                #         if (content['commiter_contribute_time2'][d]['bug_num_per_commit'] >=content['commiter_contribute_time3'][d]['bug_num_per_commit']and content['commiter_contribute_time2'][d]['bug_commit_num_rate'] >=
                #                 content['commiter_contribute_time3'][d]['bug_commit_num_rate']):
                #             if (content['commiter_contribute_time3'][d]['bug_num_per_commit'] >=content['commiter_contribute_time4'][d]['bug_num_per_commit'] and content['commiter_contribute_time3'][d]['bug_commit_num_rate'] >=
                #                     content['commiter_contribute_time4'][d]['bug_commit_num_rate']):
                #                 if(content['commiter_contribute_time4'][d]['bug_num_per_commit']==0 or content['commiter_contribute_time4'][d]['bug_commit_num_rate'] == 0):
                #                     continue
                #                 no_imporve_d_count+=1

                dict[files]=no_imporve_d_count
    print(111)

def get_RQ4_DATA():
    # 获取所有项目的总文件数量
    folder_path = "RQ4"
    dict = {}
    for files in os.listdir(folder_path):
        if (files.endswith('.json')):
            dir_path = os.path.join(folder_path, files)
            with open(dir_path, "r") as file:
                content = json.load(file)
                dict[files] = content['number_improved_daily_long_time_error_prone_developer']
    print(111)

def get_one_commit_one_bug_developer_count():
    # 获取所有项目的总文件数量
    folder_path = "RQ1"
    dict = {}
    for files in os.listdir(folder_path):
        if (files.endswith('.json')):
            dir_path = os.path.join(folder_path, files)
            with open(dir_path, "r") as file:
                content = json.load(file)
                developer_commit=content['commiter_commit_number']
                developer_bug=content['commiter_bug_number']
                dict[files]=0
                for d in developer_commit.keys():
                    try:
                        if(developer_commit[d]==1 and developer_bug[d]>=1):
                            dict[files]+=1
                    except:
                        continue
    print(111)

def draw_3_1_zhengtaifenbu():
    induce_path = './bug_inducing_commit/'
    # cate_dir_list = os.listdir(induce_path)
    catetory = '#big-data'
    cate_dir_list = [catetory]
    print(cate_dir_list)

    all_cate_dict = {}
    for cate in cate_dir_list:
        induce_file_list = os.listdir(induce_path + cate)
        all_cate_dict[cate] = []
        for induce_file in induce_file_list:
            item_name = induce_file.split('_')[2].split('.')[0]
            all_cate_dict[cate].append(item_name)


    for c in all_cate_dict.keys():
        xx_dict = {}
        xx_dict['ABC'] = {}
        xx_dict['PBC'] = {}
        for itemname in all_cate_dict[c]:
            rq1_path = './RQ1/' + c + '/' + itemname + '_metrics.json'
            with open(rq1_path, 'r', encoding='gbk') as fp:
                json_data = json.load(fp)  # 读取json文件
            Merge(json_data['number_of_introduce_bugs_per_commit'],
                  xx_dict['ABC'])
            Merge(json_data['bug_introducing_commit_rate'], xx_dict['PBC'])
        aaa = list(xx_dict['ABC'].values())
        aaa1 = [x for x in aaa if x != 0]
        bbb = list(xx_dict['PBC'].values())
        bbb1 = [x for x in bbb if x != 0]
        plt.hist(aaa1, bins=20, edgecolor='black')
        plt.title("ABC")
        plt.show()
        plt.hist(bbb1,bins=20,edgecolor='black')
        plt.title("PBC")
        plt.show()
        print(111)


if __name__ =="__main__":
    folder_path = "RQ3"
    cate_labels = ['big-data', 'build-M', 'cloud', 'content', 'database', 'graphics', 'http', 'java', 'javaee', 'library','N-client', 'N-server', 'other', 'web-FW', 'xml']
    # draw_3_1_a()
    # draw_3_1_zhengtaifenbu()
    #collect_3_2()
    # draw_4_1()
    draw_4_2()
    # draw_4_3()
    # draw_4_4()
    # calculate_long_time_no_promote()
    # get_RQ4_DATA()
    # get_one_commit_one_bug_developer_count()