from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse, PlainTextResponse
import logging
import random
import time
import string

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI()

import ner2_api

@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    
    return response

@app.get('/')
def index_route():
    return JSONResponse({'message': 'Index Route'})

@app.get('/health')
def health():
    return PlainTextResponse("200")



@app.post('/predict_ner_str')
async def predict_ner_str(d_content: dict = Body()):
    #print(d_content)
    result = ner2_api.predict_str(d_content)
    return JSONResponse(result)
    #return JSONResponse({})

