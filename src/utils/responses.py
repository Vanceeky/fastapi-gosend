from typing import Optional, Union
from fastapi.responses import JSONResponse
import datetime

def json_response(
        message: Optional[str] = None,
        data: Optional[Union[dict, list]] = None,
        status_code: int = 200
) -> JSONResponse:
    """
    Generates a JSON response with a standardized format for success or error.

    Args:
        message (Optional[str]): An optional message to include in the response. If not provided, 
                                  a default message will be used based on the status code.
        data (Optional[Union[dict, list]]): The data to be included in the response body, 
                                            typically a dictionary or a list.
        status_code (int): The HTTP status code to set for the response (default is 200).

    Returns:
        JSONResponse: The FastAPI JSON response object with the status, message, and data.
    """
    status = "success" if 200 <= status_code < 300 else "error"
    
    return JSONResponse({
        "status": status,
        "data": data,
        "message": message or ("Request was successful" if status == "success" else "An error occurred")
    }, status_code=status_code)



def datetime_to_str(dt: datetime) -> str:
    """
    Converts a datetime object to a string in the format "%Y-%m-%d %H:%M:%S".

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        str: The formatted string representation of the datetime.
    """
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)