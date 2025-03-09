from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from api import router
from utils.responses import json_response

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GoSEND Mobile API",
    version="1.0.0",
    description="GoSEND Mobile API",
)

app.include_router(router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://192.168.1.7:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

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