import requests
import prompts
questions=[]
answers=[]
#获取问题列表 object 
with open("question.txt", "r", encoding='utf-8') as f:  #打开文本
    data = f.readlines()   #读取文本
    n = 0
    for item in data:
        n=n+1
        print(n,item)
        if(n % 3==1):
            questions.append(item)
    print(questions)
for query in questions:
    print(query)
    #选择合适的prompt回答
    #query = prompts.getprompts(query,6)
    #query = prompts.getprompts(query,2)
    #query = prompts.getprompts(query,3)
    r = requests.post('http://127.0.0.1:8100/', json={"prompt": query, "history": []},headers={'Content-Type':'application/json'})
    print(r.json())
    response=r.json()["response"]
    answers.append(response)
    print(answers)
with open("answer.txt", "a", encoding='utf-8') as f:  #打开文本
    for it in answers:
        f.write(it+"\n"+"\n"+"\n")
print("OK")

