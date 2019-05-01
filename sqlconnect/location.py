
import json
import urllib.request

#基于百度地图API下的经纬度信息来解析地理位置信息
def getlocation(lat,lng):
    #31.809928, 102.537467, 3019.300   36.859295, 99.226527
    #lat = '36.859295'
    #lng = '99.226527'
    #rP4PGHFg6gA5E31GTDP4eGZnUCq7zXfs    lyw
    #8PdKyQYB4QCvVj3vCwnCzIvlfPVL8zGm    lrf

    url = 'http://api.map.baidu.com/geocoder/v2/?location=' + str(lat) + ',' + str(lng) + '&output=json&pois=1&ak=rP4PGHFg6gA5E31GTDP4eGZnUCq7zXfs'
    req=None
    res="{}"
    try:
        req = urllib.request.urlopen(url)  # json格式的返回数据
        res = req.read().decode("utf-8")  # 将其他编码的字符串解码成unicode
    except Exception:
        print("发送请求失败")

    
    return json.loads(res)

#json序列化解析数据(lat:纬度，lng:经度)
def jsonFormatLocation(lat,lng):
    str = getlocation(lat,lng)
    if str=={}:
        return {}
    dictjson={}#声明一个字典
    #get()获取json里面的数据
    jsonResult = str.get('result')
    address = jsonResult.get('addressComponent')
    #国家
    country = address.get('country')
    #国家编号（0：中国）
    country_code = address.get('country_code')
    #省
    province = address.get('province')
    #城市
    city = address.get('city')
    #城市等级
    city_level = address.get('city_level')
    #县级
    district = address.get('district')
    #把获取到的值，添加到字典里（添加）
    dictjson['country']=country
    dictjson['country_code'] = country_code
    dictjson['province'] = province
    dictjson['city'] = city
    dictjson['city_level'] = city_level
    dictjson['district']=district
    return dictjson

def geoLocation(lat,lng):
    from geopy.geocoders import Nominatim
    import time
    geolocator = Nominatim()
    location=None
    for i in range(3):
        try:
            location = geolocator.reverse(str(lat)+','+str(lng),timeout=10)
            break
        except(GeocoderTimedOut, GeocoderServiceError):
            print('超时')
            time.sleep(1.25)
    if location==None:
        return {}
    address=location.raw['address']
    dictjson={}
    dictjson['country']=address['country']
    
    dictjson['province'] = address['state']
    if 'city' in address.keys():
        dictjson['city'] = address['city']
    else:
        dictjson['city'] = address['region']
    
    dictjson['district']=address['county']
    return dictjson
#if __name__ == '__main__':
    #print(jsonFormat('',''))
