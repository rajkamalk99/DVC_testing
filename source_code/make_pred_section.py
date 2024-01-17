from glob import glob
from time import time
import requests
import os
import json

input_folder_path = "/home/charinpatel/raapid/workspace/python/PROJECT_DATA/health_care_nlp/INPUT"
output_folder_path = "/home/charinpatel/raapid/workspace/python/PROJECT_DATA/health_care_nlp/OUTPUT"
url = "http://127.0.0.1:5002/predict_section_str"

list_files_present = []#set([os.path.basename(x) for x in glob(output_folder_path+"*")])
start_time = time()
tik = time()
for i,file_path in enumerate(glob(input_folder_path+"/*")):
    if os.path.basename(file_path) not in list_files_present:
        print("-"*500)
        filename = os.path.basename(file_path)
        print(f"processing for {filename} started")
        with open(file_path) as fp:
            content = fp.read()#[:-1]

        # input_json = json.loads(content)
        # d = {"content":content, "servicingFacility" :"rumc"}
        d_content = {"content": content,
                     "clientCode": "RAAPID", "projectId": "DEFAULT",
                     "dos": '2023-03-01 00:00:00', 'token': filename,
                     'gender': 'M', 'dob': '1950-01-01 00:00:00',
                     "documentId": "TESTID", "documentName": "TEST"}
        # d_content = {"content": content, "servicingFacility": "KPMG",
        #              "clientId": "KPMG", "projectId": "test1",
        #              "documentId": "1292", "documentName": "INT_VB_2407_2_AD35173 - Test Bhuvan - request procedure with progress note 2.8.23 _214235_1690189586404",
        #              "dos": '2022-08-08'}
        #d = {"content":input_json["textSnippet"], "servicingFacility" :"rumc",
        #     "hcc_validate_codes":list(set(
        #         [x['value'].replace(".","") for x in input_json["codes"] if x['codingSystem']=="ICD10CM"])) + ["I10","I129"]}
        # print(d_content)
        res = requests.post(url,
                            headers= {'Content-type': 'application/json'},
                            data = json.dumps(d_content) )
        print(res)
        with open(output_folder_path + "/" +os.path.basename(file_path)+".json","w") as fw:
            fw.write(json.dumps(res.json()["result"]))

        if i%10==0:
            tok = time()
            print(i, tok-tik, "secs to process filename", os.path.basename(file_path))
            tik = time()
        # break
        #tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
        #print("Before starting: Total m/y:\t" + str(tot_m) + "\tUsed :\t" + str(used_m) + "\tFree:\t", str(free_m))
        #used_mmy_list.append(used_m)

end_time = time()

print(end_time-start_time, "secs to process total", len(glob(input_folder_path+"/*")))
