
import subprocess
import Get_Data
subprocess.Popen("python3 Get_Data.py" , stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
tem = [[11111.11,21],[3,4],[5,6]]
lines = []
for i in tem:
    str1 = map(str,i)
    str2 = ','.join(str1)
    lines.append(str2)
    print(lines)

          
