import GetLineCoord as glc
def main():
    linelist = []
    linelist = input("请输入你想查询的公交信息的开头数字或者开头大写首字母或者详细名称：").split()
    glc.getbusdata(linelist)    

if __name__ == '__main__':
    main()
