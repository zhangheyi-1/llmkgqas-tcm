# coding=utf-8
import json
#将问答.xls 转换为json
import xlrd

def get_data(dir_case, sheetnum):
    # 如果路径下xlsx文件很多，可以把文件名做一个拼接传入文件名这个参数
    # dir_case = 'F:\\code\\csdn\\cese_excel\\' + filename + '.xlsx'
    '''
获取其中一张sheet
table = data.sheet_by_name(data.sheet_names()[0])
sheet的行数与列数
table.nrows, table.ncols
    '''
    data = xlrd.open_workbook(dir_case)
    table = data.sheets()[sheetnum]
    nor = table.nrows
    nol = table.ncols
    dict = {}
    for i in range(1, nor):
        for j in range(nol):
            title = table.cell_value(0, j)
            value = table.cell_value(i, j)
            # print value
            dict[title] = value
        yield dict
'''        
• yield 是一个类似 return 的关键字，只是这个函数返回的是个生成器
• 当你调用这个函数的时候，函数内部的代码并不立马执行 ，这个函数只是返回一个生成器对象
• 当你使用for进行迭代的时候，函数中的代码才会执行
'''
if __name__ == '__main__':
    for i in get_data('问答.xls', 0):
        dict={}
        dict["question"]=i["question"]
        dict["answer"]=i["answer"]
        with open("train2.json","a+",encoding="utf-8") as fp:
            json.dump(dict,fp,ensure_ascii=False)
            fp.write("\n")
            fp.close()
        print(i)
