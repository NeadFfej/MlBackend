import time
import json
import requests

from celery_config.worker import celery
from core.configuration import settings


@celery.task()
def check_ml(session: str, text_request: str, model_data: dict):
    result_data = []
    for _ in range(10):
        batch_request = text_request # => _
        # TODO Обработка 
        
        # А-ля задержка для обработки больших данных
        time.sleep(1)

        batch_response = "NaN"
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
        r = requests.post(url, params=params, json=json.dumps(json_, indent=4))
        
        code_prefix = r.status_code // 100
        if code_prefix != 2 and r.status_code != 404:
            print(r.json())
        
    return {"request": text_request, "response": result_data, "model_data": model_data}
