from fastapi import status, Depends, UploadFile
from fastapi.security import APIKeyCookie
from fastapi.exceptions import HTTPException

from core.security.tokens import verify_jwt_token


def validate_csv(file: UploadFile):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Uploaded file must be a CSV file")
    
    return file.file.read()


access_token_scheme = APIKeyCookie(
    name="access",
    scheme_name="Cookie access token",
    description="Cookie access token",
    auto_error=False,
)


def get_session_validator(need_validator_raise: bool = False, ):
    async def validator(
        token: str = Depends(access_token_scheme),
    ):
        token_data = verify_jwt_token(token=token)
        
        if (not token_data) and need_validator_raise:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
        return token_data

    return validator

