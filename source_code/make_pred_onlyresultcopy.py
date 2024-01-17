from glob import glob
from time import time
import requests
import os
import json

input_folder_path = "/home/rahulpatil/workspace/hcn_resource_validation/input"
output_folder_path = "/home/rahulpatil/workspace/hcn_resource_validation/output/"
tik = time()
used_mmy_list = []
start_time = time()
tik = time()

import os, sys
import hashlib

# get env hash]
list_all_paths = []
for root, dirs, files in os.walk(input_folder_path+"/"):
    for file in files:
        list_all_paths.append(os.path.join(root,file))
#print(list_all_paths)
            
            
for i,file_path in enumerate(list_all_paths):

    with open(file_path) as fp:
        content = fp.read()[:-1]

    d = {"content":content, "servicingFacility" :"rumc"}
    
    res = requests.post("http://127.0.0.1:5002/run_hcn" ,headers= {'Content-type': 'application/json'}, data = json.dumps(d) )
    with open(output_folder_path + "/" + os.path.basename(file_path),"w") as fw:
        fw.write(json.dumps(res.json()["result"]))
    
    if i%10==0:
    	tok = time()
    	print(i,tok-tik, "secs to process filename", os.path.basename(file_path))
    	tik = time()
    #tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    #print("Before starting: Total m/y:\t" + str(tot_m) + "\tUsed :\t" + str(used_m) + "\tFree:\t", str(free_m))
    #used_mmy_list.append(used_m)

end_time = time()

print(end_time-start_time, "secs to process filename", len(glob(input_folder_path+"/*")))


