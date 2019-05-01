from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.externals import joblib
import os
from time import time
n_topics = list(range(4, 20, 2))
perplexityLst = [1.0] * len(n_topics)
n_top_words = 40

def print_top_words(model, feature_names, n_top_words,name:str):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()
    with open(os.path.join('usermodel/'+name+'/result', 'res_topic_word.csv'), 'w') as f:
        f.write("Topic, Top Word\n")
        for topic_idx, topic in enumerate(model.components_):
            f.write(str(topic_idx) + ',')
            topic_word_dist = [(feature_names[i], topic[i]) for i in topic.argsort()[:-n_top_words - 1:-1]]
            for word, score in topic_word_dist:
                f.write(word + '#' + str(score) + ';')
            f.write('\n')
def lda(data,name:str):

    tf_ModelPath = os.path.join('usermodel/'+name+'/model', 'tfVector.model')  # 保存词频模型
    lda_ModelPath = os.path.join('usermodel/'+name+'/model', 'ldaModels.model')  # 保存训练的lda模型
    bestModelPath=os.path.join('usermodel/'+name+'/model', 'bestLDAModel.model')
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                               
                                )
    tf = tf_vectorizer.fit_transform(data)
    
    lda_models = []
    for idx, n_topic in enumerate(n_topics):
        lda = LatentDirichletAllocation(n_topics=n_topic,
                    max_iter=8000,
                    learning_method='batch',
                    evaluate_every=200,
                    perp_tol=0.01)
        t0 = time()
        lda.fit(tf)
        perplexityLst[idx] = lda.perplexity(tf)
        lda_models.append(lda)
    print("# of Topic: %d, " % n_topics[idx], end=' ')
    print("done in %0.3fs, N_iter %d, " % ((time() - t0), lda.n_iter_), end=' ')
    print("Perplexity Score %0.3f" % perplexityLst[idx])


    # 打印最佳模型
    best_index = perplexityLst.index(min(perplexityLst))
    best_n_topic = n_topics[best_index]
    best_model = lda_models[best_index]
    print("Best # of Topic: ", best_n_topic)
    print("Best Model: ")

    # 保存每个n_topics下的LDA模型，以便后续查看使用
    joblib.dump(tf_vectorizer, tf_ModelPath)
    joblib.dump(lda_models, lda_ModelPath)  
    joblib.dump(best_model, bestModelPath)  


    # 保存并输出topic_word矩阵
    print("#########Topic-Word Distribution#########")
    tf_vectorizer._validate_vocabulary()
    tf_feature_names = tf_vectorizer.get_feature_names()
    print_top_words(best_model, tf_feature_names, n_top_words,name)
    #print(docres)
    #joblib.dump(tf_vectorizer, tf_ModelPath)
    return best_model,tf_vectorizer
   



def getData(path:str):
    fr=open(path,'r')
    line=fr.readline()
    trainData=[]
    testData=[]
    i=1
    while line!=None and line!='':
        if i%5==0:
            testData.append(line)
        else:
            trainData.append(line)
        i+=1
        line=fr.readline()
    return trainData,testData

def trian(name:str):
    modelPath='usermodel/'+name+'/model'
    resPath='usermodel/'+name+'/result'
    if not os.path.exists(modelPath):
        os.makedirs(modelPath)
        os.makedirs(resPath)

    trainData,testData=getData('userData/'+name+'.txt')
    model,vec=lda(trainData,name)
    res=model.transform(vec.transform(testData))
    num=0
    length=len(res)
    for i in range(len(res)):
        for j in range(len(res[i])):
            if res[i][j]>0.6:
                num+=1
                break
    print(num/length)

trian('zhjghy')