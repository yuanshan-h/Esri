#导入需要的库，模块报错在setting里install一般能解决
import requests
import json
from bs4 import BeautifulSoup
url = "https://chongqing.8684.cn/list1"  # 今天就只先演示获取一种线路类型下所有公交的信息，要想拿到整个城市的，其实就加个for循环:line1,line2,line3......
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
    print(line)