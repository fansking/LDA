import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.externals import joblib

def getData(dataPath:str):
    fr=open(dataPath,'r')
    line=fr.readline()
    data=[]
    while line!=None and line!='':
        data.append(line)
        line=fr.readline()
    return data


def recomment(name:str,dataPath:str):
    tf_ModelPath = os.path.join('usermodel/'+name+'/model', 'tfVector.model')  # 保存词频模型
    bestModelPath=os.path.join('usermodel/'+name+'/model', 'bestLDAModel.model')
    data=getData(dataPath)
    tf_vectorizer = joblib.load(tf_ModelPath)
    lda=joblib.load(bestModelPath)
    tf=tf_vectorizer.transform(data)
    res=lda.transform(tf)
    for i in range(len(res)):
        for j in range(len(res[i])):
            if res[i][j]>0.6:
                print(j,'   ',data[i])
                break

recomment('xjghy','1.txt')