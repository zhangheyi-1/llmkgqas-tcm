import json
import time
from textrank4zh import TextRank4Keyword
import requests

file_path = "questions.txt"  # 替换为你的文件路径
with open(file_path, "r",encoding='utf-8') as file:
    contents = file.read()
questions = contents.split("\n\n")
questions = questions[8001:] #改成[8001:]
entities = []
prompts = []
i = 0
for question in questions:
    mentioned = []
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=question, lower=True, window=2)
    for item in tr4w.get_keywords(20, word_min_len=1):
        if item.weight > 0.1:
            mentioned.append(item.word)
    if i % 5 == 0:
        print(i)
        print(question)
        print(mentioned)

    url = "https://api.ownthink.com/kg/knowledge"
    for mention in mentioned:
        if mention in entities:
            continue
        triplets = []
        params = {"entity": mention}
        entities.append(mention)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # 如果发生网络请求错误，会抛出异常
            time.sleep(1)
            if response.ok and response.text is not None:
                text = json.loads(response.text)
                if 'desc' in text['data'] and 'avp' in text['data']:
                    desc = text['data']['desc']
                    avp = text['data']['avp']
                    for item in avp:
                        triplets.append(mention + '->' + item[0] + '->' + item[1])
                    data = {'entity': mention, 'desc': desc, 'triplets': triplets}
                    if i % 5 == 0:
                        print(data)
                    if data not in prompts:
                        prompts.append(data)
                else:
                    print(mention, response.text)
        except requests.exceptions.RequestException as e:
            print(f"{mention}网络请求错误: {e}")
    i += 1

json_data = json.dumps(prompts, indent=4, ensure_ascii=False)
# 将JSON字符串写入文件
file_path = "kg.json"  # 替换为你想要保存的文件路径
with open(file_path, "w", encoding='utf-8') as file:
    file.write(json_data)