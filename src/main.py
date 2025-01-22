from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from api import router
from utils.responses import json_response

app = FastAPI(
    title="GoSEND Mobile API",
    version="1.0.0",
    description="GoSEND Mobile API",
)

app.include_router(router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    
    return json_response(
        message= str(exc.detail),
        status_code=exc.status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return json_response(
        message="Validaton error occured",
        data = {"errors": exc.errors()},
        status_code = 400
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}