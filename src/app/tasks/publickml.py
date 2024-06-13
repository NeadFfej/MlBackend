from celery_config.worker import celery



@celery.task()
def check_ml(text_request: str, model_data: dict):
    return (text_request, model_data)





