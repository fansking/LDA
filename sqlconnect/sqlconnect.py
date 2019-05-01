from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import text

import numpy as np
import location
import os
#连接到数据库并把操作数据化
def getSession():
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/user_profile_data')
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    return sessionmaker(bind=engine)()
#获取所有用户，三元组列表，依次是是工作单位，用户名称，下载条数
def getUsers(session:sessionmaker)->list:
    sql="select af_user.TNAME,cds.YHMC,count(ds.ID) record_count from (ds_product_imagery ds join cdsjdd_yxsj_sj cd on ds.ID = cd.SJBH join cdsjdd_yxsj cds on cd.DDBH = cds.DDBH join af_user on cds.YHMC = af_user.USERNAME) group by cds.YHMC order by record_count DESC;"
    resultproxy = session.execute(text(sql))
    results = resultproxy.fetchall()
    return results
#获取指定用户的数据信息。顺序为：
#0:工作单位，1:用户名称，2:卫星编号，3:传感器编号，4:产品级别
#5:云量，6:产品类型
#7:左上纬度，8:左上经度
#9:右上纬度，10:右上经度
#11:右下纬度，12:右下经度
#13:左下纬度，14:左下经度
#15:中心经度 16:中心纬度
#如果把经纬度在二维平面内显示，经度应对应x，纬度对应y
def getUserData(session:sessionmaker,name:str):
    sql="select af_user.TNAME,cds.YHMC,ds.SATELLITEID,ds.SENSORID,ds.PRODUCTLEVEL,ds.CLOUDPERCENT,ds.PRODUCTTYPE,ds.TLLATITUDE,ds.TLLONGITUDE,ds.TRLATITUDE,ds.TRLONGITUDE,ds.BRLATITUDE,ds.BRLONGITUDE,ds.BLLATITUDE,ds.BLLONGITUDE,ds.CENTERLONGITUDE,ds.CENTERLATITUDE from (ds_product_imagery ds inner join cdsjdd_yxsj_sj cd on ds.ID = cd.SJBH inner join cdsjdd_yxsj cds on cd.DDBH = cds.DDBH inner join af_user on cds.YHMC = af_user.USERNAME) where cds.YHMC like :YHMC;"
    resultproxy = session.execute(text(sql).bindparams(YHMC=name))
    results = resultproxy.fetchall()
    resMat=np.mat(results)
    return resMat

#处理getUserData得到的数据，并返回分隔开的内容
def dataProcess(data:np.matrix):
    SATELLITEID=np.tile(data[:,2],1).astype(str)
    SENSORID=np.tile(data[:,3],1).astype(str)
    PRODUCTLEVEL=np.tile(data[:,4],1).astype(str)
    CLOUDPERCENT=np.tile(data[:,5],1).astype(str)
    PRODUCTTYPE=np.tile(data[:,6],1).astype(str)
    NS=np.tile(data[:,7:],1).astype(float)#0-7分别为上个函数的注释的7-14内容
    x=NS[:,[1,3,5,7]]#所有经度
    y=NS[:,[0,2,4,6]]#所有纬度
    lat_cen=NS[:,9]#中心纬度
    lng_cen=NS[:,8]#中心经度
    x_min=np.min(x)
    x_max=np.max(x)
    y_min=np.min(y)
    y_max=np.max(y)
    X=[x_min,x_max,x_min,x_max]#得到的四个边界值，分别对应点为左上，右上，左下，右下
    Y=[y_max,y_max,y_min,y_min]
    return SATELLITEID,SENSORID,PRODUCTLEVEL,CLOUDPERCENT,PRODUCTTYPE,NS,X,Y,lat_cen,lng_cen



res=getUserData(getSession(),'zhjghy')
SATELLITEID,SENSORID,PRODUCTLEVEL,CLOUDPERCENT,PRODUCTTYPE,NS,X,Y,lat_cen,lng_cen=dataProcess(res)
#d={}
#for i in range(len(res))
if not os.path.exists('userData'):
    os.makedirs('userData')
fw=open('userData/zhjghy.txt','w')

for i in range(len(lat_cen)):
    fw.write(str(SATELLITEID[i,0])+' ')
    fw.write(str(SENSORID[i,0])+' ')
    fw.write(str(SATELLITEID[i,0])+' ')
    fw.write(str(PRODUCTLEVEL[i,0])+' ')
    fw.write(str(CLOUDPERCENT[i,0])+' ')
    fw.write(str(PRODUCTTYPE[i,0])+' ')
    if int(lat_cen[i,0])==0 or int(lng_cen[i,0])==0:
        lng_cen[i,0]=(NS[i,1]+NS[i,3]+NS[i,5]+NS[i,7])/4
        lat_cen[i,0]=(NS[i,2]+NS[i,4]+NS[i,6]+NS[i,0])/4
    try:
        lo=location.jsonFormatLocation(lat_cen[i,0],lng_cen[i,0])
        if lo=={}:
            #l.append(' ')
            fw.write('\n')
            continue
        else:
            #l.append(str(lo['province'])+' '+str(lo['city'])+' '+str(lo['district']))
            fw.write(' '+str(lo['province'])+' '+str(lo['city'])+' '+str(lo['district']))
            fw.write('\n')
        #if lo['province'] not in d.keys():
        #    d[lo['province']]=1
        #else:
        #    d[lo['province']]+=1
        #if lo['city'] not in d.keys():
        #    d[lo['city']]=1
        #else:
        #    d[lo['city']]+=1
        #if lo['district'] not in d.keys():
        #    d[lo['district']]=1
        #else:
        #    d[lo['district']]+=1
    except Exception:
        print('解析错误')
        fw.write('\n')
fw.close()


#print(d)
#fw=open("xjghy.txt",'w')
#fw.write(str(d))
#fw.write('\n')
#fw.write(str(l))
#fw.close()

#SATELLITEID,SENSORID,PRODUCTLEVEL,CLOUDPERCENT,PRODUCTTYPE,NS,X,Y=dataProcess(res)

#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.decomposition import LatentDirichletAllocation


#X=np.array([res[0,8],res[0,10],res[0,12],res[0,14]]).astype(float)
#Y=np.array([res[0,7],res[0,9],res[0,11],res[0,13]]).astype(float)
#txt = ['左上','右上','右下','左下']
#plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
#plt.scatter(X, Y)
#for i in range(len(X)):
#    plt.annotate(txt[i], xy = (X[i], Y[i]), xytext = (X[i]+0.01, Y[i]+0.01))
#plt.show()
#print(getUsers(getSession())[0])
#getUserData(getSession(),'zhjghy')
#Student = Base.classes.ds_product_imagery_dzz
#ret = db.query(Student).first()
#mydict = ret.__dict__
#print(mydict['FGEOMETRY'])
