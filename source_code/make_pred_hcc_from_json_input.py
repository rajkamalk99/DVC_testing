from glob import glob
from time import time
import requests
import os
import json
import numpy as np
import pandas as pd

input_folder_path = "/home/rajkamalkareddula/Documents/RAAPID/clients/century/improvement_over_50_docs/re-parsing/round_3/inputs"
output_folder_path = "/home/rajkamalkareddula/Documents/RAAPID/clients/century/improvement_over_50_docs/re-parsing/round_3/outputs"


mapping_path= "/home/rajkamalkareddula/Documents/RAAPID/clients/century/improvement_over_50_docs/re-parsing/round_3/reparse_mapping.csv"

mapping= pd.read_csv(mapping_path)

url = "http://127.0.0.1:5002/predict_hcc_str"


def date_corrector(date):
    if date is np.nan:
        return ""
    splits= date.split("/")
    return f"{splits[-1]}-{splits[0]}-{splits[1]} 23:59:59"

list_files_present = []#set([os.path.basename(x) for x in glob(output_folder_path+"*")])
start_time = time()
tik = time()
for i,file_path in enumerate(glob(input_folder_path+"/*")):
    if os.path.basename(file_path) not in list_files_present:
        filename = os.path.basename(file_path)
        print(f"processing for {filename} started")
        with open(file_path) as fp:
            content = fp.read()#[:-1]

        file_attributes= mapping[mapping["filename"] == filename]

        if len(file_attributes) == 0:
            print("********** something wrong*********")
            print(f"Found no attributes for {filename}")
            continue

        DOS= date_corrector(file_attributes["dos"].tolist()[0])
        content= content
        DOB= date_corrector(file_attributes["dob"].tolist()[0])
        Gender= file_attributes["gender"].tolist()[0]

        d_content = {"content": content,
                     "clientCode": "CENTAURI", "projectId": "DEFAULT",
                     "dos": DOS, 'token': filename,
                     'gender': Gender, 'dob': DOB}
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