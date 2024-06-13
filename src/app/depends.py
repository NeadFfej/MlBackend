from fastapi import  UploadFile
from fastapi.exceptions import HTTPException


def validate_csv(file: UploadFile):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Uploaded file must be a CSV file")
    
    return file.file.read()
