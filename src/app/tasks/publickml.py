from celery_config.worker import celery

import time 


@celery.task()
def check_ml(text_request: str, model_data: dict):
    for i in range(10):
        celery.send_task('app.tasks.publickml.process_partial_result', args=(i, ))
        time.sleep(1)
    return (text_request, model_data)


# Тестовый вариант внутреннего вызова задач
@celery.task
def process_partial_result(result):
    print(f"Received partial result: {result}")


