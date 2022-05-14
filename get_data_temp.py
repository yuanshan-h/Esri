from asyncio.windows_events import NULL
import requests
import json
import pandas as pd
import shapefile
import math
import numpy as np
import json
from bs4 import BeautifulSoup
# 坐标转化函数
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
count = 0

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


def lines_wgs84(x):  # 格式转换
    lst = []
    for i in x:
        lng = float(i.split(',')[0])
        lat = float(i.split(',')[1])
        lst.append(gcj02_to_wgs84(lng, lat))
    return lst

# 生成矢量文件 
w = shapefile.Writer('公交路线轨迹.shp', encoding='utf-8-sig')
w.field('name', 'C')
wp = shapefile.Writer('公交站点.shp', encoding='utf-8-sig')
wp.field('name', 'C')

errorlist = [] #记录爬取过程中高德未记载的线路
errordict = {} #记录爬取过程中高德未记载的线路
# headers = {
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
# }
# 0、在这里设置城市和线路名！(应确保有这条线路)
cityname = '重庆'

listline=[1,2,3,4,5,6,7,8,9,'B','C','D','G','L','N','Q','S','T','X','Y']
for ie in listline:
    url = "https://chongqing.8684.cn/list{}".format(ie)  # 今天就只先演示获取一种线路类型下所有公交的信息，要想拿到整个城市的，其实就加个for循环:line1,line2,line3......
    # 伪装请求头
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }
    # 通过requests模块模拟get请求
    res = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    div = soup.find('div', class_='list clearfix')
    lists = div.find_all('a')
    line_all = []
    for item in lists:
        # print(item.string) # item.string与item.text效果一样
        line_one = item.text  #获取a标签下的公交线路
        line_all.append(line_one)

    for i in line_all:
        url1 = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&extensions=all&key=a5b7479db5b24fd68cedcf24f482c156&output=json&city={}&offset=1&keywords={}&platform=JS'.format(
            cityname, i)
        # 1、获取数据
        r = requests.get(url1, headers).text
        rt = json.loads(r)
        # 2、读取公交线路部分信息（可参考rt变量中的内容，按需获取）
        dt = {}
        try:  #该公交路线在高德地图可能不存在
            dt['line_name'] = rt['buslines'][0]['name']  # 公交线路名字
        except:
            errorlist.append(i)
            print(errorlist)
            errordict['未找到的路线'] = i
            ed = pd.DataFrame(errordict,index=[count+1])
            ed.to_csv('表格未找的的公交路线.csv',header=False, mode='a', encoding='utf-8-sig')
            continue
        dt['start_stop'] = rt['buslines'][0]['start_stop']  # 始发站

        dt['end_stop'] = rt['buslines'][0]['end_stop']  # 终点站
        # 3、获取沿途站点站名和对应坐标并保存在“公交基本信息”表格中
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
        # dm.to_csv('表格11公交基本信息.csv',header=False, mode='a', encoding='utf-8-sig')

        # 坐标转换 生成CSV文件
        station_coords_t = lines_wgs84(station_coords)
        lines = []
        for j in station_coords_t:
            str1 = map(str, j)
            str2 = ','.join(str1)
            lines.append(str2)
        dt['station_coords']=lines
        tr = pd.DataFrame(dt)
        tr['latitude'], tr['longitude'] = tr['station_coords'].str.split(',', 1).str
        tr.to_csv('表格1公交基本信息T.csv', header=False, mode='a', encoding='utf-8-sig')

        # 公交站点数据生成点要素矢量文件
        for k in range(len(station_name)):
            wp.point(station_coords_t[k][0],station_coords_t[k][1])  # 生成点要素
            wp.record(name=station_name[k])


        # 4、获取沿途路径坐标（行驶轨迹）
        polyline = rt['buslines'][0]['polyline']
        # 生成csv表格文件
        # tmp={}
        # tmp['station_coords']=polyline.split(";")
        # path=pd.DataFrame(tmp)
        # path['latitude'], path['longitude'] = path['station_coords'].str.split(',', 1).str#将坐标拆解为经度和纬度
        # path.to_csv('表格2_{}{}公交路线轨迹.csv'.format(cityname,line),encoding='utf-8-sig')

        # 公交轨迹数据生成线要素矢量文件
        polylines = []
        for h in polyline.split(";"):
            polylines.append(h)
        test = lines_wgs84(polylines)  # 经纬度转换为wgs84坐标系
        w.line([test])  # 生成线要素
        w.record(name=i) 
w.close()
wp.close()
