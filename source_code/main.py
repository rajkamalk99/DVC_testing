# from org.hcn.tokenizer_utils.env_var_setter import set_os_env_var
import org.hcn.utils.env_var_setter
from org.hcn.utils.log_utils import HcnLogUtils

# set_os_env_var()
from org.hcn.core.CDoc import CDoc

from org.hcn.annotators.SectionDetection import Section_Detector
from org.hcn.annotators.SentenceDetection import Sentence_Detector
from org.hcn.annotators.TokenDetection import Token_Detector
from org.hcn.annotators.EntityDetection import Entity_Detector
from org.hcn.annotators.ChunkAndPosDetection import ChunkAndPosDetector
from org.hcn.utils.db_utils import HcnDbUtils

hcn_db_utils = HcnDbUtils()
hcn_db_utils.execute_query("SELECT * FROM PHI_DIA.entity_info;")

section_obj = Section_Detector()
sentence_obj = Sentence_Detector()
token_obj = Token_Detector()
entity_obj = Entity_Detector()
chunk_obj = ChunkAndPosDetector()


HcnLogUtils.lgr.debug('This is in Main script')
# hcn_db_utils.test()


def run(raw_text, task):
    # Later raw_text will setted by setter method of cdoc class
    cdoc = CDoc(raw_text)
    cdoc = section_obj.process(cdoc)
    #cdoc = token_obj.process(cdoc)
    if task == "SECTION_DETECTION":
        return cdoc

    cdoc = sentence_obj.process(cdoc)
    if task == "SENTENCE_DETECTION":
        return cdoc

    cdoc = token_obj.process(cdoc)
    if task == "TOKEN_DETECTION":
        for tok in cdoc.get_tokenDictList():
            HcnLogUtils.lgr.debug("Token begin= {}, end= {}, type= {}, covered text= {}".format(tok.begin, tok.end, tok.get_type(), tok.get_text_from_begin_end()))

        return cdoc
    if task == "CHUNK_DETECTION":
        cdoc = chunk_obj.process(cdoc)
        for chunk in cdoc.get_chunkDictList():
            HcnLogUtils.lgr.debug("Chunk begin= {}, end= {}, type= {}, covered text= {}".format(chunk.begin, chunk.end, chunk.get_type(), chunk.get_text_from_begin_end()))


    #cdoc = entity_obj.process(cdoc)
    if task == "ENTITY_DETECTION":
        return cdoc

    return cdoc


# raw_text = "he is good.he is nice\nhe can be better"
#raw_text = "patent has htn and fever. 99 @ he also has high blood pressure.\n he is also suffering from runny nose"
raw_text = "\nThe patient has hypertension.\n 99 @ he also has high blood pressure.\n"
cdoc_obj = run(raw_text, "TOKEN_DETECTION")

raw_text = "History of Present Illness: The patient is a 67-year-old Caucasian male, who was admitted from the surgical unit on 03/14/2019 because of bilateral foot wounds and need for IV antibiotics. On admission, he was found to have abnormal LFTs with an elevated alk phos, AST, and ALT. The patient denies history of significant alcohol use of liver disease. Denies any medications, nausea, vomiting, abdominal pain, abdominal distention, or ascites. He has a history of hypertension, diabetes."
#cdoc_obj = run(raw_text, "CHUNK_DETECTION")
# print(len(cdoc_obj.get_entityDictList()), "len(cdoc_obj.get_entityDictList())")
# for s in cdoc_obj.get_entityDictList():
#     print(raw_text[s.begin:s.end], s.__dict__)

