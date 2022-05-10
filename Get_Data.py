import requests
import json
from bs4 import BeautifulSoup
#定义一个函数，传入线路名称相当于在高德地图搜索，来获取每趟公交的站点名称和经纬度
def get_location(line):
    url_api = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&extensions=all&key=559bdffe35eec8c8f4dae959451d705c&output=json&city=武汉&offset=2&keywords={}&platform=JS'.format(
        line)
    res = requests.get(url_api).text
    # print(res) 可以用于检验传回的信息里面是否有自己需要的数据
    rt = json.loads(res)
    #print(rt)
    #print(rt['buslines'])
    i = 0
    line_name = rt['buslines'][0]['name']
    polyline = rt['buslines'][0]['polyline']
    info = [line_name, polyline]
    print(info)
    stop = rt['buslines'][0]['busstops']
    for i in range(len(stop)):
        station = stop[i]['name']
        location = stop[i]['location']
        info_ = [line, station, location]
        print(info_)
        i += 1
 
url = "https://wuhan.8684.cn/line3"  # 今天就只先演示获取一种线路类型下所有公交的信息，要想拿到整个城市的，其实就加个for循环:line1,line2,line3......
# 伪装请求头
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}
# 通过requests模块模拟get请求
res = requests.get(url=url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")
div = soup.find('div', class_='list clearfix')
lists = div.find_all('a')
for item in lists:
    line = item.text  #获取a标签下的公交线路
    get_location(line)
 
 
 