from fastapi import status

def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
   return {
        "status": "success",
        "message": message,
        "data": data
   }

def error_response(message="Error", code=status.HTTP_400_BAD_REQUEST, details=None):
    return {
        "status": "error",
        "message": message,
        "code": code,
        "details": details
    }
