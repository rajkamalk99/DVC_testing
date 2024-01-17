from glob import glob
from time import time
import requests
import os
import json

input_folder_path = "/home/rahulp/PycharmProjects/test3/text"
output_folder_path = "/home/rahulp/PycharmProjects/test3/res"
tik = time()
used_mmy_list = []
start_time = time()
for i,file_path in enumerate(glob(input_folder_path+"/*")):

    with open(file_path) as fp:
        content = fp.read()

    d = {"content":content, "servicingFacility" :"Reveleer"}
    tik = time()
    res = requests.post("http://127.0.0.1:5002/run_hcn" ,headers= {'Content-type': 'application/json'}, data = json.dumps(d) )
    with open(output_folder_path + "/" +os.path.basename(file_path),"w") as fw:
        fw.write(json.dumps(res.json()))
    tok = time()
    print(tok-tik, "secs to process filename", os.path.basename(file_path))
    tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    print("Before starting: Total m/y:\t" + str(tot_m) + "\tUsed :\t" + str(used_m) + "\tFree:\t", str(free_m))
    used_mmy_list.append(used_m)

end_time = time()

print(end_time-start_time, "secs to process filename", len(glob(input_folder_path+"/*")))


