import requests
import json
import pandas as pd
import shapefile
import math
import numpy as np
import CoordTransform as transform
import GetLineNumber as gln

def getbusdata(linelist):
    count = 0
    w=shapefile.Writer('公交路线轨迹.shp',encoding='utf-8-sig')
    w.field('name', 'C')
    wp=shapefile.Writer('公交站点.shp',encoding='utf-8-sig')
    wp.field('name','C')

    errorlist = [] #记录爬取过程中高德未记载的线路
    errordict = {} #记录爬取过程中高德未记载的线路
    #0、在这里设置城市和线路名！(应确保有这条线路) 
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }
    cityname='重庆'
    for i in gln.lines_data(linelist):  
        url = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&extensions=all&key=a5b7479db5b24fd68cedcf24f482c156&output=json&city={}&offset=1&keywords={}&platform=JS'.format(
            cityname, i)
        # 1、获取数据
        r = requests.get(url, headers).text
        rt = json.loads(r)
        # 2、读取公交线路部分信息（可参考rt变量中的内容，按需获取）
        dt = {}
        try:  # 该公交路线在高德地图可能不存在
            dt['line_name'] = rt['buslines'][0]['name']  # 公交线路名字
        except:
            errorlist.append(i)
            print(errorlist)
            errordict['未找到的路线'] = i
            ed = pd.DataFrame(errordict, index=[++count])
            ed.to_csv('表格未找的的公交路线.csv', header=False,
                        mode='a', encoding='utf-8-sig')
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
        station_coords_t = transform.lines_wgs84(station_coords)
        lines = []
        for j in station_coords_t:
            str1 = map(str, j)
            str2 = ','.join(str1)
            lines.append(str2)
        dt['station_coords'] = lines
        tr = pd.DataFrame(dt)
        tr['latitude'], tr['longitude'] = tr['station_coords'].str.split(
                ',', 1).str
        tr.to_csv('表格1公交基本信息T.csv', header=False,
                    mode='a', encoding='utf-8-sig')

        # 公交站点数据生成点要素矢量文件
        for k in range(len(station_name)):
            wp.point(station_coords_t[k][0], station_coords_t[k][1])  # 生成点要素
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
            test = transform.lines_wgs84(polylines)  # 经纬度转换为wgs84坐标系
        w.line([test])  # 生成线要素
        w.record(name=i)
    w.close()
    wp.close()
