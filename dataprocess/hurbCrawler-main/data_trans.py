import csv
import json
import random
import re
#通过medicineTable 构造QA数据集
# 得到train.json
file_path = "medicineTable.csv"
output="train.json"
#从csv读取数据[{"key":"value"}]
file=open(file_path,encoding="utf-8")
data = file.readlines()
dict_list=[]
for item in data:
    eles=re.findall(r'[{](.*?)[}]',item)
    dict = {}
    for ele in eles:
        key,value=re.findall(r"['](.*?)[']",ele)
        dict[key]=value
    dict_list.append(dict)
# print(dict_list)
#将一条数据拼接成问答形式 json{"question":"value","answer":"value"}
#设计问题：
# 1.能推荐主治xx的方剂给我么 回答：推荐(方名)，”处方“，,该方“用法用量”，炮制过程为“炮制”，
# 2.xx方剂是什么？ 回答：方名：处方。此方来自“出处”,该方“用法用量”，炮制过程为“炮制”，
# 3.对“主治”应该怎么开方子？
# 4.我得了“主治” 回答：推荐您：
# 5.”主治“ 回答：方名，处方，。。
for item in dict_list:
    try:
        # print(item)
        type = random.choice([1,2,3,4,5])
        json_data={}
        if type==1:
            question="能推荐主治"+item["主治"]+"的方剂给我么"
            if("炮制" in item.keys()):
                answer=item["方名"]+"效果可以，抓取"+item["处方"]+"该方"+item["用法用量"]+"炮制过程为"+item["炮制"]
            else:
                answer=item["方名"]+"效果可以，抓取"+item["处方"]+"该方"+item["用法用量"]
            pass
        elif type==2:
            question = item["方名"] + "是什么"
            if ("炮制" in item.keys()):
                answer = item["方名"] + "是中药方剂，其处方为:" + item["处方"] +"该方主治："+item["主治"]+ "该方出自"+item["出处"] + "。该方的用法用量是"+item["用法用量"] + "炮制过程为" + item["炮制"]
            else:
                answer = item["方名"] + "是中药方剂，其处方为:" + item["处方"] +"该方主治："+item["主治"]+ "该方出自" + item["出处"] + "。该方的用法用量是" + item["用法用量"]
            pass
        elif type==3:
            question = "对" + item["主治"] + "怎么开方"
            if ("炮制" in item.keys()):
                answer = "可以参考"+item["方名"] + "，抓取" + item["处方"] + "。该方" + item["用法用量"] + "炮制过程为" + item["炮制"]
            else:
                answer = "可以参考" + item["方名"] + "，抓取" + item["处方"] + "。该方" + item["用法用量"]
            pass
        elif type==4:
            question = "我需要" + item["主治"]
            if ("炮制" in item.keys()):
                answer = "针对您的主治症状,我给您开方"+item["方名"] + "，抓取" + item["处方"] + "该方" + item["用法用量"] + "炮制过程为" + item["炮制"]
            else:
                answer = "针对您的主治症状,我给您开方"+item["方名"] + "，抓取" + item["处方"] + "该方" + item["用法用量"]
            pass
        else:
            question = "针对" + item["主治"]+"开方"
            if ("炮制" in item.keys()):
                answer = "针对该症状,我给您开方"+item["方名"] + "，抓取" + item["处方"] + "该方" + item["用法用量"] + ",炮制过程为" + item["炮制"]
            else:
                answer = "针对该症状,我给您开方" + item["方名"] + "，抓取" + item["处方"] + "该方" + item["用法用量"]
            pass
        json_data = {"question": question, "answer": answer}
        print(json_data)
        with open("train.json",'a+',encoding='utf-8') as fp:
            json.dump(json_data, fp,ensure_ascii=False)
            fp.write("\n")
            fp.close()
            pass
    except Exception as e:
        # print(e)
        continue



