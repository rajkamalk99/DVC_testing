from glob import glob
from time import time
import requests
import os
import json

input_folder_path = "/home/rahulp/workspace/repo/inp_out/meat_inp/"
inter_folder_path = "/home/rahulp/workspace/repo/inp_out/meat_inter/"
output_folder_path = "/home/rahulp/workspace/repo/inp_out/meat_out/"


def create_server_input(input_json):
    servicingFacility = 'RUMC'
    status = 'COMPLETED'
    token = 'c501ddb7-5232-471a-b4b3-b5ab01aa6a74'
    if 'result' in input_json:
        input_json = input_json['result']
    meat_input_dict = {'content': input_json['content'],
                       "servicingFacility": servicingFacility,
                       "status": status,
                       "token": token,
                       "codes": []}
    icd10cmcodes_list = input_json['icd10cmcodes']
    for code_dict in icd10cmcodes_list:
        temp_dict = dict()
        temp_dict['value'] = code_dict['codes'][0]['code']
        temp_dict['codingSystem'] = 'ICD10'
        temp_dict['evidence'] = [{"textSpan": {'text': phrase['text'], 'beginOffset': phrase['begin']},
                                  "certainty": phrase['certainty'],
                                  "status": phrase['status'],
                                  "section": {"text": phrase['section']['text'],
                                              'beginOffset': phrase['section']['begin']}}
                                 for phrase in code_dict['phrases']]
        meat_input_dict['codes'].append(temp_dict)
    return meat_input_dict


start_time = time()
tik = time()
for i, file_path in enumerate(glob(input_folder_path + "/*")):
    print((file_path))
    with open(file_path) as fp:
        d = json.load(fp)  # [:-1]
        d = create_server_input(d)
    # d = {"content":content, "servicingFacility" :"rumc"}
    with open(inter_folder_path + os.path.basename(file_path),"w") as fw:
        fw.write(str(d))

    with open(inter_folder_path + os.path.basename(file_path).replace(".json",".txt"),"w") as fw:
        fw.write(d['content'])

    # print({"servicingFacility": d['servicingFacility'],
    #                           "status": d['status'],
    #                           "token": d['token'],
    #                           "codes": d["codes"]})
    # print(inter_folder_path + os.path.basename(file_path).replace(".json",".txt"))
    # files = {"content": open(inter_folder_path + os.path.basename(file_path).replace(".json",".txt"), "rb")}
    text_path = inter_folder_path + os.path.basename(file_path).replace(".json",".txt")
    file_dict = {"content": open(text_path, "rb"),

                 }
    data_dict = {"servicingFacility": d['servicingFacility'],
                 "status": d['status'],
                 "token": d['token'],
                 "codes": json.dumps(d["codes"])}
    # print(file_dict)
    res = requests.post("http://0.0.0.0:5002/predict_meat",
                        files = file_dict, data =data_dict)
    print(res)
    with open(output_folder_path + "/" + os.path.basename(file_path), "w") as fw:
        fw.write(json.dumps(res.json()))

    if i % 10 == 0:
        tok = time()
        print(i, tok - tik, "secs to process filename", os.path.basename(file_path))
        tik = time()
    # tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    # print("Before starting: Total m/y:\t" + str(tot_m) + "\tUsed :\t" + str(used_m) + "\tFree:\t", str(free_m))
    # used_mmy_list.append(used_m)

end_time = time()

print(end_time - start_time, "secs to process filename", len(glob(input_folder_path + "/*")))
