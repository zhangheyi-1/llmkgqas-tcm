# -*- coding: utf-8 -*-
"""
DataLoder For Chinese Medical Dialogue Dataset
"""
import json

def getdata():
    train_document_number=1241
    test_document_number=413
    dev_document_number=413
    traindata={}
    testdata={}
    devdata={}
    for i in range(train_document_number):
        with open("train/train_"+str(i)+'.json',encoding="utf8") as f:
            traindocument=json.load(f)
            traindata[traindocument['example-id']]=traindocument['dialogue-content']
    for i in range(test_document_number):
        with open("test/test_"+str(i)+'.json',encoding="utf8") as f:
            testdocument=json.load(f)
            testdata[testdocument['example-id']]=testdocument['dialogue-content']
    for i in range(dev_document_number):
        with open("dev/dev_"+str(i)+'.json',encoding="utf8") as f:
            devdocument=json.load(f)
            devdata[devdocument['example-id']]=devdocument['dialogue-content']
    return traindata,testdata,devdata

traindata,testdata,devdata=getdata()
totaldata={}
totaldata.update(traindata)
totaldata.update(testdata)
totaldata.update(devdata)
