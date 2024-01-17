import datetime
from time import time
import json
from jsonschema import validate
import traceback

from flask import Flask, request, jsonify
from fastapi.responses import JSONResponse, PlainTextResponse

app = Flask(__name__)
from waitress import serve

# import nltk
#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt')

from org.hcn.utils.env_var_setter import set_os_env_var
import org.hcn.utils.env_var_setter
from org.hcn.utils import HcnConstants
from org.hcn.utils.log_utils import HcnLogUtils, AppFilter
import os
HcnLogUtils.lgr.info( f" Enviroment info-{str(os.environ).replace(':','=')}".replace("'",'"'))
HcnLogUtils.lgr.info( f"Server Info - {os.popen('/sbin/ifconfig').read().replace(':','-')}".replace('\n',' ').replace("'",'"'))

from org.hcn.core.CDoc import CDoc
from org.hcn.core.Req_Data import Req_Data

from org.hcn.annotators.SegmentDetection import Segment_Detector
from org.hcn.annotators.SectionDetection import Section_Detector
from org.hcn.annotators.TokenDetection import Token_Detector
from org.hcn.annotators.SentenceDetection import Sentence_Detector
# from org.hcn.annotators.ChunkAndPosDetection import ChunkAndPosDetector
# from org.hcn.annotators.ChunkCorrection import ChunkCorrection
from org.hcn.annotators.EntityDetectionNER2 import Entity_DetectorNER2
from org.hcn.annotators.RelationExtractionNER import Relation_ExtractorNER
from org.hcn.annotators.NegationDetection import Negation_Detector
from org.hcn.annotators.StatusDetection import StatusDetector
from org.hcn.annotators.CuiLookUp import CuiLookUp
from org.hcn.annotators.LabDetection_nondl import Lab_Detector
from org.hcn.annotators.MeasDetection_nondl import Meas_Detector
from org.hcn.annotators.DrugDetection_nondl import Drug_Detector

from org.hcn.annotators.LabAttributeRuleBased import Lab_Detector_Rule

# from org.hcn.utils.db_utils import HcnDbUtils
from org.hcn.JsonConverter import convertToJSON
# hcn_db_utils = HcnDbUtils()
# from org.hcn.utils.result_validation import validate_result_json

segment_obj = Segment_Detector()
section_obj = Section_Detector()
token_obj = Token_Detector()
sentence_obj = Sentence_Detector()
# chunk_obj = ChunkAndPosDetector()
# chunk_correction_obj = ChunkCorrection()
entity_obj = Entity_DetectorNER2()
rel_obj = Relation_ExtractorNER()
negation_obj = Negation_Detector()
status_obj = StatusDetector()
cuiLook_obj = CuiLookUp(HcnConstants.CUI_LOOKUP_DB_PATH)
lab_attr_obj_nondl = Lab_Detector()
meas_attr_obj_nondl = Meas_Detector()
drug_attr_obj_nondl = Drug_Detector()

lab_attr_obj_rule = Lab_Detector_Rule()

with open(HcnConstants.JSON_SCHEMA_RESULT_PATH, 'r') as file:
    result_schema = json.load(file)
with open(HcnConstants.JSON_SCHEMA_INPUT_PATH, 'r') as file:
    input_schema = json.load(file)


def run(raw_text, task):
    # Later raw_text will setted by setter method of cdoc class
    cdoc = CDoc(raw_text)

    cdoc = segment_obj.process(cdoc)
    if task == "SEGMENT_DETECTION":
        return cdoc

    cdoc = section_obj.process(cdoc)
    if task == "SECTION_DETECTION":
        return cdoc
        
    cdoc = sentence_obj.process(cdoc)
    if task == "SENTENCE_DETECTION":
        return cdoc

    cdoc = token_obj.process(cdoc)
    if task == "TOKEN_DETECTION":
        return cdoc

    # cdoc = chunk_obj.process(cdoc)
    # if task == "CHUNK_AND_POS_DETECTION":
    #     return cdoc
    #
    # cdoc = chunk_correction_obj.process(cdoc)
    # if task == "CHUNK_CORRECTION":
    #     return cdoc

    cdoc = entity_obj.process(cdoc)
    if task == "ENTITY_DETECTION":
        return cdoc

    cdoc = rel_obj.process(cdoc)
    if task == "RELATION_EXTRACTION":
        return cdoc

    cdoc = negation_obj.process(cdoc)
    if task == "NEGATION_DETECTION":
        return cdoc

    cdoc = status_obj.process(cdoc)
    if task == "STATUS_DETECTION":
        return cdoc

    cdoc = cuiLook_obj.process(cdoc)
    if task == "CUI_LOOKUP":
        return cdoc

    #cdoc = lab_attr_obj_rule.process(cdoc)
    cdoc = lab_attr_obj_nondl.process(cdoc)

    #cdoc = lab_attr_obj_rule.process(cdoc)
    cdoc = lab_attr_obj_nondl.process(cdoc)
    # cdoc = lab_attr_obj_dl.process(cdoc)
    if task == "LAD":
        return cdoc

    cdoc = meas_attr_obj_nondl.process(cdoc)
    if task == "MAD":
        return cdoc

    cdoc = drug_attr_obj_nondl.process(cdoc)
    # cdoc = drug_attr_obj_dl.process(cdoc)
    if task == "DAD":
        return cdoc

    return cdoc

@app.route('/', methods=['GET'])
def index_route():
    return jsonify({'message': 'Index Route'})

@app.route('/health', methods=['GET'])
def health():
    return "200"


@app.route('/predict_ner', methods=['GET', 'POST'])
def predict():
    try:
        # d_content = request.get_json()
        start = time()
        text = str(request.files['content'].stream.read())[:25000]
        facility = str(request.form['servicingFacility'])
        d_content = {"content": text, "servicingFacility": facility}

        validate(instance=d_content, schema=input_schema)
        req_obj = Req_Data(d_content)
        cdoc_obj = run(req_obj, "ENTITY_DETECTION")
        cdoc_json = convertToJSON(cdoc_obj)
        result_response = {"status": "SUCCESS", "result": cdoc_json, "errorMessage": None}
        #print("Token list: ", token_list)
        #validate_result_json(result_response,result_schema)
        HcnLogUtils.lgr.info(" Total characters in document = "+str(len(text))+' run_ner2 pipeline takes= ' + str(time() - start))
        #return jsonify(result_response)
        return result_response
    except Exception as e:
        HcnLogUtils.lgr.error('========= ERROR START===========')
        HcnLogUtils.lgr.error('GOT request.get_json()='+str(request.get_json()).replace(':','-').replace('"',"'"))
        # HcnLogUtils.lgr.error(str(e).replace(':','-').replace('"',"'"), exc_info=True)
        err = json.dumps(traceback.format_exc())
        HcnLogUtils.lgr.error(f"{err.replace(':', '-')}".replace('"', ""))
        HcnLogUtils.lgr.error('========= ERROR  END ===========')
        result_response = {"status": "FAIL", "result": None, "errorMessage": "tmp default error msg "}
        #return jsonify(result_response)
        return result_response


#@app.route('/predict_ner_str', methods=['GET', 'POST'])
def predict_str(request_json):
    try:
        start = time()
        #request_json = request.get_json()

        text = str(request_json['content'])
        clientId = "RAAPID"
        projectId = "DEFAULT"
        dos_tmp = "1970-01-01 00:00:00"
        dos_date_obj = datetime.datetime.strptime(dos_tmp, '%Y-%m-%d %H:%M:%S').date() if len(dos_tmp) > 0 else None
        gender_tmp = "M"
        gender = gender_tmp if len(gender_tmp) > 0 else "NA"
        token = "TEST"
        client_project_token = f"{clientId}_{projectId}_{token}"
        HcnLogUtils.lgr.addFilter(AppFilter(client_project_token, 'py_ner2'))  # set token_od,project_id,client_id in log
        dob_tmp = "1970-01-01 00:00:00"
        dob_date_obj = datetime.datetime.strptime(dob_tmp, '%Y-%m-%d %H:%M:%S').date() if len(dob_tmp) > 0 else None
        HcnLogUtils.lgr.info(
            f"'servicingFacility'= '{clientId}', 'dos'= '{dos_date_obj}', 'dob'= '{dob_date_obj}','gender'='{gender}','token'='{token}'")
        d_content = {"content": text, "servicingFacility": clientId, "dos": dos_date_obj, "dob": dob_date_obj,
                 "gender": gender, "token": token, "clientId":clientId, "projectId":projectId}
        validate(instance=d_content, schema=input_schema)
        req_obj = Req_Data(d_content)
        cdoc_obj = run(req_obj, "STATUS_DETECTION")
        cdoc_json = convertToJSON(cdoc_obj)
        result_response = {"status": "SUCCESS", "result": cdoc_json, "errorMessage": None}
        #validate_result_json(result_response,result_schema)
        HcnLogUtils.lgr.info('run_ner2 pipeline takes=' + str(time() - start))
        #return jsonify(result_response)
        return result_response

    except Exception as e:
        #print(f"Error log printing Error: {e}")
        HcnLogUtils.lgr.error('========= ERROR START===========')
        #err = json.dumps(traceback.format_exc())
        #HcnLogUtils.lgr.error(f"{err.replace(':', '-')}".replace('"', ""))
        #HcnLogUtils.lgr.error("GOT request.get_json()="+str(request.get_json()).replace(':','-').replace('"',"'"))
        # HcnLogUtils.lgr.error(str(e).replace('-',':').replace('"',"'"), exc_info=True)
        err = json.dumps(traceback.format_exc())
        HcnLogUtils.lgr.error(f"{err.replace(':', '-')}".replace('"', ""))
        HcnLogUtils.lgr.error('========= ERROR  END ===========')
        result_response = {"status": "FAIL", "result": None, "errorMessage": "tmp default error msg "}
        #return jsonify(result_response)
        return result_response


if __name__ == '__main__':
  os.system('echo "HCN Service is up and running"')
  serve(app, host="0.0.0.0", port=5002,  _quiet=True )
  #app.run(host='localhost', port=5002, threaded=False)
