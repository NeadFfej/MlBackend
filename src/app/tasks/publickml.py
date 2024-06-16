import time
import json
import requests
from pathlib import Path

import spacy 

from celery_config.worker import celery
from core.configuration import settings


file_path = Path(__file__).resolve()
models_path = file_path.parents[3] / "mldata"


@celery.task()
def check_ml(session: str, text_requests: list[str], model_data: dict):
    result_data = []
    nlp = spacy.load(models_path / model_data["name"])
    
    for batch_request in text_requests:
        words = batch_request.split(" ")
        doc = nlp(batch_request)
        
        batch_response = ['O' for _ in range(len(words))]
        for ent in doc.ents:
            batch_response[ent.start] = ent.label_
        
        result_data.append(batch_response)
        
        params = {
            "user_id": session,
            "event": "newdata",
        }
        json_ = {
            "batch_request": batch_request,
            "batch_response": batch_response,
        }

        url = f"http://{settings.DOMAIN}:8000/system/sse/newevent"
        r = requests.post(url, params=params, json=json.dumps(json_))
        
        code_prefix = r.status_code // 100
        if code_prefix != 2 and r.status_code != 404:
            print(r.json())
        
    return {"request": text_requests, "response": result_data, "model_data": model_data}
