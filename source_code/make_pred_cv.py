from glob import glob
from time import time
import requests
import os
import json

input_folder_path = "/home/charinpatel/raapid/workspace/python/PROJECT_DATA/health_care_nlp/INPUT"
output_folder_path = "/home/charinpatel/raapid/workspace/python/PROJECT_DATA/health_care_nlp/OUTPUT"

url = "http://127.0.0.1:5002/predict_cv_str"
# url = "https://intcorehcncvservice.healthcarenlp.com/predict_cv_str"

list_files_present = []#set([os.path.basename(x) for x in glob(output_folder_path+"*")])
start_time = time()
tik = time()
for i,file_path in enumerate(glob(input_folder_path+"/*")):
    if os.path.basename(file_path) not in list_files_present:

        with open(file_path) as fp:
            content = fp.read()#[:-1]

        d_content = {"content": content, "servicingFacility": "rumc",
                     "clientCode": "RAAPID", "projectId": "DEFAULT",
                     "dos": '2023-03-01 23:59:59', 'token': 'TEST',
                     'gender': 'M', 'dob': '1950-01-01 23:59:59',
                     "hcc_validate_codes": ["F1220", "E785", "Z7982", "Z7901", "H5789", "E6601", "Z9114", "I429",
                                            "G459",
                                            "F17200",
                                            "I5042", "I160", "N1830", "Z79899", "F1020", "I130", "Z6835", "D3500"]
                     }
        res = requests.post(url,
                            headers={'Content-type': 'application/json'},
                            data=json.dumps(d_content))
        print(res)
        with open(output_folder_path + "/" +os.path.basename(file_path)+".json","w") as fw:
            fw.write(json.dumps(res.json()["result"]))

        if i%10==0:
            tok = time()
            print(i, tok-tik, "secs to process filename", os.path.basename(file_path))
            tik = time()

end_time = time()

print(end_time-start_time, "secs to process total", len(glob(input_folder_path+"/*")))
