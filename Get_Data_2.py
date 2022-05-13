import requests
import json
import pandas as pd
import shapefile
import math
import numpy as np
#坐标转化函数
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]
def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret
def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret
def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)
def lines_wgs84(x):#格式转换
    lst = []
    for i in x:
        lng = float(i.split(',')[0])
        lat = float(i.split(',')[1])
        lst.append(gcj02_to_wgs84(lng,lat))
    return lst
w=shapefile.Writer('公交路线轨迹.shp',encoding='utf-8-sig')
w.field('name', 'C')
wp=shapefile.Writer('公交站点.shp',encoding='utf-8-sig')
wp.field('name','C')
#0、在这里设置城市和线路名！(应确保有这条线路) 
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}
cityname='重庆'
for i in [347,346]:
    line='{}路'.format(i) 
    url = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&extensions=all&key=a5b7479db5b24fd68cedcf24f482c156&output=json&city={}&offset=1&keywords={}&platform=JS'.format(cityname,line)
    #1、获取数据 
    r = requests.get(url,headers).text 
    rt = json.loads(r)
    #2、读取公交线路部分信息（可参考rt变量中的内容，按需获取） 
    dt = {} 
    dt['line_name'] = rt['buslines'][0]['name'] #公交线路名字 

    dt['start_stop'] = rt['buslines'][0]['start_stop'] #始发站 

    dt['end_stop'] = rt['buslines'][0]['end_stop'] #终点站 
    #3、获取沿途站点站名和对应坐标并保存在“公交基本信息”表格中 
    station_name = [] 
    station_coords = [] 
    for st in rt['buslines'][0]['busstops']: 
        station_name.append(st['name']) 
        station_coords.append(st['location'])
        
    dt['station_name'] = station_name 
    dt['station_coords'] = station_coords 

    # 火星坐标系的csv文件
    # print(station_coords)
    # dm = pd.DataFrame(dt) 
    # print(dt)
    # dm['latitude'], dm['longitude'] = dm['station_coords'].str.split(',', 1).str#将坐标拆解为经度和纬度 
    # dm.to_csv('表格1_{}{}公交基本信息.csv'.format(cityname,line),encoding='utf-8-sig')

    # 坐标转换
    station_coords_t = lines_wgs84(station_coords)
    lines = []
    print(station_coords)
    for i in station_coords_t:
        str1 = map(str,i)
        str2 = ','.join(str1)
        lines.append(str2)
        # print(lines)
    dt['station_coords']=lines
    tr = pd.DataFrame(dt)
    tr['latitude'], tr['longitude'] = tr['station_coords'].str.split(',', 1).str
    # tr.to_csv('表格1_{}{}公交基本信息T.csv'.format(cityname,line),encoding='utf-8-sig')
    tr.to_csv('表格1公交基本信息T.csv',header=False,mode='a',encoding='utf-8-sig')
    for i in range(len(station_coords_t)):
        wp.point([i])  #生成线要素
        wp.record(name=i)
    #4、获取沿途路径坐标（行驶轨迹）并保存在“公交路线轨迹表格中” 
    polyline=rt['buslines'][0]['polyline'] 

    polylines = []
    for i in polyline.split(";"):
        polylines.append(i)

    # 生成csv表格文件
    # tmp={} 
    # tmp['station_coords']=polyline.split(";")         
    # path=pd.DataFrame(tmp) 
    # path['latitude'], path['longitude'] = path['station_coords'].str.split(',', 1).str#将坐标拆解为经度和纬度 
    # path.to_csv('表格2_{}{}公交路线轨迹.csv'.format(cityname,line),encoding='utf-8-sig')

    test = lines_wgs84(polylines)#经纬度转换为wgs84坐标系
    w.line([test])  #生成线要素
    w.record(name=line)        
w.close()
wp.close()